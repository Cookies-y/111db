from flask_restx import Namespace, Resource, fields
from http import HTTPStatus
from flask_jwt_extended import jwt_required, get_jwt_identity
from . import db
from .models import User, Course, Discussion, Enrollment # Ensure all are imported
from sqlalchemy.orm import joinedload # For eager loading replies

# --- Namespace Definitions ---
course_discussions_ns = Namespace(
    name='course_discussions',
    description='Discussions within a specific course (list topics, create new topic)',
    path='/courses/<int:course_id>/discussions'
)

discussion_ops_ns = Namespace(
    name='discussion_operations',
    description='Operations on specific discussion posts/threads (get thread, post reply)',
    path='/discussions'
)

# --- Data Transfer Objects (DTOs) / Marshalling Models ---

# Simplified Author Model (reused)
author_simple_model = discussion_ops_ns.model('AuthorSimpleOutput', {
    'user_id': fields.Integer(readonly=True, description="Author's User ID"),
    'username': fields.String(description="Author's username"),
    'real_name': fields.String(description="Author's real name")
})

# Input model for creating new discussion topics or replies
discussion_post_input_model = discussion_ops_ns.model('DiscussionPostInput', {
    'title': fields.String(required=False, description='Title for a new topic (ignored for replies)', min_length=3, max_length=100),
    'content': fields.String(required=True, description='Content of the post/reply', min_length=1),
    # parent_id is part of the URL for replies, not in body for that case.
    # For creating a new topic, parent_id is implicitly None.
})

# Base fields for discussion post output
discussion_post_base_fields = {
    'post_id': fields.Integer(readonly=True),
    'course_id': fields.Integer(readonly=True), # Added readonly as it's set by context
    'author': fields.Nested(author_simple_model, attribute='author'), # Assumes 'author' relationship on Discussion model
    'title': fields.String(nullable=True),
    'content': fields.String(),
    'post_time': fields.DateTime(dt_format='iso8601', readonly=True),
    'parent_id': fields.Integer(nullable=True, readonly=True),
    'reply_count': fields.Integer(description="Number of direct replies", readonly=True) # Will be populated in code
}

# Output model for a single discussion post (topic or reply, without its own replies nested)
discussion_post_output_model = course_discussions_ns.model('DiscussionPostOutput', discussion_post_base_fields)
# Also define under discussion_ops_ns if used there for consistency
discussion_ops_post_output_model = discussion_ops_ns.model('DiscussionPostOutput', discussion_post_base_fields)


# Output model for a full discussion thread (a topic with its replies nested)
# Note: The 'self' for replies will use discussion_ops_ns's definition if not careful.
# It's often better to define the recursive part within the same namespace or be explicit.
# For simplicity, we assume Flask-RESTx can handle it or replies are marshalled manually for nesting.
# Let's define a simple recursive model structure within discussion_ops_ns.
nested_reply_model = discussion_ops_ns.model('NestedReply', discussion_post_base_fields) # Replies won't have further replies in this simple model

discussion_thread_output_model = discussion_ops_ns.model('DiscussionThreadOutput', {
    **discussion_post_base_fields,
    'replies': fields.List(fields.Nested(nested_reply_model), description="List of direct replies to this post")
})


# === Resources for /courses/<int:course_id>/discussions ===
@course_discussions_ns.route('/')
@course_discussions_ns.param('course_id', 'The course identifier')
class CourseDiscussionList(Resource):
    @course_discussions_ns.doc(description="List all top-level discussion topics for a course. Requires enrollment or being the course teacher.", security='jsonWebToken')
    @course_discussions_ns.marshal_list_with(discussion_post_output_model)
    @jwt_required()
    def get(self, course_id):
        """List all top-level discussion topics for a course."""
        current_user_id = get_jwt_identity()
        user = User.query.get_or_404(current_user_id)
        course = Course.query.get_or_404(course_id)

        is_teacher = (course.teacher_id == user.user_id)
        is_enrolled = False
        if not is_teacher and user.user_type == 1: # Student
            is_enrolled = Enrollment.query.filter_by(course_id=course_id, student_id=user.user_id).first() is not None

        if not is_teacher and not is_enrolled:
            return {'message': 'You are not authorized to view discussions for this course.'}, HTTPStatus.FORBIDDEN

        topics = Discussion.query.filter_by(course_id=course_id, parent_id=None).order_by(Discussion.post_time.desc()).all()

        # Populate reply_count for each topic
        for topic in topics:
            topic.reply_count = Discussion.query.filter_by(parent_id=topic.post_id).count()
            # Alternative if using lazy='dynamic' on topic.replies: topic.reply_count = topic.replies.count()

        return topics, HTTPStatus.OK

    @course_discussions_ns.doc(description="Create a new discussion topic in a course. Requires enrollment or being the course teacher.", security='jsonWebToken')
    @course_discussions_ns.expect(discussion_post_input_model, validate=True) # Title is optional in model, but required here
    @course_discussions_ns.marshal_with(discussion_post_output_model, code=HTTPStatus.CREATED)
    @jwt_required()
    def post(self, course_id):
        """Create a new discussion topic in a course."""
        current_user_id = get_jwt_identity()
        user = User.query.get_or_404(current_user_id)
        course = Course.query.get_or_404(course_id)

        is_teacher = (course.teacher_id == user.user_id)
        is_enrolled = False
        if not is_teacher and user.user_type == 1: # Student
            is_enrolled = Enrollment.query.filter_by(course_id=course_id, student_id=user.user_id).first() is not None

        if not is_teacher and not is_enrolled:
            return {'message': 'You are not authorized to post discussions in this course.'}, HTTPStatus.FORBIDDEN

        data = course_discussions_ns.payload
        title = data.get('title')
        content = data['content']

        if not title: # Title is required for new topics
            return {'message': 'Title is required for a new discussion topic.'}, HTTPStatus.BAD_REQUEST

        new_topic = Discussion(
            course_id=course_id,
            user_id=current_user_id,
            title=title,
            content=content,
            parent_id=None
        )
        db.session.add(new_topic)
        db.session.commit()
        new_topic.reply_count = 0 # New topics have 0 replies initially
        return new_topic, HTTPStatus.CREATED

# === Resources for /discussions/... ===
@discussion_ops_ns.route('/<int:post_id>/thread')
@discussion_ops_ns.param('post_id', 'The ID of the top-level discussion post (topic)')
class DiscussionThread(Resource):
    @discussion_ops_ns.doc(description="Get a specific discussion topic with all its direct replies. Requires enrollment or being the course teacher.", security='jsonWebToken')
    @discussion_ops_ns.marshal_with(discussion_thread_output_model)
    @jwt_required()
    def get(self, post_id):
        """Get a specific discussion topic with all its direct replies."""
        current_user_id = get_jwt_identity()
        user = User.query.get_or_404(current_user_id)

        # Eager load replies along with the parent post
        # options(joinedload(Discussion.replies)) might be too simple for multi-level, but good for direct replies.
        # The model relationship Discussion.replies should be set up for this.
        topic = Discussion.query.options(joinedload(Discussion.replies)).filter_by(post_id=post_id).first_or_404()

        if topic.parent_id is not None: # Ensure it's a top-level post
            return {'message': 'Requested post is a reply, not a top-level topic.'}, HTTPStatus.BAD_REQUEST

        course = Course.query.get_or_404(topic.course_id)
        is_teacher = (course.teacher_id == user.user_id)
        is_enrolled = False
        if not is_teacher and user.user_type == 1: # Student
            is_enrolled = Enrollment.query.filter_by(course_id=topic.course_id, student_id=user.user_id).first() is not None

        if not is_teacher and not is_enrolled:
            return {'message': 'You are not authorized to view this discussion thread.'}, HTTPStatus.FORBIDDEN

        # Populate reply_count for the main topic and its replies
        topic.reply_count = Discussion.query.filter_by(parent_id=topic.post_id).count()
        for reply in topic.replies:
            reply.reply_count = Discussion.query.filter_by(parent_id=reply.post_id).count() # Replies to replies (level 2)

        return topic, HTTPStatus.OK

@discussion_ops_ns.route('/<int:parent_post_id>/replies')
@discussion_ops_ns.param('parent_post_id', 'The ID of the post to reply to')
class DiscussionReply(Resource):
    @discussion_ops_ns.doc(description="Post a reply to a specific discussion post. Requires enrollment or being the course teacher.", security='jsonWebToken')
    @discussion_ops_ns.expect(discussion_post_input_model, validate=True) # title is ignored for replies
    @discussion_ops_ns.marshal_with(discussion_ops_post_output_model, code=HTTPStatus.CREATED) # Use the simpler post output model
    @jwt_required()
    def post(self, parent_post_id):
        """Post a reply to a specific discussion post."""
        current_user_id = get_jwt_identity()
        user = User.query.get_or_404(current_user_id)
        parent_post = Discussion.query.get_or_404(parent_post_id)
        course = Course.query.get_or_404(parent_post.course_id)

        is_teacher = (course.teacher_id == user.user_id)
        is_enrolled = False
        if not is_teacher and user.user_type == 1: # Student
            is_enrolled = Enrollment.query.filter_by(course_id=parent_post.course_id, student_id=user.user_id).first() is not None

        if not is_teacher and not is_enrolled:
            return {'message': 'You are not authorized to reply in this discussion.'}, HTTPStatus.FORBIDDEN

        data = discussion_ops_ns.payload
        content = data['content']
        # Title is not used for replies, or could be derived e.g., "Re: parent_post.title"

        new_reply = Discussion(
            course_id=parent_post.course_id,
            user_id=current_user_id,
            title=f"Re: {parent_post.title}" if parent_post.title else "Re: Post " + str(parent_post.post_id), # Example title for reply
            content=content,
            parent_id=parent_post_id
        )
        db.session.add(new_reply)
        db.session.commit()
        new_reply.reply_count = 0 # New replies have 0 replies initially
        return new_reply, HTTPStatus.CREATED

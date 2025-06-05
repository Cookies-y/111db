from flask_restx import Namespace, Resource, fields
from http import HTTPStatus
from flask_jwt_extended import jwt_required, get_jwt_identity
from . import db
from .models import User, Course, Assignment, Enrollment, Submission # Ensure Submission is imported
from datetime import datetime

# --- Namespace Definitions ---
course_assignments_ns = Namespace(
    name='course_assignments',
    description='Assignments for a specific course (create, list for course)',
    path='/courses/<int:course_id>/assignments'
)

assignment_ops_ns = Namespace(
    name='assignment_operations',
    description='Operations on a specific assignment by its ID (get details, submit, list submissions)',
    path='/assignments'
)

submission_ops_ns = Namespace(
    name='submission_operations',
    description='Operations on a specific submission by its ID (get details, grade)',
    path='/submissions'
)


# --- Data Transfer Objects (DTOs) / Marshalling Models ---

# Assignment Models (existing, slightly renamed for clarity if needed)
assignment_model_fields_def = {
    'assignment_id': fields.Integer(readonly=True, description='Unique identifier of the assignment'),
    'course_id': fields.Integer(readonly=True, description='ID of the course this assignment belongs to'),
    'title': fields.String(required=True, description='Title of the assignment', min_length=3, max_length=100),
    'description': fields.String(required=False, description='Detailed description of the assignment'),
    'deadline': fields.DateTime(required=True, description='Submission deadline (ISO 8601 format)', dt_format='iso8601'),
    'total_score': fields.Integer(required=False, description='Total possible score for the assignment', default=100, min=0),
    'create_time': fields.DateTime(readonly=True, description='Time the assignment was created (ISO 8601 format)')
}
assignment_input_model = course_assignments_ns.model('AssignmentCreationInput', {
    'title': assignment_model_fields_def['title'],
    'description': assignment_model_fields_def['description'],
    'deadline': assignment_model_fields_def['deadline'],
    'total_score': assignment_model_fields_def['total_score']
})
assignment_output_model = course_assignments_ns.model('AssignmentOutput', assignment_model_fields_def)
# This model can be used by assignment_ops_ns as well for consistency
assignment_detail_output_model = assignment_ops_ns.model('AssignmentDetailOutput', assignment_model_fields_def)


# Submission Models
submission_input_model = assignment_ops_ns.model('SubmissionInput', {
    'content': fields.String(required=True, description='Content of the submission'),
    'attachment_url': fields.String(required=False, description='URL to an attachment for the submission', nullable=True)
})

student_simple_model = assignment_ops_ns.model('StudentSimpleOutput', { # Can be defined once and reused
    'user_id': fields.Integer(readonly=True, description="Student's User ID"),
    'username': fields.String(description="Student's username"),
    'real_name': fields.String(description="Student's real name")
})

submission_output_model_def = {
    'submission_id': fields.Integer(readonly=True),
    'assignment_id': fields.Integer(),
    'student': fields.Nested(student_simple_model, attribute='student'), # Assumes 'student' relationship on Submission model
    'content': fields.String(),
    'attachment_url': fields.String(nullable=True, attribute='attachment'), # Model field is 'attachment'
    'submit_time': fields.DateTime(dt_format='iso8601'),
    'score': fields.Integer(nullable=True),
    'feedback': fields.String(nullable=True)
}
# Define for each namespace that uses it to avoid conflicts if schemas diverge later.
submission_list_output_model = assignment_ops_ns.model('SubmissionListOutput', submission_output_model_def)
submission_detail_output_model = submission_ops_ns.model('SubmissionDetailOutput', submission_output_model_def)


grade_input_model = submission_ops_ns.model('GradeInput', {
    'score': fields.Integer(required=True, min=0, description='Score awarded for the submission'),
    'feedback': fields.String(required=False, description='Feedback provided by the teacher', nullable=True)
})


# === Resources for Course-Specific Assignment Operations ===
@course_assignments_ns.route('/')
@course_assignments_ns.param('course_id', 'The course identifier')
class CourseAssignmentList(Resource):
    @course_assignments_ns.doc(description="List all assignments for a specific course. Requires enrollment or being the course teacher.", security='jsonWebToken')
    @course_assignments_ns.marshal_list_with(assignment_output_model)
    @jwt_required()
    def get(self, course_id):
        current_user_id = get_jwt_identity()
        user = User.query.get_or_404(current_user_id)
        course = Course.query.get_or_404(course_id)
        is_teacher = (course.teacher_id == user.user_id)
        is_enrolled = False
        if not is_teacher and user.user_type == 1:
            is_enrolled = Enrollment.query.filter_by(course_id=course_id, student_id=user.user_id).first() is not None
        if not is_teacher and not is_enrolled:
            return {'message': 'You are not authorized to view assignments for this course.'}, HTTPStatus.FORBIDDEN
        assignments = Assignment.query.filter_by(course_id=course_id).order_by(Assignment.deadline.asc()).all()
        return assignments, HTTPStatus.OK

    @course_assignments_ns.doc(description="Create a new assignment for a course. Requires being the course teacher.", security='jsonWebToken')
    @course_assignments_ns.expect(assignment_input_model, validate=True)
    @course_assignments_ns.marshal_with(assignment_output_model, code=HTTPStatus.CREATED)
    @jwt_required()
    def post(self, course_id):
        current_user_id = get_jwt_identity()
        user = User.query.get_or_404(current_user_id)
        course = Course.query.get_or_404(course_id)
        if course.teacher_id != user.user_id or user.user_type != 2:
            return {'message': 'Only the teacher of this course can create assignments.'}, HTTPStatus.FORBIDDEN
        data = course_assignments_ns.payload
        new_assignment = Assignment(
            course_id=course_id, title=data['title'], description=data.get('description'),
            deadline=data['deadline'], total_score=data.get('total_score', 100)
        )
        db.session.add(new_assignment)
        db.session.commit()
        return new_assignment, HTTPStatus.CREATED

# === Resources for Operations on a Specific Assignment (by assignment_id) ===
@assignment_ops_ns.route('/<int:assignment_id>')
@assignment_ops_ns.param('assignment_id', 'The assignment identifier')
class AssignmentDetailResource(Resource): # Renamed from AssignmentDetail to avoid conflict
    @assignment_ops_ns.doc(description="Get details of a specific assignment. Requires enrollment or being the course teacher.", security='jsonWebToken')
    @assignment_ops_ns.marshal_with(assignment_detail_output_model)
    @jwt_required()
    def get(self, assignment_id):
        current_user_id = get_jwt_identity()
        user = User.query.get_or_404(current_user_id)
        assignment = Assignment.query.get_or_404(assignment_id)
        course = Course.query.get_or_404(assignment.course_id)
        is_teacher = (course.teacher_id == user.user_id)
        is_enrolled = False
        if not is_teacher and user.user_type == 1:
            is_enrolled = Enrollment.query.filter_by(course_id=assignment.course_id, student_id=user.user_id).first() is not None
        if not is_teacher and not is_enrolled:
            return {'message': 'You are not authorized to view this assignment.'}, HTTPStatus.FORBIDDEN
        return assignment, HTTPStatus.OK

@assignment_ops_ns.route('/<int:assignment_id>/submissions')
@assignment_ops_ns.param('assignment_id', 'The assignment identifier')
class AssignmentSubmissionsResource(Resource):
    @assignment_ops_ns.doc(description="List submissions for an assignment (teacher view).", security='jsonWebToken')
    @assignment_ops_ns.marshal_list_with(submission_list_output_model)
    @jwt_required()
    def get(self, assignment_id):
        """List submissions for an assignment (Teacher View)."""
        current_user_id = get_jwt_identity()
        user = User.query.get_or_404(current_user_id)
        assignment = Assignment.query.get_or_404(assignment_id)
        course = Course.query.get_or_404(assignment.course_id)
        if not (course.teacher_id == user.user_id and user.user_type == 2):
            return {'message': 'Only the teacher of this course can view all submissions.'}, HTTPStatus.FORBIDDEN
        submissions = Submission.query.filter_by(assignment_id=assignment_id).order_by(Submission.submit_time.asc()).all()
        return submissions, HTTPStatus.OK

    @assignment_ops_ns.doc(description="Submit to an assignment (Student View).", security='jsonWebToken')
    @assignment_ops_ns.expect(submission_input_model, validate=True)
    @assignment_ops_ns.marshal_with(submission_list_output_model, code=HTTPStatus.CREATED) # Use submission_list_output_model as it has student info
    @jwt_required()
    def post(self, assignment_id):
        """Submit to an assignment (Student View)."""
        current_user_id = get_jwt_identity()
        user = User.query.get_or_404(current_user_id)
        if user.user_type != 1: # Must be a student
            return {'message': 'Only students can submit assignments.'}, HTTPStatus.FORBIDDEN

        assignment = Assignment.query.get_or_404(assignment_id)
        if datetime.utcnow() > assignment.deadline:
             return {'message': 'The deadline for this assignment has passed.'}, HTTPStatus.FORBIDDEN

        is_enrolled = Enrollment.query.filter_by(course_id=assignment.course_id, student_id=user.user_id).first()
        if not is_enrolled:
            return {'message': 'You are not enrolled in the course for this assignment.'}, HTTPStatus.FORBIDDEN

        existing_submission = Submission.query.filter_by(assignment_id=assignment_id, student_id=user.user_id).first()
        if existing_submission:
            return {'message': 'You have already submitted to this assignment.'}, HTTPStatus.CONFLICT

        data = assignment_ops_ns.payload
        new_submission = Submission(
            assignment_id=assignment_id,
            student_id=user.user_id,
            content=data['content'],
            attachment=data.get('attachment_url') # model field is 'attachment'
        )
        db.session.add(new_submission)
        db.session.commit()
        return new_submission, HTTPStatus.CREATED

# === Resources for Operations on a Specific Submission (by submission_id) ===
@submission_ops_ns.route('/<int:submission_id>')
@submission_ops_ns.param('submission_id', 'The submission identifier')
class SubmissionDetailResource(Resource):
    @submission_ops_ns.doc(description="Get details of a specific submission. Requires being the student who submitted or the course teacher.", security='jsonWebToken')
    @submission_ops_ns.marshal_with(submission_detail_output_model)
    @jwt_required()
    def get(self, submission_id):
        """Fetch details of a specific submission."""
        current_user_id = get_jwt_identity()
        user = User.query.get_or_404(current_user_id)
        submission = Submission.query.get_or_404(submission_id)
        assignment = Assignment.query.get_or_404(submission.assignment_id)
        course = Course.query.get_or_404(assignment.course_id)

        is_course_teacher = (course.teacher_id == user.user_id and user.user_type == 2)
        is_student_owner = (submission.student_id == user.user_id)

        if not is_course_teacher and not is_student_owner:
            return {'message': 'You are not authorized to view this submission.'}, HTTPStatus.FORBIDDEN
        return submission, HTTPStatus.OK

@submission_ops_ns.route('/<int:submission_id>/grade')
@submission_ops_ns.param('submission_id', 'The submission identifier')
class SubmissionGradeResource(Resource):
    @submission_ops_ns.doc(description="Grade a submission. Requires being the course teacher.", security='jsonWebToken')
    @submission_ops_ns.expect(grade_input_model, validate=True)
    @submission_ops_ns.marshal_with(submission_detail_output_model) # Return the updated submission
    @jwt_required()
    def put(self, submission_id):
        """Grade a submission (Teacher only)."""
        current_user_id = get_jwt_identity()
        user = User.query.get_or_404(current_user_id)
        submission = Submission.query.get_or_404(submission_id)
        assignment = Assignment.query.get_or_404(submission.assignment_id)
        course = Course.query.get_or_404(assignment.course_id)

        if not (course.teacher_id == user.user_id and user.user_type == 2):
            return {'message': 'Only the teacher of this course can grade submissions.'}, HTTPStatus.FORBIDDEN

        data = submission_ops_ns.payload

        # Validate score against assignment's total_score
        if data['score'] > assignment.total_score:
             return {'message': f"Score cannot exceed assignment's total score of {assignment.total_score}."}, HTTPStatus.BAD_REQUEST

        submission.score = data['score']
        submission.feedback = data.get('feedback')
        # Potentially update submission status if there's one
        db.session.commit()
        return submission, HTTPStatus.OK

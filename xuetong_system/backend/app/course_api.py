from flask_restx import Namespace, Resource, fields
from http import HTTPStatus
from flask_jwt_extended import jwt_required, get_jwt_identity
from . import db
from .models import User, Course, Chapter, Material # Make sure all necessary models are imported
from datetime import date # For date fields

course_ns = Namespace('courses', description='Course related operations')

# --- Data Transfer Objects (DTOs) / Marshalling Models ---

teacher_simple_model = course_ns.model('TeacherSimpleOutput', {
    'user_id': fields.Integer(readonly=True, description='Teacher User ID'),
    'real_name': fields.String(description='Teacher\'s real name'),
    'email': fields.String(description='Teacher\'s email')
})

material_model = course_ns.model('MaterialOutput', {
    'material_id': fields.Integer(readonly=True, description='Material ID'),
    'title': fields.String(required=True, description='Title of the material'),
    'material_type': fields.Integer(required=True, description='Type of material (1:Video, 2:Document, 3:Link)'),
    'url': fields.String(required=True, description='URL or path to the material content'),
    'duration': fields.Integer(nullable=True, description='Duration in seconds (for video)'),
    'upload_time': fields.DateTime(readonly=True, description='Time material was uploaded')
})

chapter_model = course_ns.model('ChapterOutput', {
    'chapter_id': fields.Integer(readonly=True, description='Chapter ID'),
    'chapter_name': fields.String(required=True, description='Name of the chapter'),
    'chapter_order': fields.Integer(required=True, description='Order of the chapter in the course'),
    'description': fields.String(nullable=True, description='Description of the chapter'),
    'materials': fields.List(fields.Nested(material_model), description='List of materials in this chapter')
})

course_list_item_model = course_ns.model('CourseListItemOutput', {
    'course_id': fields.Integer(readonly=True, description='Course ID'),
    'course_name': fields.String(required=True, description='Name of the course'),
    'description': fields.String(nullable=True, description='Brief description of the course'),
    'teacher': fields.Nested(teacher_simple_model, description='Teacher of the course', attribute='teacher'),
    'cover_image': fields.String(nullable=True, description='URL of the course cover image'),
    'status': fields.Integer(required=True, description='Status of the course (1:Not Started, 2:In Progress, 3:Ended)'),
    'create_time': fields.DateTime(readonly=True, description='Time course was created')
})

# For CourseDetail, we include fields from CourseListItem and add more
course_detail_model = course_ns.model('CourseDetailOutput', {
    'course_id': fields.Integer(readonly=True, description='Course ID'),
    'course_name': fields.String(required=True, description='Name of the course'),
    'description': fields.String(nullable=True, description='Brief description of the course'),
    'teacher': fields.Nested(teacher_simple_model, description='Teacher of the course', attribute='teacher'),
    'cover_image': fields.String(nullable=True, description='URL of the course cover image'),
    'status': fields.Integer(required=True, description='Status of the course (1:Not Started, 2:In Progress, 3:Ended)'),
    'create_time': fields.DateTime(readonly=True, description='Time course was created'),
    # Additional fields for detail view
    'start_date': fields.Date(required=True, description='Course start date'),
    'end_date': fields.Date(required=True, description='Course end date'),
    'chapters': fields.List(fields.Nested(chapter_model), description='List of chapters in the course')
})

course_creation_input_model = course_ns.model('CourseCreationInput', {
    'course_name': fields.String(required=True, min_length=3, max_length=100, description='Name of the course'),
    'description': fields.String(nullable=True, description='Detailed description of the course'),
    'start_date': fields.Date(required=True, description='Course start date (YYYY-MM-DD)'),
    'end_date': fields.Date(required=True, description='Course end date (YYYY-MM-DD)'),
    'status': fields.Integer(required=True, description='Status of the course (1:Not Started, 2:In Progress, 3:Ended)', enum=[1, 2, 3]),
    'cover_image': fields.String(nullable=True, description='URL of the course cover image')
})


# --- API Resources ---

@course_ns.route('/')
class CourseListCreate(Resource):
    @course_ns.marshal_list_with(course_list_item_model, description='List of available courses.')
    def get(self):
        """Lists all available courses."""
        courses = Course.query.order_by(Course.create_time.desc()).all()
        return courses, HTTPStatus.OK

    @jwt_required()
    @course_ns.expect(course_creation_input_model, validate=True)
    @course_ns.marshal_with(course_detail_model, code=HTTPStatus.CREATED, description='Course created successfully.')
    @course_ns.doc(security='jsonWebToken', description='Create a new course. Requires teacher role.')
    @course_ns.response(HTTPStatus.FORBIDDEN, 'Only teachers can create courses.')
    @course_ns.response(HTTPStatus.UNAUTHORIZED, 'Token is missing or invalid.')
    @course_ns.response(HTTPStatus.BAD_REQUEST, 'Input validation error.')
    def post(self):
        """Creates a new course. Only accessible by teachers."""
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)

        if not user or user.user_type != 2: # 2 for teacher
            return {'message': 'Only teachers can create courses.'}, HTTPStatus.FORBIDDEN

        data = course_ns.payload

        # Convert date strings from payload to date objects if necessary
        # Flask-RESTx Date field should handle this, but good to be aware
        start_date_obj = data['start_date'] # Directly use if conversion is handled
        end_date_obj = data['end_date']     # Directly use if conversion is handled

        if isinstance(start_date_obj, str)):
            start_date_obj = date.fromisoformat(start_date_obj)
        if isinstance(end_date_obj, str)):
            end_date_obj = date.fromisoformat(end_date_obj)

        if end_date_obj < start_date_obj:
            return {'message': 'End date cannot be before start date.'}, HTTPStatus.BAD_REQUEST

        new_course = Course(
            course_name=data['course_name'],
            description=data.get('description'),
            teacher_id=current_user_id,
            start_date=start_date_obj,
            end_date=end_date_obj,
            status=data['status'],
            cover_image=data.get('cover_image')
            # create_time is default
        )
        db.session.add(new_course)
        db.session.commit()
        return new_course, HTTPStatus.CREATED

@course_ns.route('/<int:course_id>')
@course_ns.param('course_id', 'The unique identifier of the course.')
class CourseResource(Resource):
    @course_ns.marshal_with(course_detail_model, description='Detailed information about the course.')
    @course_ns.response(HTTPStatus.NOT_FOUND, 'Course not found.')
    def get(self, course_id):
        """Fetches details of a specific course, including its chapters and materials."""
        # Using get_or_404 automatically handles the Not Found response
        course = Course.query.get_or_404(course_id, description=f"Course with ID {course_id} not found.")
        return course, HTTPStatus.OK

    # Placeholder for PUT (Update Course) - Requires @jwt_required() and teacher check
    # @jwt_required()
    # @course_ns.expect(course_creation_input_model, validate=True) # Can reuse or make a specific update model
    # @course_ns.marshal_with(course_detail_model)
    # @course_ns.doc(security='jsonWebToken')
    # def put(self, course_id):
    #     pass

    # Placeholder for DELETE (Delete Course) - Requires @jwt_required() and teacher/admin check
    # @jwt_required()
    # @course_ns.response(HTTPStatus.NO_CONTENT, 'Course deleted successfully.')
    # @course_ns.doc(security='jsonWebToken')
    # def delete(self, course_id):
    #     pass

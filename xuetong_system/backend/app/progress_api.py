from flask_restx import Namespace, Resource, fields
from http import HTTPStatus
from flask_jwt_extended import jwt_required, get_jwt_identity
from . import db
from .models import User, Course, Material, Chapter, Progress, Enrollment
from datetime import datetime

# --- Namespace Definitions ---
material_progress_ns = Namespace(
    name='material_progress',
    description='Manage progress on specific learning materials',
    path='/materials/<int:material_id>/progress'
)

course_progress_ns = Namespace(
    name='course_material_progress',
    description='View all material progress for a student within a specific course',
    path='/courses/<int:course_id>/my-material-progress'
)

# --- Data Transfer Objects (DTOs) / Marshalling Models ---
progress_status_input_model = material_progress_ns.model('ProgressStatusInput', {
    'is_completed': fields.Boolean(required=True, description='Mark as true if completed, false if un-marking (sets progress to 0 or 100).')
    # 'progress': fields.Integer(required=False, description='Specific progress percentage (0-100)', min=0, max=100)
    # For MVP, is_completed is simpler. Progress percentage can be added later.
})

material_progress_output_model_fields = {
    'material_id': fields.Integer(readonly=True, description="Material ID"),
    'material_title': fields.String(readonly=True, description="Title of the material"), # To be populated in resource
    'is_completed': fields.Boolean(description="Is the material marked as completed?"),
    'progress_percentage': fields.Integer(attribute='progress', description="Progress percentage (0-100)"),
    'last_learn_time': fields.DateTime(dt_format='iso8601', readonly=True, description="Last time progress was updated")
}
# Define for each namespace to avoid potential conflicts if they are registered with different Api objects or have slight variations later
material_progress_output_model = material_progress_ns.model('MaterialProgressOutput', material_progress_output_model_fields)
course_material_progress_output_model = course_progress_ns.model('CourseMaterialProgressOutput', material_progress_output_model_fields)


# === Resources for /materials/<int:material_id>/progress ===
@material_progress_ns.route('/')
@material_progress_ns.param('material_id', 'The material identifier')
class MaterialProgressResource(Resource):
    @material_progress_ns.doc(description="Get or update progress for a specific material for the current student.", security='jsonWebToken')
    @jwt_required()
    def _get_common_objects(self, material_id):
        """Helper to get user, material, course and check enrollment."""
        user_id = get_jwt_identity()
        user = User.query.get_or_404(user_id)
        if user.user_type != 1: # Must be a student
            material_progress_ns.abort(HTTPStatus.FORBIDDEN, 'Only students can track material progress.')

        material = Material.query.get_or_404(material_id)
        chapter = Chapter.query.get_or_404(material.chapter_id) # Material must belong to a chapter
        course = Course.query.get_or_404(chapter.course_id) # Chapter must belong to a course

        Enrollment.query.filter_by(student_id=user_id, course_id=course.course_id).first_or_404(
            description='You are not enrolled in the course containing this material.'
        )
        return user, material, course

    @material_progress_ns.marshal_with(material_progress_output_model)
    @material_progress_ns.response(HTTPStatus.NOT_FOUND, 'Material or progress record not found.')
    @material_progress_ns.response(HTTPStatus.FORBIDDEN, 'Not authorized or not enrolled.')
    def get(self, material_id):
        """Get progress for a specific material for the current student."""
        user, material, _ = self._get_common_objects(material_id)

        progress_record = Progress.query.filter_by(user_id=user.user_id, material_id=material.material_id).first()
        if not progress_record:
            # Return a default "not started" progress record representation
            return {
                'material_id': material.material_id,
                'material_title': material.title,
                'is_completed': False,
                'progress_percentage': 0,
                'last_learn_time': None # Or a default time if preferred
            }, HTTPStatus.OK # Or 404 if "no progress" means "not found" strictly

        progress_record.material_title = material.title # Add title for marshalling
        return progress_record, HTTPStatus.OK

    @material_progress_ns.expect(progress_status_input_model, validate=True)
    @material_progress_ns.marshal_with(material_progress_output_model) # Responds with the updated/created progress
    @material_progress_ns.response(HTTPStatus.CREATED, 'Progress record created/updated.') # Can be OK too
    @material_progress_ns.response(HTTPStatus.NOT_FOUND, 'Material not found.')
    @material_progress_ns.response(HTTPStatus.FORBIDDEN, 'Not authorized or not enrolled.')
    def post(self, material_id):
        """Mark a material as completed or not completed for the current student."""
        user, material, _ = self._get_common_objects(material_id)
        args = material_progress_ns.payload
        is_completed = args['is_completed']

        progress_record = Progress.query.filter_by(user_id=user.user_id, material_id=material.material_id).first()
        status_code = HTTPStatus.OK

        if not progress_record:
            progress_record = Progress(user_id=user.user_id, material_id=material.material_id)
            db.session.add(progress_record)
            status_code = HTTPStatus.CREATED # Indicate resource creation

        progress_record.is_completed = is_completed
        progress_record.progress = 100 if is_completed else 0 # Simplified: 100% if completed, 0% otherwise
        progress_record.last_learn_time = datetime.utcnow()

        db.session.commit()

        progress_record.material_title = material.title # Add title for marshalling
        return progress_record, status_code


# === Resources for /courses/<int:course_id>/my-material-progress ===
@course_progress_ns.route('/')
@course_progress_ns.param('course_id', 'The course identifier')
class CourseMaterialProgressList(Resource):
    @course_progress_ns.doc(description="Get all material progress for the current student in a specific course.", security='jsonWebToken')
    @course_progress_ns.marshal_list_with(course_material_progress_output_model)
    @course_progress_ns.response(HTTPStatus.NOT_FOUND, 'Course not found.')
    @course_progress_ns.response(HTTPStatus.FORBIDDEN, 'Not authorized or not enrolled.')
    @jwt_required()
    def get(self, course_id):
        """Get all material progress for the current student in a specific course."""
        user_id = get_jwt_identity()
        user = User.query.get_or_404(user_id)

        if user.user_type != 1: # Must be a student
            course_progress_ns.abort(HTTPStatus.FORBIDDEN, 'Only students can view their material progress.')

        # Check course exists and student is enrolled
        Course.query.get_or_404(course_id)
        Enrollment.query.filter_by(student_id=user_id, course_id=course_id).first_or_404(
            description='You are not enrolled in this course.'
        )

        # Fetch all materials for the course
        materials_in_course = Material.query.join(Chapter).filter(Chapter.course_id == course_id).all()

        results = []
        for material in materials_in_course:
            progress_record = Progress.query.filter_by(user_id=user_id, material_id=material.material_id).first()
            results.append({
                'material_id': material.material_id,
                'material_title': material.title,
                'is_completed': progress_record.is_completed if progress_record else False,
                'progress': progress_record.progress if progress_record else 0, # Field name for marshaller
                'last_learn_time': progress_record.last_learn_time if progress_record else None
            })

        return results, HTTPStatus.OK

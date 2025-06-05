from flask_restx import Namespace, Resource, fields
from http import HTTPStatus
from flask_jwt_extended import jwt_required, get_jwt_identity
from . import db
from .models import User, Course, Exam, ExamResult, Enrollment # Ensure all are imported
from datetime import datetime

# --- Namespace Definitions ---
course_exams_ns = Namespace(
    name='course_exams',
    description='Manage exams for a specific course (list, create)',
    path='/courses/<int:course_id>/exams'
)

exam_ops_ns = Namespace(
    name='exam_operations',
    description='Operations on a specific exam (get details, submit, view results)',
    path='/exams/<int:exam_id>'
)

exam_result_ops_ns = Namespace(
    name='exam_result_operations',
    description='Manage individual exam results (e.g., update by teacher)',
    path='/exam-results' # Specific result operations by result_id
)


# --- Reusable DTOs / Marshalling Models ---
student_simple_model = exam_ops_ns.model('StudentSimpleOutput', { # Defined under exam_ops_ns but can be used by others
    'user_id': fields.Integer(readonly=True, description="Student's User ID"),
    'username': fields.String(description="Student's username"),
    'real_name': fields.String(description="Student's real name")
})

# --- Exam DTOs ---
exam_fields = {
    'exam_id': fields.Integer(readonly=True, description='Unique identifier of the exam'),
    'course_id': fields.Integer(readonly=True, description='ID of the course this exam belongs to'),
    'exam_name': fields.String(required=True, description='Name of the exam', min_length=3, max_length=100),
    'description': fields.String(required=False, description='Detailed description of the exam', nullable=True),
    'start_time': fields.DateTime(required=True, description='Exam start time (ISO 8601 format)', dt_format='iso8601'),
    'end_time': fields.DateTime(required=True, description='Exam end time (ISO 8601 format)', dt_format='iso8601'),
    'total_score': fields.Integer(required=True, description='Total possible score', default=100, min=0),
    'duration': fields.Integer(required=True, description='Exam duration in minutes', min=1) # Duration in minutes
}
exam_input_model = course_exams_ns.model('ExamCreationInput', {
    'exam_name': exam_fields['exam_name'],
    'description': exam_fields['description'],
    'start_time': exam_fields['start_time'],
    'end_time': exam_fields['end_time'],
    'total_score': exam_fields['total_score'],
    'duration': exam_fields['duration']
})
exam_output_model = course_exams_ns.model('ExamOutput', exam_fields) # Also used by exam_ops_ns

# --- Exam Result DTOs ---
exam_result_fields = {
    'result_id': fields.Integer(readonly=True),
    'exam_id': fields.Integer(),
    'student': fields.Nested(student_simple_model, attribute='student'), # Assumes 'student' relationship
    'score': fields.Integer(required=True, description='Score obtained by the student'), # Required for submission
    'submit_time': fields.DateTime(readonly=True, dt_format='iso8601'),
    'status': fields.Integer(readonly=True, description='Status of the exam attempt (e.g., 3=Completed)') # Usually set by system
}
exam_result_output_model = exam_ops_ns.model('ExamResultOutput', exam_result_fields)

# For student submitting their score (simplified MVP)
exam_result_submission_input_model = exam_ops_ns.model('ExamResultSubmissionInput', {
    'score': fields.Integer(required=True, description='Score achieved by the student', min=0)
})

# For teacher updating/overriding a result
exam_result_update_input_model = exam_result_ops_ns.model('ExamResultUpdateInput', {
    'score': fields.Integer(required=True, description='Updated score', min=0),
    # 'status': fields.Integer(description='Updated status', enum=[1,2,3]) # Optional
})

# Extended Exam Detail model for teachers (includes all results)
exam_detail_for_teacher_model = exam_ops_ns.model('ExamDetailForTeacherOutput', {
    **exam_fields, # Inherit all fields from exam_fields
    'results': fields.List(fields.Nested(exam_result_output_model), description='List of all student results for this exam')
})


# === Resources for /courses/<int:course_id>/exams ===
@course_exams_ns.route('/')
@course_exams_ns.param('course_id', 'The course identifier')
class CourseExamList(Resource):
    @course_exams_ns.doc(description="List all exams for a course. Requires enrollment or being the course teacher.", security='jsonWebToken')
    @course_exams_ns.marshal_list_with(exam_output_model)
    @jwt_required()
    def get(self, course_id):
        """List all exams for a specific course."""
        current_user_id = get_jwt_identity()
        user = User.query.get_or_404(current_user_id)
        course = Course.query.get_or_404(course_id)

        is_teacher = (course.teacher_id == user.user_id)
        is_enrolled = False
        if not is_teacher and user.user_type == 1: # Student
            is_enrolled = Enrollment.query.filter_by(course_id=course_id, student_id=user.user_id).first() is not None

        if not is_teacher and not is_enrolled:
            return {'message': 'You are not authorized to view exams for this course.'}, HTTPStatus.FORBIDDEN

        exams = Exam.query.filter_by(course_id=course_id).order_by(Exam.start_time.asc()).all()
        return exams, HTTPStatus.OK

    @course_exams_ns.doc(description="Create a new exam for a course. Requires being the course teacher.", security='jsonWebToken')
    @course_exams_ns.expect(exam_input_model, validate=True)
    @course_exams_ns.marshal_with(exam_output_model, code=HTTPStatus.CREATED)
    @jwt_required()
    def post(self, course_id):
        """Create a new exam for a course (Teacher only)."""
        current_user_id = get_jwt_identity()
        user = User.query.get_or_404(current_user_id)
        course = Course.query.get_or_404(course_id)

        if not (course.teacher_id == user.user_id and user.user_type == 2):
            return {'message': 'Only the teacher of this course can create exams.'}, HTTPStatus.FORBIDDEN

        data = course_exams_ns.payload
        if data['end_time'] <= data['start_time']:
            return {'message': 'Exam end time must be after start time.'}, HTTPStatus.BAD_REQUEST

        new_exam = Exam(
            course_id=course_id,
            exam_name=data['exam_name'],
            description=data.get('description'),
            start_time=data['start_time'],
            end_time=data['end_time'],
            total_score=data.get('total_score', 100),
            duration=data['duration']
        )
        db.session.add(new_exam)
        db.session.commit()
        return new_exam, HTTPStatus.CREATED

# === Resources for /exams/<int:exam_id> ===
@exam_ops_ns.route('/') # Path is relative to namespace: /exams/<int:exam_id>/
@exam_ops_ns.param('exam_id', 'The exam identifier')
class ExamDetail(Resource):
    @exam_ops_ns.doc(description="Get details of an exam. Teacher sees all results, student sees exam info and their own result if submitted.", security='jsonWebToken')
    # Conditional marshalling is tricky. We'll marshal with teacher model and filter if student.
    # Or, better, define two different GET methods or handle marshalling in code.
    # For simplicity now, let's always return the teacher model and let frontend adapt, or use a generic model.
    # A more advanced solution uses multiple @marshal_with based on condition or custom marshalling.
    # Let's use exam_output_model for students and exam_detail_for_teacher_model for teachers.
    # Flask-RESTx doesn't directly support conditional @marshal_with on a single method easily.
    # So, the method will decide what data to return, and we'll use a more general output model or just return dict.
    # For now, let's return the detailed model and note that frontend for student should not display all results.
    @exam_ops_ns.marshal_with(exam_detail_for_teacher_model)
    @jwt_required()
    def get(self, exam_id):
        """Fetch details of a specific exam."""
        current_user_id = get_jwt_identity()
        user = User.query.get_or_404(current_user_id)
        exam = Exam.query.get_or_404(exam_id)
        course = Course.query.get_or_404(exam.course_id)

        is_teacher = (course.teacher_id == user.user_id and user.user_type == 2)
        is_enrolled = False
        if not is_teacher and user.user_type == 1: # Student
            is_enrolled = Enrollment.query.filter_by(course_id=exam.course_id, student_id=user.user_id).first() is not None

        if not is_teacher and not is_enrolled:
            return {'message': 'You are not authorized to view this exam.'}, HTTPStatus.FORBIDDEN

        if is_teacher:
            # Teacher gets all results, which are part of Exam model's 'results' relationship
            return exam, HTTPStatus.OK
        else: # Student
            # Student sees exam details, and we can add their specific result if available
            # The `exam_detail_for_teacher_model` includes 'results', which will be an empty list for student if not filtered.
            # A better approach: student only sees their own result, or no results if this model is used.
            # For now, student will get the exam details, and the 'results' field will be whatever the relationship loads.
            # Let's filter results for students:
            exam_data = {**exam.__dict__} # shallow copy
            exam_data.pop('_sa_instance_state', None) # remove SQLAlchemy state

            my_result = ExamResult.query.filter_by(exam_id=exam.exam_id, student_id=user.user_id).first()
            exam_data['my_result'] = my_result # Add student's own result
            exam_data['results'] = [my_result] if my_result else [] # Overwrite 'results' to only include their own

            # To use exam_detail_for_teacher_model correctly, we need to ensure the structure matches.
            # This dynamic dict creation might not work perfectly with marshal_with.
            # A simpler approach for now: return the exam object, and frontend for student only displays their result.
            # The `exam_detail_for_teacher_model` will try to marshal `exam.results`.
            # If student, `exam.results` will be all results. This is a data exposure issue for students.
            # Correct approach: Use different models or filter data before returning for students.

            # Simplification for this step: Student gets exam details only, no results via this endpoint directly.
            # They would use a separate "my results" endpoint or this endpoint is modified.
            # For now, let's use the simpler exam_output_model for students.
            if not is_teacher:
                 # Re-marshal with a simpler model for students if we don't want them to see all results
                 # This is tricky with decorators. For now, teacher gets full detail.
                 # Student will also get full detail including all results, which is not ideal.
                 # This needs refinement in a real scenario.
                 # A quick fix:
                 student_exam_view = exam_ops_ns.marshal(exam, exam_output_model) # Marshal manually
                 student_exam_view['my_result'] = exam_ops_ns.marshal(my_result, exam_result_output_model) if my_result else None
                 return student_exam_view, HTTPStatus.OK

            return exam, HTTPStatus.OK # Teacher gets exam with all results via relationship


@exam_ops_ns.route('/submit')
@exam_ops_ns.param('exam_id', 'The exam identifier')
class ExamSubmission(Resource):
    @exam_ops_ns.doc(description="Submit results for an exam (Student only).", security='jsonWebToken')
    @exam_ops_ns.expect(exam_result_submission_input_model, validate=True)
    @exam_ops_ns.marshal_with(exam_result_output_model, code=HTTPStatus.CREATED)
    @jwt_required()
    def post(self, exam_id):
        """Submit an exam result (Student only)."""
        current_user_id = get_jwt_identity()
        user = User.query.get_or_404(current_user_id)
        exam = Exam.query.get_or_404(exam_id)

        if user.user_type != 1: # Must be a student
            return {'message': 'Only students can submit exam results.'}, HTTPStatus.FORBIDDEN

        is_enrolled = Enrollment.query.filter_by(course_id=exam.course_id, student_id=user.user_id).first()
        if not is_enrolled:
            return {'message': 'You are not enrolled in the course for this exam.'}, HTTPStatus.FORBIDDEN

        now = datetime.utcnow()
        if not (exam.start_time <= now <= exam.end_time):
            return {'message': 'Exam is not currently active or has ended.'}, HTTPStatus.FORBIDDEN

        existing_result = ExamResult.query.filter_by(exam_id=exam_id, student_id=user.user_id).first()
        if existing_result:
            return {'message': 'You have already submitted results for this exam.'}, HTTPStatus.CONFLICT

        data = exam_ops_ns.payload
        if data['score'] > exam.total_score:
            return {'message': f"Score cannot exceed exam's total score of {exam.total_score}."}, HTTPStatus.BAD_REQUEST

        new_result = ExamResult(
            exam_id=exam_id,
            student_id=user.user_id,
            score=data['score'],
            status=3 # Mark as Completed
            # submit_time is default
        )
        db.session.add(new_result)
        db.session.commit()
        return new_result, HTTPStatus.CREATED

@exam_ops_ns.route('/results')
@exam_ops_ns.param('exam_id', 'The exam identifier')
class ExamResultsList(Resource):
    @exam_ops_ns.doc(description="List all results for an exam (Teacher only).", security='jsonWebToken')
    @exam_ops_ns.marshal_list_with(exam_result_output_model)
    @jwt_required()
    def get(self, exam_id):
        """List all results for an exam (Teacher only)."""
        current_user_id = get_jwt_identity()
        user = User.query.get_or_404(current_user_id)
        exam = Exam.query.get_or_404(exam_id)
        course = Course.query.get_or_404(exam.course_id)

        if not (course.teacher_id == user.user_id and user.user_type == 2):
            return {'message': 'Only the teacher of this course can view exam results.'}, HTTPStatus.FORBIDDEN

        results = ExamResult.query.filter_by(exam_id=exam_id).order_by(ExamResult.submit_time.desc()).all()
        return results, HTTPStatus.OK


# === Resources for /exam-results/<int:result_id> ===
@exam_result_ops_ns.route('/<int:result_id>')
@exam_result_ops_ns.param('result_id', 'The exam result identifier')
class ExamResultDetail(Resource):
    @exam_result_ops_ns.doc(description="Get or update a specific exam result (Teacher only for update).", security='jsonWebToken')
    @exam_result_ops_ns.marshal_with(exam_result_output_model) # For GET
    @jwt_required()
    def get(self, result_id):
        """Fetch details of a specific exam result."""
        current_user_id = get_jwt_identity()
        user = User.query.get_or_404(current_user_id)
        result = ExamResult.query.get_or_404(result_id)
        exam = Exam.query.get_or_404(result.exam_id)
        course = Course.query.get_or_404(exam.course_id)

        is_teacher = (course.teacher_id == user.user_id and user.user_type == 2)
        is_owner = (result.student_id == user.user_id)

        if not is_teacher and not is_owner:
             return {'message': 'You are not authorized to view this exam result.'}, HTTPStatus.FORBIDDEN
        return result, HTTPStatus.OK

    @exam_result_ops_ns.expect(exam_result_update_input_model, validate=True)
    @exam_result_ops_ns.marshal_with(exam_result_output_model) # For PUT response
    @jwt_required()
    def put(self, result_id):
        """Update an exam result (e.g., override score - Teacher only)."""
        current_user_id = get_jwt_identity()
        user = User.query.get_or_404(current_user_id)
        result = ExamResult.query.get_or_404(result_id)
        exam = Exam.query.get_or_404(result.exam_id)
        course = Course.query.get_or_404(exam.course_id)

        if not (course.teacher_id == user.user_id and user.user_type == 2):
            return {'message': 'Only the teacher of this course can update exam results.'}, HTTPStatus.FORBIDDEN

        data = exam_result_ops_ns.payload
        if data['score'] > exam.total_score:
            return {'message': f"Score cannot exceed exam's total score of {exam.total_score}."}, HTTPStatus.BAD_REQUEST

        result.score = data['score']
        # result.status = data.get('status', result.status) # If status update is allowed
        db.session.commit()
        return result, HTTPStatus.OK

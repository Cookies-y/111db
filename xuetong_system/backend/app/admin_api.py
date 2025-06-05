from flask_restx import Namespace, Resource, fields
from http import HTTPStatus
from flask import abort # Using Flask's abort for simplicity
from functools import wraps
from flask_jwt_extended import jwt_required, get_jwt_identity, verify_jwt_in_request, get_jwt

from . import db
from .models import User, Course # Import Course model
# Import DTOs from course_api for reuse
from .course_api import course_list_item_model, course_detail_model

# --- Admin Namespace ---
admin_ns = Namespace('admin', description='Administrator operations', path='/admin')


# --- Admin Role Check Decorator ---
def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)

        if not user:
            admin_ns.abort(HTTPStatus.UNAUTHORIZED, message='User not found, invalid token context.')

        if user.user_type != 3: # 3 for admin
            admin_ns.abort(HTTPStatus.FORBIDDEN, message='Administrator access required for this resource.')

        return fn(*args, **kwargs)
    return wrapper


# --- DTOs for Admin User View ---
admin_user_output_model = admin_ns.model('AdminUserOutput', {
    'user_id': fields.Integer(readonly=True, description='User ID'),
    'username': fields.String(description='Username'),
    'real_name': fields.String(description='Real name'),
    'email': fields.String(description='Email address'),
    'phone': fields.String(nullable=True, description='Phone number'),
    'user_type': fields.Integer(description='User type (1:Student, 2:Teacher, 3:Admin)'),
    'register_time': fields.DateTime(dt_format='iso8601', readonly=True, description='Registration timestamp'),
    'last_login': fields.DateTime(dt_format='iso8601', nullable=True, readonly=True, description='Last login timestamp')
})

# Note: We are reusing course_list_item_model and course_detail_model from course_api.py
# If admin-specific views of courses are needed later (e.g., with more/different fields),
# new DTOs can be defined here within admin_ns.


# --- API Resources ---

@admin_ns.route('/users')
class AdminUserList(Resource):
    method_decorators = [jwt_required(), admin_required]

    @admin_ns.doc(security='jsonWebToken', description="List all users (Admin access only).")
    @admin_ns.marshal_list_with(admin_user_output_model)
    def get(self):
        """Lists all users in the system."""
        users = User.query.order_by(User.user_id.asc()).all()
        return users, HTTPStatus.OK

@admin_ns.route('/users/<int:user_id>')
@admin_ns.param('user_id', 'The user identifier')
class AdminUserDetail(Resource):
    method_decorators = [jwt_required(), admin_required]

    @admin_ns.doc(security='jsonWebToken', description="Get details of a specific user (Admin access only).")
    @admin_ns.marshal_with(admin_user_output_model)
    @admin_ns.response(HTTPStatus.NOT_FOUND, 'User not found.')
    def get(self, user_id):
        """Fetches details of a specific user."""
        user = User.query.get_or_404(user_id, description=f"User with ID {user_id} not found.")
        return user, HTTPStatus.OK

# --- Admin Course Management Resources ---

@admin_ns.route('/courses')
class AdminCourseList(Resource):
    method_decorators = [jwt_required(), admin_required]

    @admin_ns.doc(security='jsonWebToken', description="List all courses in the system (Admin access only).")
    @admin_ns.marshal_list_with(course_list_item_model) # Reusing DTO from course_api
    def get(self):
        """Lists all courses in the system."""
        courses = Course.query.order_by(Course.course_id.asc()).all()
        return courses, HTTPStatus.OK

@admin_ns.route('/courses/<int:course_id>')
@admin_ns.param('course_id', 'The course identifier')
class AdminCourseDetail(Resource):
    method_decorators = [jwt_required(), admin_required]

    @admin_ns.doc(security='jsonWebToken', description="Get details of a specific course, including chapters and materials (Admin access only).")
    @admin_ns.marshal_with(course_detail_model) # Reusing DTO from course_api
    @admin_ns.response(HTTPStatus.NOT_FOUND, 'Course not found.')
    def get(self, course_id):
        """Fetches details of a specific course."""
        course = Course.query.get_or_404(course_id, description=f"Course with ID {course_id} not found.")
        return course, HTTPStatus.OK

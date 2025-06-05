from flask_restx import Namespace, Resource, fields
from flask import request
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from . import db, bcrypt
from .models import User
from http import HTTPStatus

auth_ns = Namespace('auth', description='Authentication and User Registration Operations')

# --- User Type Mapping ---
USER_TYPE_TO_INT = {'student': 1, 'teacher': 2, 'admin': 3}
INT_TO_USER_TYPE = {v: k for k, v in USER_TYPE_TO_INT.items()}

# --- Request Models ---
registration_input_model = auth_ns.model('UserRegistrationInput', {
    'username': fields.String(required=True, description='Unique username', min_length=3, max_length=50),
    'password': fields.String(required=True, description='User password', min_length=6, max_length=128),
    'real_name': fields.String(required=True, description='User\'s real name', max_length=50),
    'email': fields.String(required=True, description='User\'s email address', max_length=100),
    'user_type': fields.String(required=True, description='Type of user', enum=['student', 'teacher'], example='student')
})

login_input_model = auth_ns.model('LoginInput', {
    'email': fields.String(required=True, description='User\'s email address', example='student@example.com'),
    'password': fields.String(required=True, description='User password', example='password123')
})

# --- Response Models ---
message_model = auth_ns.model('ResponseMessage', {
    'message': fields.String(description='A message detailing the result of an operation')
})

user_public_model = auth_ns.model('UserPublicOutput', {
    'user_id': fields.Integer(readonly=True, description='User ID'),
    'username': fields.String(description='Username'),
    'email': fields.String(description='Email address'),
    'real_name': fields.String(description='Real name'),
    'user_type': fields.String(attribute=lambda x: INT_TO_USER_TYPE.get(x.user_type, 'unknown'), description='User type (student, teacher, admin)'),
    'register_time': fields.DateTime(description='Registration timestamp')
})

token_model = auth_ns.model('TokenOutput', {
    'access_token': fields.String(description='JWT Access Token')
})

protected_message_model = auth_ns.model('ProtectedMessageOutput', {
    'message': fields.String(description='A protected message confirming authentication'),
    'current_user_id': fields.Integer(description='ID of the authenticated user making the request')
})


# --- API Routes ---
@auth_ns.route('/register')
class UserRegistration(Resource):
    @auth_ns.expect(registration_input_model, validate=True)
    @auth_ns.marshal_with(user_public_model, code=HTTPStatus.CREATED, description='User registered successfully.')
    @auth_ns.response(HTTPStatus.BAD_REQUEST, 'Input validation error / Invalid user type string', model=message_model)
    @auth_ns.response(HTTPStatus.CONFLICT, 'User already exists (username or email)', model=message_model)
    def post(self):
        """Registers a new user."""
        data = auth_ns.payload

        username = data['username']
        password = data['password']
        real_name = data['real_name']
        email = data['email']
        user_type_str = data['user_type']

        if User.query.filter_by(username=username).first():
            return {'message': 'Username already exists.'}, HTTPStatus.CONFLICT
        if User.query.filter_by(email=email).first():
            return {'message': 'Email already exists.'}, HTTPStatus.CONFLICT

        user_type_int = USER_TYPE_TO_INT.get(user_type_str.lower())
        if user_type_int is None:
            return {'message': f"Invalid user_type '{user_type_str}'. Must be one of {list(USER_TYPE_TO_INT.keys())}."}, HTTPStatus.BAD_REQUEST

        if user_type_int == USER_TYPE_TO_INT['admin']:
            return {'message': "Registration as 'admin' is not allowed via this endpoint."}, HTTPStatus.BAD_REQUEST

        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        new_user = User(
            username=username,
            password_hash=hashed_password,
            real_name=real_name,
            email=email,
            user_type=user_type_int
        )

        db.session.add(new_user)
        db.session.commit()

        return new_user, HTTPStatus.CREATED

@auth_ns.route('/login')
class UserLogin(Resource):
    @auth_ns.expect(login_input_model, validate=True)
    @auth_ns.marshal_with(token_model, code=HTTPStatus.OK, description='Login successful, access token returned.')
    @auth_ns.response(HTTPStatus.UNAUTHORIZED, 'Invalid credentials or user not found', model=message_model)
    @auth_ns.response(HTTPStatus.BAD_REQUEST, 'Input validation error', model=message_model)
    def post(self):
        """Logs in a user and returns a JWT access token."""
        data = auth_ns.payload
        email = data['email']
        password = data['password']

        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            user.last_login = db.func.now()
            db.session.commit()

            access_token = create_access_token(identity=user.user_id)
            return {'access_token': access_token}, HTTPStatus.OK
        else:
            return {'message': 'Invalid credentials or user not found.'}, HTTPStatus.UNAUTHORIZED

@auth_ns.route('/protected')
class ProtectedResource(Resource):
    # Apply jwt_required to all methods in this Resource
    # method_decorators = [jwt_required()] # Alternative way to apply to all methods

    @jwt_required()
    @auth_ns.doc(security='jsonWebToken', description='Access this endpoint with a Bearer token in the Authorization header.')
    @auth_ns.marshal_with(protected_message_model, code=HTTPStatus.OK, description='Successfully accessed protected resource.')
    @auth_ns.response(HTTPStatus.UNAUTHORIZED, 'Missing or invalid token (ensure Bearer token is used).', model=message_model)
    @auth_ns.response(HTTPStatus.FORBIDDEN, 'Token is invalid or expired (though often results in 401/422 with Flask-JWT-Extended).', model=message_model)
    def get(self):
        """Access a protected resource. Requires JWT authentication."""
        current_user_id = get_jwt_identity()
        # You could fetch the user from DB if more details are needed:
        # user = User.query.get(current_user_id)
        return {
            'message': f'Hello User ID {current_user_id}! This is a protected endpoint.',
            'current_user_id': current_user_id
        }, HTTPStatus.OK

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, TextAreaField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError
from .models import User

class RegistrationForm(FlaskForm):
    username = StringField('用户名', validators=[DataRequired(), Length(min=4, max=50)])
    email = StringField('邮箱', validators=[DataRequired(), Email(), Length(max=100)])
    real_name = StringField('真实姓名', validators=[DataRequired(), Length(max=50)])
    user_type = SelectField('账户类型', choices=[('student', '学生'), ('teacher', '教师')], validators=[DataRequired()])
    password = PasswordField('密码', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('确认密码', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('注册')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            # TODO: Translate validation messages
            raise ValidationError('该用户名已被占用，请选择其他用户名。')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            # TODO: Translate validation messages
            raise ValidationError('该邮箱已被注册，请使用其他邮箱或直接登录。')

class LoginForm(FlaskForm):
    email = StringField('邮箱', validators=[DataRequired(), Email()])
    password = PasswordField('密码', validators=[DataRequired()])
    submit = SubmitField('登录')

class CourseForm(FlaskForm):
    course_name = StringField('课程名称', validators=[DataRequired(), Length(min=3, max=100)])
    description = TextAreaField('课程描述', validators=[Length(max=500)])
    submit = SubmitField('创建课程')

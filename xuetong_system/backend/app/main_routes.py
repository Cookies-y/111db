from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from . import db
from .models import Course, User
from .forms import CourseForm

main_bp = Blueprint('main', __name__) # No template_folder specified, will use app/templates

@main_bp.route('/')
@main_bp.route('/index')
@login_required # Require login for the main index page
def index():
    # For now, the index page will list courses.
    # This also serves as the redirect target from auth routes.
    return redirect(url_for('main.list_courses'))

@main_bp.route('/courses')
@login_required
def list_courses():
    courses = Course.query.all()
    # Title attr will be handled by template translation
    return render_template('main/list_courses.html', courses=courses, title="Available Courses")

@main_bp.route('/create_course', methods=['GET', 'POST'])
@login_required
def create_course():
    if current_user.user_type != 'teacher':
        flash('只有教师才能创建课程。', 'danger')
        return redirect(url_for('main.list_courses'))

    form = CourseForm()
    if form.validate_on_submit():
        course = Course(
            course_name=form.course_name.data,
            description=form.description.data,
            teacher_id=current_user.id
        )
        db.session.add(course)
        db.session.commit()
        flash('课程创建成功！', 'success')
        return redirect(url_for('main.list_courses'))

    # Title attr will be handled by template translation
    return render_template('main/create_course.html', title='Create New Course', form=form)

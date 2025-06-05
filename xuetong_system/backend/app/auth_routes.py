from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from . import db # Assuming db is accessible from the app package
from .models import User
from .forms import RegistrationForm, LoginForm

# It's good practice to specify template_folder if it's not the default 'templates' directly under blueprint
# For example, if you have app/templates/auth/login.html, then 'templates/auth' or just 'templates' if it's standard.
# If your templates are in backend/app/templates/auth, and your blueprint is in backend/app/auth_routes.py
# then Flask should be able to find 'auth/login.html' if you use render_template('auth/login.html')
# No, the template_folder for a blueprint is relative to the blueprint's location by default,
# but it's more common to put all templates in the app's main template folder (app/templates)
# and then organize them in subdirectories (e.g. app/templates/auth/login.html).
# So, we will reference them as 'auth/login.html' and 'auth/register.html' in render_template.
auth_bp = Blueprint('auth', __name__) # No need to specify template_folder here if using app/templates/auth

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index')) # Assuming a 'main.index' route will exist
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            email=form.email.data,
            real_name=form.real_name.data,
            user_type=form.user_type.data
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!', 'success')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', title='Register', form=form)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index')) # Assuming a 'main.index' route will exist
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            # next_page = request.args.get('next') # For redirecting after login
            # return redirect(next_page) if next_page else redirect(url_for('main.index'))
            flash('Login successful.', 'success')
            return redirect(url_for('main.index')) # Simplified redirect for now
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('auth/login.html', title='Login', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))

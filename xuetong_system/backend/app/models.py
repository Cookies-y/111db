from . import db
from datetime import datetime, date
from flask_bcrypt import generate_password_hash, check_password_hash # For User model password hashing

class User(db.Model):
    __tablename__ = 'user'
    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    password_hash = db.Column(db.String(128), nullable=False) # Bcrypt hashes are typically 60 chars
    real_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    phone = db.Column(db.String(20), nullable=True)
    user_type = db.Column(db.SmallInteger, nullable=False)  # 1=student, 2=teacher, 3=admin
    register_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    last_login = db.Column(db.DateTime, nullable=True)

    # Relationships
    # For teachers
    courses_taught = db.relationship('Course', backref='teacher', lazy='dynamic', foreign_keys='Course.teacher_id')

    # For students
    enrollments = db.relationship('Enrollment', backref='student', lazy='dynamic', foreign_keys='Enrollment.student_id')
    submissions = db.relationship('Submission', backref='student', lazy='dynamic', foreign_keys='Submission.student_id')
    exam_results = db.relationship('ExamResult', backref='student', lazy='dynamic', foreign_keys='ExamResult.student_id')

    # General
    discussions_posted = db.relationship('Discussion', backref='author', lazy='dynamic', foreign_keys='Discussion.user_id')
    progress_records = db.relationship('Progress', backref='user', lazy='dynamic', foreign_keys='Progress.user_id')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'

class Course(db.Model):
    __tablename__ = 'course'
    course_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    course_name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    teacher_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    create_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    status = db.Column(db.SmallInteger, nullable=False)  # 1=Not Started, 2=In Progress, 3=Ended
    cover_image = db.Column(db.String(255), nullable=True)

    # Relationships
    chapters = db.relationship('Chapter', backref='course', lazy='dynamic', cascade="all, delete-orphan")
    assignments = db.relationship('Assignment', backref='course', lazy='dynamic', cascade="all, delete-orphan")
    exams = db.relationship('Exam', backref='course', lazy='dynamic', cascade="all, delete-orphan")
    discussions = db.relationship('Discussion', backref='course', lazy='dynamic', cascade="all, delete-orphan")
    enrollments = db.relationship('Enrollment', backref='course', lazy='dynamic', cascade="all, delete-orphan")

    def __repr__(self):
        return f'<Course {self.course_name}>'

class Chapter(db.Model):
    __tablename__ = 'chapter'
    chapter_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    course_id = db.Column(db.Integer, db.ForeignKey('course.course_id'), nullable=False)
    chapter_name = db.Column(db.String(100), nullable=False)
    chapter_order = db.Column(db.Integer, nullable=False)
    description = db.Column(db.Text, nullable=True)

    # Relationships
    materials = db.relationship('Material', backref='chapter', lazy='dynamic', cascade="all, delete-orphan")

    def __repr__(self):
        return f'<Chapter {self.chapter_name}>'

class Material(db.Model):
    __tablename__ = 'material'
    material_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    chapter_id = db.Column(db.Integer, db.ForeignKey('chapter.chapter_id'), nullable=False)
    material_type = db.Column(db.SmallInteger, nullable=False)  # 1=Video, 2=Document, 3=Link
    title = db.Column(db.String(100), nullable=False)
    url = db.Column(db.String(255), nullable=False) # Could be path or URL
    duration = db.Column(db.Integer, nullable=True)  # Video duration in seconds
    file_size = db.Column(db.Integer, nullable=True)  # File size in KB
    upload_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    progress_records = db.relationship('Progress', backref='material', lazy='dynamic', cascade="all, delete-orphan")

    def __repr__(self):
        return f'<Material {self.title}>'

class Assignment(db.Model):
    __tablename__ = 'assignment'
    assignment_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    course_id = db.Column(db.Integer, db.ForeignKey('course.course_id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    deadline = db.Column(db.DateTime, nullable=False)
    total_score = db.Column(db.Integer, nullable=False, default=100)
    create_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    submissions = db.relationship('Submission', backref='assignment', lazy='dynamic', cascade="all, delete-orphan")

    def __repr__(self):
        return f'<Assignment {self.title}>'

class Submission(db.Model):
    __tablename__ = 'submission'
    submission_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    assignment_id = db.Column(db.Integer, db.ForeignKey('assignment.assignment_id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    content = db.Column(db.Text, nullable=True)
    attachment = db.Column(db.String(255), nullable=True)  # URL to attachment
    submit_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    score = db.Column(db.Integer, nullable=True)
    feedback = db.Column(db.Text, nullable=True)  # Teacher feedback

    def __repr__(self):
        return f'<Submission {self.submission_id} for Assignment {self.assignment_id} by Student {self.student_id}>'

class Exam(db.Model):
    __tablename__ = 'exam'
    exam_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    course_id = db.Column(db.Integer, db.ForeignKey('course.course_id'), nullable=False)
    exam_name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    total_score = db.Column(db.Integer, nullable=False, default=100)
    duration = db.Column(db.Integer, nullable=False)  # Exam duration in minutes

    # Relationships
    results = db.relationship('ExamResult', backref='exam', lazy='dynamic', cascade="all, delete-orphan")

    def __repr__(self):
        return f'<Exam {self.exam_name}>'

class ExamResult(db.Model):
    __tablename__ = 'exam_result'
    result_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    exam_id = db.Column(db.Integer, db.ForeignKey('exam.exam_id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    score = db.Column(db.Integer, nullable=False)
    submit_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    status = db.Column(db.SmallInteger, nullable=False)  # 1=Not Started, 2=In Progress, 3=Completed

    def __repr__(self):
        return f'<ExamResult {self.result_id} for Exam {self.exam_id} by Student {self.student_id}>'

class Discussion(db.Model):
    __tablename__ = 'discussion'
    post_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    course_id = db.Column(db.Integer, db.ForeignKey('course.course_id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    post_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    parent_id = db.Column(db.Integer, db.ForeignKey('discussion.post_id'), nullable=True)

    # Relationships
    replies = db.relationship('Discussion', backref=db.backref('parent_post', remote_side=[post_id]), lazy='dynamic', cascade="all, delete-orphan")

    def __repr__(self):
        return f'<DiscussionPost {self.title} by User {self.user_id}>'

class Enrollment(db.Model):
    __tablename__ = 'enrollment'
    enrollment_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    course_id = db.Column(db.Integer, db.ForeignKey('course.course_id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    enroll_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    completion_status = db.Column(db.SmallInteger, nullable=False, default=0)  # 0=Not Completed, 1=Completed
    final_grade = db.Column(db.Integer, nullable=True)

    __table_args__ = (db.UniqueConstraint('course_id', 'student_id', name='uq_enrollment_course_student'),)

    def __repr__(self):
        return f'<Enrollment Student {self.student_id} in Course {self.course_id}>'

class Progress(db.Model):
    __tablename__ = 'progress'
    progress_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    material_id = db.Column(db.Integer, db.ForeignKey('material.material_id'), nullable=False)
    progress = db.Column(db.Integer, nullable=False, default=0)  # Percentage, 0-100
    last_learn_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_completed = db.Column(db.Boolean, nullable=False, default=False)

    __table_args__ = (db.UniqueConstraint('user_id', 'material_id', name='uq_progress_user_material'),)

    def __repr__(self):
        return f'<Progress User {self.user_id} on Material {self.material_id}: {self.progress}%>'

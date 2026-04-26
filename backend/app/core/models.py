from datetime import datetime
from enum import Enum
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class UserRole(Enum):
    STUDENT = "STUDENT"
    FACULTY = "FACULTY"
    ADMIN = "ADMIN"

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.Enum(UserRole), nullable=False, default=UserRole.STUDENT)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    professor_profile = db.relationship('Professor', back_populates='user', uselist=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Professor(db.Model):
    __tablename__ = 'professors'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False) # MANDATORY
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    
    user = db.relationship('User', back_populates='professor_profile')
    requirements = db.relationship('CourseRequirement', backref='instructor', lazy=True)
    timetable_entries = db.relationship('TimetableEntry', backref='instructor', lazy=True)

class Room(db.Model):
    __tablename__ = 'rooms'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    is_lab = db.Column(db.Boolean, default=False)
    capacity = db.Column(db.Integer, default=100)
    x = db.Column(db.Float, default=0.0)
    y = db.Column(db.Float, default=0.0)
    z = db.Column(db.Float, default=0.0)

class StudentGroup(db.Model):
    __tablename__ = 'student_groups'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    size = db.Column(db.Integer, nullable=False)
    
    requirements = db.relationship('CourseRequirement', backref='student_grp', lazy=True)
    timetable_entries = db.relationship('TimetableEntry', backref='student_grp', lazy=True)

class CourseRequirement(db.Model):
    __tablename__ = 'course_requirements'
    id = db.Column(db.Integer, primary_key=True)
    course_code = db.Column(db.String(20), nullable=False)
    session_type = db.Column(db.String(20), nullable=False) 
    professor_id = db.Column(db.Integer, db.ForeignKey('professors.id'), nullable=False)
    student_group_id = db.Column(db.Integer, db.ForeignKey('student_groups.id'), nullable=False)
    slots_required = db.Column(db.Integer, default=1)
    slots_continuous = db.Column(db.Boolean, default=False)
    preference_bin = db.Column(db.Integer, default=1)

class Schedule(db.Model):
    __tablename__ = 'schedules'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    fitness_score = db.Column(db.Float)
    is_active = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    entries = db.relationship('TimetableEntry', backref='schedule', lazy=True, cascade="all, delete-orphan")

class TimetableEntry(db.Model):
    __tablename__ = 'timetable_entries'
    id = db.Column(db.Integer, primary_key=True)
    schedule_id = db.Column(db.Integer, db.ForeignKey('schedules.id'), nullable=False)
    day = db.Column(db.String(20), nullable=False)
    time_slot = db.Column(db.Integer, nullable=False)
    course_code = db.Column(db.String(20), nullable=False)
    room_id = db.Column(db.Integer, db.ForeignKey('rooms.id'), nullable=False)
    professor_id = db.Column(db.Integer, db.ForeignKey('professors.id'), nullable=False)
    student_group_id = db.Column(db.Integer, db.ForeignKey('student_groups.id'), nullable=False)
    session_type = db.Column(db.String(20), nullable=False)

    room = db.relationship('Room', backref='timetable_entries')

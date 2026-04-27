from datetime import datetime, UTC
from enum import Enum
from .extensions import db
from werkzeug.security import generate_password_hash, check_password_hash

class UserRole(Enum):
    STUDENT = "STUDENT"
    FACULTY = "FACULTY"
    ADMIN = "ADMIN"

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.Enum(UserRole), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(UTC))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Professor(db.Model):
    __tablename__ = 'professors'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)

class Room(db.Model):
    __tablename__ = 'rooms'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    is_lab = db.Column(db.Boolean, default=False)
    capacity = db.Column(db.Integer, nullable=False)
    x = db.Column(db.Float, default=0.0)
    y = db.Column(db.Float, default=0.0)
    z = db.Column(db.Float, default=0.0)

class StudentGroup(db.Model):
    __tablename__ = 'student_groups'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    size = db.Column(db.Integer, nullable=False)

class CourseRequirement(db.Model):
    __tablename__ = 'course_requirements'
    id = db.Column(db.Integer, primary_key=True)
    course_code = db.Column(db.String(20), nullable=False)
    session_type = db.Column(db.String(20), nullable=False) # 'lecture', 'lab', 'tutorial'
    professor_id = db.Column(db.Integer, db.ForeignKey('professors.id'), nullable=False)
    student_group_id = db.Column(db.Integer, db.ForeignKey('student_groups.id'), nullable=False)
    slots_required = db.Column(db.Integer, default=1)
    slots_continuous = db.Column(db.Boolean, default=False)
    preference_bin = db.Column(db.Integer, default=1) # 1: Morning, 2: Afternoon, 3: Flexible

class Schedule(db.Model):
    __tablename__ = 'schedules'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(UTC))
    fitness_score = db.Column(db.Float)
    is_active = db.Column(db.Boolean, default=False)

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

class ActivityLog(db.Model):
    __tablename__ = 'activity_logs'
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(50), nullable=False) # 'NOTIFICATION' or 'CHANGE'
    title = db.Column(db.String(100), nullable=False)
    message = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True) # Optional: target user
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(UTC))

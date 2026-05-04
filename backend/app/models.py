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

    professor_profile = db.relationship('Professor', back_populates='user', uselist=False)

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
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(UTC))
    
    user = db.relationship('User', back_populates='professor_profile')
    course_instances = db.relationship('CourseInstance', backref='instructor', lazy=True)
    timetable_entries = db.relationship('TimetableEntry', backref='instructor', lazy=True)

class Room(db.Model):
    __tablename__ = 'rooms'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    is_lab = db.Column(db.Boolean, default=False)
    capacity = db.Column(db.Integer, default=100)
    x = db.Column(db.Float, default=0.0)
    y = db.Column(db.Float, default=0.0)
    z = db.Column(db.Float, default=0.0)
    allowed_batches = db.Column(db.JSON, nullable=True)  # None = all batches allowed, List of batch names = restricted
    allowed_departments = db.Column(db.JSON, nullable=True)  # None/empty = all departments allowed, List of dept codes = restricted
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(UTC))
    
    course_instances = db.relationship('CourseInstance', backref='room', lazy=True)
    timetable_entries = db.relationship('TimetableEntry', backref='room', lazy=True)

# ============================================================================
# StudentGroup Hierarchy Support
# ============================================================================
student_group_hierarchy = db.Table(
    'student_group_hierarchy',
    db.Column('child_id', db.Integer, db.ForeignKey('student_groups.id', ondelete='CASCADE'), primary_key=True),
    db.Column('parent_id', db.Integer, db.ForeignKey('student_groups.id', ondelete='CASCADE'), primary_key=True)
)

class StudentGroup(db.Model):
    __tablename__ = 'student_groups'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    size = db.Column(db.Integer, nullable=False)
    level = db.Column(db.String(50), default='batch')  # 'batch', 'department', 'track', 'elective'
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(UTC))
    
    # Self-referential many-to-many relationship for hierarchy
    parent_groups = db.relationship(
        'StudentGroup',
        secondary=student_group_hierarchy,
        primaryjoin=id == student_group_hierarchy.c.child_id,
        secondaryjoin=id == student_group_hierarchy.c.parent_id,
        backref='child_groups',
        lazy=True
    )
    
    course_instances = db.relationship('CourseInstance', backref='student_grp', lazy=True)
    timetable_entries = db.relationship('TimetableEntry', backref='student_grp', lazy=True)

# ============================================================================
# Course: Base course template (metadata)
# ============================================================================
class Course(db.Model):
    __tablename__ = 'courses'
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    total_credits = db.Column(db.Integer, nullable=False)
    lectures_per_week = db.Column(db.Integer, default=0)
    tutorials_per_week = db.Column(db.Integer, default=0)
    practicals_per_week = db.Column(db.Integer, default=0)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(UTC))
    
    instances = db.relationship('CourseInstance', backref='course_template', lazy=True)

# ============================================================================
# CourseInstance: Actual session to be scheduled (what the GA algorithm works with)
# ============================================================================
class CourseInstance(db.Model):
    __tablename__ = 'course_instances'
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.String(20), db.ForeignKey('courses.course_id'), nullable=False)
    session_type = db.Column(db.String(20), nullable=False)  # 'lecture', 'tutorial', 'lab'
    instructor_id = db.Column(db.Integer, db.ForeignKey('professors.id'), nullable=False)
    room_id = db.Column(db.Integer, db.ForeignKey('rooms.id'), nullable=False)
    student_group_id = db.Column(db.Integer, db.ForeignKey('student_groups.id'), nullable=False)
    
    # Scheduling constraints
    slots_required = db.Column(db.Integer, default=1)
    slots_continuous = db.Column(db.Boolean, default=False)
    preference_bin = db.Column(db.Integer, default=1)  # 1=morning, 2=noon, 3=evening
    lecture_consecutive = db.Column(db.Boolean, default=False)  # max 1 lecture/day constraint
    
    # Elective grouping constraint
    parallelizable_id = db.Column(db.Integer)  # Same ID = mutually exclusive in same track
    
    course_credits = db.Column(db.Float)
    department_name = db.Column(db.String(50), nullable=True)  # e.g., "CSE", "ME", "General" - department owning/teaching this course
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(UTC))
    
    timetable_entries = db.relationship('TimetableEntry', backref='course_instance', lazy=True)

# ============================================================================
# Time Slot Configuration
# ============================================================================
class TimeSlotConfiguration(db.Model):
    __tablename__ = 'time_slot_configuration'
    id = db.Column(db.Integer, primary_key=True)
    day_of_week = db.Column(db.String(20), unique=True, nullable=False)
    total_slots = db.Column(db.Integer, nullable=False)
    preference_bin_1_slots = db.Column(db.Integer)  # morning bin
    preference_bin_2_slots = db.Column(db.Integer)  # noon bin
    preference_bin_3_slots = db.Column(db.Integer)  # evening bin
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(UTC))

# ============================================================================
# Preference Bins
# ============================================================================
class PreferenceBin(db.Model):
    __tablename__ = 'preference_bins'
    id = db.Column(db.Integer, primary_key=True)
    bin_id = db.Column(db.Integer, unique=True, nullable=False)
    name = db.Column(db.String(50))
    start_time = db.Column(db.Time)
    end_time = db.Column(db.Time)

class Schedule(db.Model):
    __tablename__ = 'schedules'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(UTC))
    fitness_score = db.Column(db.Float)
    is_active = db.Column(db.Boolean, default=False)
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC))
    
    entries = db.relationship('TimetableEntry', backref='schedule', lazy=True, cascade="all, delete-orphan")

class TimetableEntry(db.Model):
    __tablename__ = 'timetable_entries'
    id = db.Column(db.Integer, primary_key=True)
    schedule_id = db.Column(db.Integer, db.ForeignKey('schedules.id'), nullable=False)
    day_of_week = db.Column(db.String(20), nullable=False)
    time_slot = db.Column(db.Integer, nullable=False)
    course_instance_id = db.Column(db.Integer, db.ForeignKey('course_instances.id'), nullable=False)
    room_id = db.Column(db.Integer, db.ForeignKey('rooms.id'), nullable=False)
    instructor_id = db.Column(db.Integer, db.ForeignKey('professors.id'), nullable=False)
    student_group_id = db.Column(db.Integer, db.ForeignKey('student_groups.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(UTC))

class ActivityLog(db.Model):
    __tablename__ = 'activity_logs'
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(50), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    message = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(UTC))

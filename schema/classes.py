"""
Data Model Classes for Genetic Algorithm Timetable Scheduler

These classes represent the core entities needed by the GA engine:
- Instructor: A professor/teacher
- Room: A physical classroom/lab
- StudentGroup: A cohort of students
- CourseInstance: A scheduled course requirement
"""


class Instructor:
    """Represents a professor or instructor"""
    def __init__(self, id, name):
        self.id = id
        self.name = name
    
    def __repr__(self):
        return f"Instructor({self.id}, {self.name})"


class Room:
    """Represents a physical classroom, lab, or lecture hall"""
    def __init__(self, id, name, is_lab=False, capacity=100, x=0.0, y=0.0, z=0.0):
        self.id = id
        self.name = name
        self.is_lab = is_lab
        self.capacity = capacity
        self.x = x  # X coordinate for distance calculation
        self.y = y  # Y coordinate for distance calculation
        self.z = z  # Z coordinate for distance calculation
    
    def __repr__(self):
        room_type = "Lab" if self.is_lab else "Classroom"
        return f"Room({self.id}, {self.name}, {room_type}, cap={self.capacity})"


class StudentGroup:
    """Represents a cohort of students (e.g., CS1, AI2)"""
    def __init__(self, name, size, super_groups=None):
        self.name = name
        self.size = size
        self.super_groups = super_groups if super_groups else []
    
    def __repr__(self):
        return f"StudentGroup({self.name}, size={self.size})"


class CourseInstance:
    """
    Represents a single course instance that needs to be scheduled.
    
    This is a requirement that the GA must satisfy.
    Example: "CS2101-Lecture for CS1 (Dr. Rakesh, 3 slots, preferably morning)"
    """
    def __init__(self, course_id, session_type, instructor, student_grp,
                 slots_req=1, slots_continuous=False, preference_bin=1, lecture_consecutive=False,
                 instance_id=None, parallelizable_id=None):
        self.course_id = course_id  # e.g., "MA2103", "CS/AI 2102"
        self.session_type = session_type  # 'lecture', 'tutorial', 'lab'
        self.instructor = instructor  # Instructor object
        self.student_grp = student_grp  # StudentGroup object
        self.slots_req = slots_req  # How many time slots needed
        self.slots_continuous = slots_continuous  # Must slots be consecutive?
        self.preference_bin = preference_bin  # 1=morning, 2=noon, 3=evening
        self.lecture_consecutive = lecture_consecutive  # Allow multiple lectures same day?
        self.parallelizable_id = parallelizable_id  # None=can run with any; Int=grouped electives (same ID can coexist, different ID cannot)
        self.id = instance_id if instance_id is not None else id(self)
        self.room = None  # Will be assigned by GA during scheduling
    
    def __repr__(self):
        return f"CourseInstance({self.course_id}-{self.session_type}, {self.student_grp.name}, slots={self.slots_req})"

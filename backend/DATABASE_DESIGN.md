# Database Design for Automated Timetable Generation

## PART 1: COMPLETE ANALYSIS OF test_data.py

### 1.1 Class Hierarchy & Relationships

```
Instructor (1)
  ├─ id: int
  ├─ name: str
  └─ relationships: used by CourseInstance.instructor

Room (1)
  ├─ id: int
  ├─ name: str
  ├─ coordinates: (x, y, z) - 3D location for distance calculations
  ├─ capacity: int
  ├─ is_lab: bool - distinguishes regular rooms from laboratory spaces
  └─ relationships: used by CourseInstance.room

StudentGroup (*)
  ├─ name: str
  ├─ size: int - number of students
  ├─ super_groups: List[StudentGroup] - HIERARCHICAL (parent groups)
  └─ HIERARCHY EXAMPLE:
      Class_2025 (batch level, 200 students)
      ├─ CSE_2025 (dept level, 50 students)
      │  ├─ CSE_RL_NLP_Track (elective track, 53 students)
      │  │  └─ RL_Elective_2025 (final elective, 35 students)
      │  │  └─ NL_Elective_2025 (final elective, 35 students)
      │  └─ CSE_GenAI_Track (separate track)
      │     └─ GA_Elective_2025 (final elective, 30 students)
      ├─ ME_2025 (dept level, 50 students)
      └─ ECE_2025 (dept level, 50 students)

Course (Base Template)
  ├─ course_id: str (e.g., "CS201")
  ├─ name: str (e.g., "Programming")
  ├─ total_credits: int
  ├─ lectures: int - number of lecture sessions per week
  ├─ tutorials: int - number of tutorial sessions per week
  ├─ practicals: int - number of practical/lab sessions per week
  └─ purpose: Defines course composition, used to create CourseInstance objects

CourseInstance (Actual Session to Schedule)
  ├─ id: int - unique identifier
  ├─ course_id: str - reference to Course
  ├─ session_type: str ("lecture", "tutorial", "lab")
  ├─ instructor: Instructor - who teaches this session
  ├─ room: Room - where this session occurs
  ├─ student_grp: StudentGroup - which students attend
  ├─ slots_req: int - consecutive time slots needed (e.g., 2 for 2-hour labs)
  ├─ slots_continuous: bool - must slots be consecutive?
  ├─ preference_bin: int (1=morning, 2=noon, 3=evening) - instructor preference
  ├─ lecture_consecutive: bool - max 1 lecture per day (False) or multiple allowed (True)?
  ├─ parallelizable_id: int | None
  │  └─ KEY CONSTRAINT: Determines elective exclusion groups
  │     - None: can run with any other course
  │     - Same ID (e.g., 1): RL and NL (same parallelizable_id=1) are in same track
  │                          → RL lectures CANNOT run parallel with NL lectures
  │     - Different ID (e.g., 1 vs 2): GA (id=2) CAN run parallel with RL/NL
  ├─ course_credits: float | None - set during generation
  └─ purpose: Represents ONE session type of a course for ONE student group

### 1.2 Key Instantiation Patterns

#### Student Groups - Hierarchical Creation
```python
# Batch level (root)
class_2025 = StudentGroup(name="Class of 2025", size=200)

# Department level
cse_2025 = StudentGroup(name="CSE-2025", size=50, super_groups=[class_2025])

# Track level (intermediate grouping for electives)
cse_rl_nlp_track = StudentGroup(name="CSE-RL-NLP-Track", size=53, super_groups=[cse_2025])

# Final elective level
rl_elective_2025 = StudentGroup(
    name="RL-Elective-2025", 
    size=35, 
    super_groups=[cse_rl_nlp_track, cse_2025, class_2025]  # Multiple parents!
)
```
**Important**: Students can have MULTIPLE parent groups (not just one parent)

#### Courses - From Template to Instances
```python
# 1. Define base course (template)
cs201 = Course(
    course_id="CS201",
    name="Programming",
    total_credits=4,
    lectures=3,    # 3 lecture sessions per week
    tutorials=1,   # 1 tutorial per week
    practicals=2   # 2 practical sessions per week
)

# 2. Create instances for EACH session type and EACH student group
# Create 3 lecture instances (one per lecture session per week)
for i in range(cs201.lectures):
    CourseInstance(
        id=instance_counter,
        course_id="CS201",
        session_type="lecture",
        instructor=prof_kumar,
        room=room_101,
        student_grp=cse_2025,
        slots_req=1,
        slots_continuous=False,
        preference_bin=1
    )
    instance_counter += 1

# Create 1 tutorial instance
CourseInstance(
    id=instance_counter,
    course_id="CS201",
    session_type="tutorial",
    instructor=prof_singh,
    room=room_102,
    student_grp=cse_2025,
    slots_req=1,
    slots_continuous=False,
    preference_bin=2
)

# Create 1 lab instance (requires 2 CONTINUOUS slots)
CourseInstance(
    id=instance_counter,
    course_id="CS201",
    session_type="lab",
    instructor=prof_sharma,
    room=lab_201,
    student_grp=cse_2025,
    slots_req=cs201.practicals,  # 2 slots
    slots_continuous=True,        # Must be consecutive
    preference_bin=3
)
```

#### Parallelizable Groups - Elective Constraints
```python
# Track 1 (Mutually exclusive: RL OR NL, but not both at same time)
rl_elective_2025 = StudentGroup(name="RL-Elective-2025", size=35)
nl_elective_2025 = StudentGroup(name="NL-Elective-2025", size=35)

for i in range(rl201.lectures):
    CourseInstance(
        id=...,
        course_id="RL201",
        student_grp=rl_elective_2025,
        parallelizable_id=1,  # RL Track
        ...
    )

for i in range(nl201.lectures):
    CourseInstance(
        id=...,
        course_id="NL201",
        student_grp=nl_elective_2025,
        parallelizable_id=1,  # Same as RL! → Cannot schedule together
        ...
    )

# Track 2 (Can run parallel with Track 1)
ga_elective_2025 = StudentGroup(name="GA-Elective-2025", size=30)

for i in range(ga201.lectures):
    CourseInstance(
        id=...,
        course_id="GA201",
        student_grp=ga_elective_2025,
        parallelizable_id=2,  # Different ID! → CAN run with RL/NL
        ...
    )
```

---

## PART 2: PROPOSED POSTGRESQL DATABASE SCHEMA

### 2.1 Database Tables

```sql
-- ============================================================================
-- TABLE: instructors
-- ============================================================================
CREATE TABLE instructors (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT unique_instructor_email UNIQUE(email)
);

-- ============================================================================
-- TABLE: rooms
-- ============================================================================
CREATE TABLE rooms (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    capacity INTEGER NOT NULL,
    is_lab BOOLEAN DEFAULT FALSE,
    location_x FLOAT DEFAULT 0.0,
    location_y FLOAT DEFAULT 0.0,
    location_z FLOAT DEFAULT 0.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- TABLE: student_groups
-- Parent-child hierarchy stored here
-- ============================================================================
CREATE TABLE student_groups (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    size INTEGER NOT NULL,
    level VARCHAR(50) NOT NULL, -- 'batch', 'department', 'track', 'elective'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- TABLE: student_group_hierarchy
-- Manages many-to-many parent-child relationships
-- Multiple parents allowed (e.g., RL_Elective_2025 has 3 parents)
-- ============================================================================
CREATE TABLE student_group_hierarchy (
    child_id INTEGER NOT NULL,
    parent_id INTEGER NOT NULL,
    PRIMARY KEY (child_id, parent_id),
    FOREIGN KEY (child_id) REFERENCES student_groups(id) ON DELETE CASCADE,
    FOREIGN KEY (parent_id) REFERENCES student_groups(id) ON DELETE CASCADE,
    CONSTRAINT no_self_reference CHECK (child_id != parent_id)
);

-- ============================================================================
-- TABLE: courses
-- Base course definitions (templates)
-- ============================================================================
CREATE TABLE courses (
    id SERIAL PRIMARY KEY,
    course_id VARCHAR(20) NOT NULL UNIQUE,
    name VARCHAR(100) NOT NULL,
    total_credits INTEGER NOT NULL,
    lectures_per_week INTEGER DEFAULT 0,
    tutorials_per_week INTEGER DEFAULT 0,
    practicals_per_week INTEGER DEFAULT 0,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- TABLE: course_instances
-- Actual sessions to be scheduled (what the GA works with)
-- ============================================================================
CREATE TABLE course_instances (
    id SERIAL PRIMARY KEY,
    course_id VARCHAR(20) NOT NULL,
    session_type VARCHAR(20) NOT NULL, -- 'lecture', 'tutorial', 'lab'
    instructor_id INTEGER NOT NULL,
    room_id INTEGER NOT NULL,
    student_group_id INTEGER NOT NULL,
    slots_required INTEGER DEFAULT 1, -- consecutive time slots needed
    slots_continuous BOOLEAN DEFAULT FALSE, -- must be consecutive?
    preference_bin INTEGER DEFAULT 1, -- 1=morning, 2=noon, 3=evening
    lecture_consecutive BOOLEAN DEFAULT FALSE, -- max 1/day (False) or multiple (True)
    parallelizable_id INTEGER, -- elective grouping constraint
    course_credits FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (course_id) REFERENCES courses(course_id),
    FOREIGN KEY (instructor_id) REFERENCES instructors(id),
    FOREIGN KEY (room_id) REFERENCES rooms(id),
    FOREIGN KEY (student_group_id) REFERENCES student_groups(id)
);

-- ============================================================================
-- TABLE: time_slot_configuration
-- Day-specific time slot definitions
-- ============================================================================
CREATE TABLE time_slot_configuration (
    id SERIAL PRIMARY KEY,
    day_of_week VARCHAR(20) NOT NULL, -- 'Monday', 'Tuesday', etc.
    total_slots INTEGER NOT NULL, -- number of slots available that day
    preference_bin_1_slots INTEGER, -- slots in morning bin
    preference_bin_2_slots INTEGER, -- slots in noon bin
    preference_bin_3_slots INTEGER, -- slots in evening bin
    UNIQUE(day_of_week)
);

-- ============================================================================
-- TABLE: preference_bins
-- Time preference definitions
-- ============================================================================
CREATE TABLE preference_bins (
    id SERIAL PRIMARY KEY,
    bin_id INTEGER NOT NULL UNIQUE,
    name VARCHAR(50), -- 'morning', 'noon', 'evening'
    start_time TIME,
    end_time TIME
);

-- ============================================================================
-- TABLE: timetable_schedules
-- Stores generated schedules/solutions
-- ============================================================================
CREATE TABLE timetable_schedules (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    fitness_score FLOAT,
    is_active BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- TABLE: timetable_entries
-- Individual entries in a schedule
-- ============================================================================
CREATE TABLE timetable_entries (
    id SERIAL PRIMARY KEY,
    schedule_id INTEGER NOT NULL,
    day_of_week VARCHAR(20) NOT NULL,
    time_slot INTEGER NOT NULL,
    course_instance_id INTEGER NOT NULL,
    room_id INTEGER NOT NULL,
    instructor_id INTEGER NOT NULL,
    student_group_id INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (schedule_id) REFERENCES timetable_schedules(id) ON DELETE CASCADE,
    FOREIGN KEY (course_instance_id) REFERENCES course_instances(id),
    FOREIGN KEY (room_id) REFERENCES rooms(id),
    FOREIGN KEY (instructor_id) REFERENCES instructors(id),
    FOREIGN KEY (student_group_id) REFERENCES student_groups(id)
);

-- ============================================================================
-- INDEXES for Performance
-- ============================================================================
CREATE INDEX idx_course_instances_course_id ON course_instances(course_id);
CREATE INDEX idx_course_instances_instructor_id ON course_instances(instructor_id);
CREATE INDEX idx_course_instances_student_group_id ON course_instances(student_group_id);
CREATE INDEX idx_course_instances_parallelizable_id ON course_instances(parallelizable_id);
CREATE INDEX idx_student_group_hierarchy_parent ON student_group_hierarchy(parent_id);
CREATE INDEX idx_student_group_hierarchy_child ON student_group_hierarchy(child_id);
CREATE INDEX idx_timetable_entries_schedule_id ON timetable_entries(schedule_id);
CREATE INDEX idx_timetable_entries_day_slot ON timetable_entries(day_of_week, time_slot);
```

### 2.2 Comparison with Current Backend Models

| Aspect | test_data.py | Current Backend | New Design |
|--------|--------------|-----------------|-----------|
| **Instructor** | ✓ Simple | ✓ Has Professor | ✓ Dedicated table |
| **Room** | ✓ With coordinates | ✓ Basic | ✓ Enhanced |
| **StudentGroup** | ✓ Hierarchical | ✗ Flat only | ✓ Hierarchy table |
| **Course** | ✓ Base template | ✗ Missing | ✓ New table |
| **CourseInstance** | ✓ Complex | △ Incomplete | ✓ Complete |
| **parallelizable_id** | ✓ Elective grouping | ✗ Missing | ✓ Added |
| **lecture_consecutive** | ✓ Scheduling rule | ✗ Missing | ✓ Added |
| **Time slots config** | ✓ Dict per day | ✗ Missing | ✓ New table |
| **Hierarchy support** | ✓ Multiple parents | ✗ Single parent | ✓ Many-to-many |

---

## PART 3: PROBLEMS WITH RESTRUCTURING EXISTING DB

### 3.1 Potential Issues

1. **Data Loss Risk**
   - Current `CourseRequirement` table conflates course and instance data
   - New design separates `Course` (template) from `CourseInstance` (session)
   - Need migration to extract course data

2. **StudentGroup Hierarchy**
   - Current model has NO hierarchy support
   - New design requires `student_group_hierarchy` table
   - Existing flat `StudentGroup` records need to be re-engineered

3. **Missing Fields**
   - `parallelizable_id` - new constraint feature
   - `lecture_consecutive` - new scheduling rule
   - `course_credits` - dynamic field
   - These need to be added with default values for existing data

4. **Room Coordinates**
   - Current schema has (x, y, z) but called differently
   - New schema standardizes them
   - No breaking change, just normalization

5. **Seed Data Files**
   - Current CSVs (courses.csv, faculties.csv, rooms.csv) need restructuring
   - Need to create student_group hierarchy data
   - Need to add missing fields with sensible defaults

### 3.2 Migration Strategy

```
Phase 1: Backup existing data
Phase 2: Create new tables
Phase 3: Migrate existing data:
  - Copy rooms as-is (add default coordinates if missing)
  - Copy instructors (from faculties.csv)
  - Create Course records from course metadata
  - Create StudentGroup hierarchy (partially from existing, needs manual completion)
  - Create CourseInstance records from CourseRequirement
  - Add default values for new fields
Phase 4: Verify data integrity
Phase 5: Drop old CourseRequirement table (or keep as archive)
```

---

## PART 4: NEXT STEPS (WHAT WILL BE PROVIDED)

1. **models.py enhancement** - Update Flask-SQLAlchemy models with new schema
2. **data_loader.py** - Preprocessing file to load DB data into test_data.py classes
3. **migration.py** - Alembic migration script for database restructuring
4. **seed_data_converter.py** - Convert existing CSV files to new schema


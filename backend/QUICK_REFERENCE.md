# Quick Reference: New Database Schema

## Key Tables

| Table | Purpose | Key Fields |
|-------|---------|-----------|
| `courses` | Base course metadata | `course_id`, `name`, `total_credits`, `lectures/tutorials/practicals_per_week` |
| `course_instances` ⭐ | Sessions to schedule | `course_id`, `session_type`, `instructor_id`, `room_id`, `student_group_id`, `parallelizable_id` |
| `student_groups` | Student cohorts | `name`, `size`, `level`, `parent_groups` (many-to-many) |
| `professors` | Faculty | `id`, `name`, `email` |
| `rooms` | Classrooms/labs | `name`, `capacity`, `is_lab`, `location_x/y/z` |
| `timetable_entries` | Schedule entries | `schedule_id`, `course_instance_id`, `day_of_week`, `time_slot` |
| `schedules` | Generated solutions | `name`, `fitness_score`, `is_active` |

---

## Common Queries

### Get all courses for an instructor
```python
CourseInstance.query.filter_by(instructor_id=prof_id).all()
```

### Get schedule for a student group
```python
TimetableEntry.query.filter_by(
    student_group_id=group_id,
    schedule_id=schedule_id
).all()
```

### Check for elective conflicts (same parallelizable_id)
```python
conflicts = CourseInstance.query.filter_by(parallelizable_id=1).all()
# If 2+ instances in same time slot → conflict
```

### Get student group hierarchy
```python
group = StudentGroup.query.get(group_id)
parents = group.parent_groups  # List of parent groups
children = group.child_groups  # List of child groups
```

---

## Database Migration

### Apply Migration
```bash
cd backend
flask db upgrade
```

### Rollback Migration
```bash
flask db downgrade
```

### Check Migration Status
```bash
flask db current
flask db heads
```

---

## Data Loading (for tests/GA)

```python
from app import create_app, db
from app.data_loader import DataLoader

app = create_app()
with app.app_context():
    test_data = DataLoader.load_from_database(db.session)
    
    instructors = test_data['instructors']
    rooms = test_data['rooms']
    student_groups = test_data['student_groups']
    courses = test_data['courses']  # CourseInstance objects
```

---

## Field Mapping: Old → New

| Old | New | Table |
|-----|-----|-------|
| `CourseRequirement` | `CourseInstance` | – |
| `course_code` | `course_id` (FK to courses) | course_instances |
| `professor_id` | `instructor_id` | course_instances |
| `slots_required` | `slots_required` | course_instances |
| N/A | `parallelizable_id` | course_instances ⭐ |
| N/A | `lecture_consecutive` | course_instances ⭐ |
| TimetableEntry.`day` | TimetableEntry.`day_of_week` | timetable_entries |
| Room.`x/y/z` | Room.`location_x/y/z` | rooms |
| N/A | StudentGroup.`level` | student_groups |
| N/A | StudentGroup.`parent_groups` | student_groups + hierarchy table |

---

## Service Files

### Use NEW services (after migration):
```python
# OLD (deprecated):
from app.services.ingestion_service import IngestionService
from app.services.ga_service import GAService
from app.services.preference_service import PreferenceService
from app.services.timetable_service import TimetableService

# NEW:
from app.services.ingestion_service_new import IngestionService
from app.services.ga_service_new import GAService
from app.services.preference_service_new import PreferenceService
from app.services.timetable_service_new import TimetableService
```

---

## Key Constraints

### Student Group Hierarchy
- Many-to-many via `student_group_hierarchy` table
- Each group can have multiple parents
- Example: RL_Elective_2025 → [CSE_RL_NLP_Track, CSE_2025, Class_2025]

### Elective Grouping
- Same `parallelizable_id` = same track (mutually exclusive)
- Different `parallelizable_id` = different tracks (can run parallel)
- Used to enforce: "RL and NL can't be scheduled at same time"

### Scheduling Rules
- `slots_continuous`: If True, slots must be consecutive
- `lecture_consecutive`: If False, max 1 lecture per day for same group
- `preference_bin`: 1=morning, 2=noon, 3=evening

---

## Performance Tips

1. **Use indexes for filtering:**
   ```python
   # FAST (uses index)
   CourseInstance.query.filter_by(parallelizable_id=1).all()
   
   # SLOW (no index)
   CourseInstance.query.filter_by(course_credits=3.0).all()
   ```

2. **Eager load relationships:**
   ```python
   # FAST (joinedload)
   from sqlalchemy.orm import joinedload
   instances = CourseInstance.query.options(joinedload('room')).all()
   
   # SLOW (N+1 queries)
   instances = CourseInstance.query.all()
   for i in instances:
       room = i.room
   ```

3. **Filter hierarchies efficiently:**
   ```python
   # Get all children of a group
   group = StudentGroup.query.get(group_id)
   children = group.child_groups  # Direct relationship
   ```

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Migration fails | Run downgrade first: `flask db downgrade` |
| No course_instances data | Check migration completed and data migrated from course_requirements |
| Student group hierarchy missing | Verify `student_group_hierarchy` table has entries |
| GA algorithm fails | Update GA service imports to use `*_new.py` files |
| Data loader returns empty | Check all foreign key references are correct |
| Room coordinates incorrect | They were renamed: `x→location_x`, `y→location_y`, `z→location_z` |

---

## Documentation References

- **Full Schema Design:** [DATABASE_DESIGN.md](./DATABASE_DESIGN.md)
- **Migration Steps:** [MIGRATION_GUIDE.md](./MIGRATION_GUIDE.md)
- **Implementation Details:** [IMPLEMENTATION_SUMMARY.md](./IMPLEMENTATION_SUMMARY.md)
- **ORM Models:** [app/models.py](./app/models.py)
- **Data Loader:** [app/data_loader.py](./app/data_loader.py)
- **Migration Script:** [migrations/versions/002_implement_new_schema.py](./migrations/versions/002_implement_new_schema.py)


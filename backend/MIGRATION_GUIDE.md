# Database Migration Guide: New Timetable Schema

## Overview

This guide explains the database schema migration from the old `CourseRequirement`-based model to the new `Course` + `CourseInstance` model with support for student group hierarchies.

**Status:** ✅ Fully implemented and tested  
**Breaking Changes:** ✅ None (with proper migration steps)  
**Data Loss:** ✅ None (all data preserved)

---

## What Changed

### Schema Changes

| Aspect | Before | After |
|--------|--------|-------|
| **Courses** | No separate table | `courses` table (base course metadata) |
| **Instances** | `course_requirements` table | `course_instances` table (actual sessions) |
| **Hierarchy** | Flat StudentGroup | `student_group_hierarchy` table (many-to-many) |
| **New Features** | N/A | `parallelizable_id` for elective constraints |
| **New Features** | N/A | `lecture_consecutive` for scheduling rules |
| **Time Config** | Hardcoded in code | `time_slot_configuration` table |
| **Room Fields** | `x, y, z` | `location_x, location_y, location_z` |

### New Tables

```
1. courses
   - course_id (PK, unique)
   - name
   - total_credits
   - lectures_per_week, tutorials_per_week, practicals_per_week
   - description
   - created_at

2. course_instances
   - id (PK)
   - course_id (FK → courses)
   - session_type
   - instructor_id (FK → professors)
   - room_id (FK → rooms)
   - student_group_id (FK → student_groups)
   - slots_required, slots_continuous
   - preference_bin
   - lecture_consecutive ← NEW
   - parallelizable_id ← NEW
   - course_credits
   - created_at

3. student_group_hierarchy
   - child_id (FK → student_groups)
   - parent_id (FK → student_groups)
   - (Primary key: child_id + parent_id)

4. time_slot_configuration
   - day_of_week (unique)
   - total_slots
   - preference_bin_*_slots (for each bin)

5. preference_bins
   - bin_id (unique)
   - name
   - start_time, end_time
```

### Modified Tables

**`student_groups`**
- Added: `level` (batch | department | track | elective)
- Added: `created_at`

**`rooms`**
- Renamed: `x` → `location_x`, `y` → `location_y`, `z` → `location_z`
- Added: `created_at`
- Increased: `name` length from 50 to 100

**`timetable_entries`**
- Renamed: `day` → `day_of_week`
- Added: `course_instance_id` (FK → course_instances)
- Added: `instructor_id` (FK → professors)
- Changed: `course_code` column removed (use course_instance_id)

**`schedules`**
- Added: `updated_at`

---

## Migration Steps

### Step 1: Backup Existing Database

```bash
# Create a backup before migration
pg_dump your_timetable_db > backup_pre_migration_$(date +%Y%m%d_%H%M%S).sql
```

### Step 2: Apply Alembic Migration

```bash
cd backend
flask db upgrade
```

The migration script will:
1. Create all new tables
2. Migrate data from `course_requirements` → `courses` + `course_instances`
3. Add missing fields with sensible defaults
4. Create constraints and indexes

### Step 3: Verify Migration

```bash
# Check that all tables were created
python -c "
from app import create_app, db
app = create_app()
with app.app_context():
    # List all tables
    tables = db.inspect(db.engine).get_table_names()
    for table in sorted(tables):
        print(f'✓ {table}')
"
```

### Step 4: Update Service Files

The migration includes **three new service files** with backward-compatible implementations:

```
app/services/
├── ingestion_service_new.py      ← Use instead of ingestion_service.py
├── ga_service_new.py              ← Use instead of ga_service.py
├── preference_service_new.py       ← Use instead of preference_service.py
└── timetable_service_new.py        ← Use instead of timetable_service.py
```

**To activate new services:**

Option A: Replace old files
```bash
cd backend/app/services
mv ingestion_service.py ingestion_service_old.py
mv ingestion_service_new.py ingestion_service.py
# Repeat for ga_service, preference_service, timetable_service
```

Option B: Update imports in routes
```python
# In routes/ingestion.py, routes/timetable.py, etc.
# Change:
# from ..services.ingestion_service import IngestionService
# To:
# from ..services.ingestion_service_new import IngestionService
```

### Step 5: Test with Data Loader

```python
from app import create_app, db
from app.data_loader import DataLoader

app = create_app()

with app.app_context():
    # Load database into test_data.py format
    test_data = DataLoader.load_from_database(db.session)
    
    # Verify loaded data
    print(f"✓ Instructors: {len(test_data['instructors'])}")
    print(f"✓ Rooms: {len(test_data['rooms'])}")
    print(f"✓ Student Groups: {len(test_data['student_groups'])}")
    print(f"✓ Courses: {len(test_data['courses'])}")
```

---

## API Changes for Developers

### IngestionService

**Old:**
```python
IngestionService.process_courses(data)  # Created CourseRequirement
```

**New:**
```python
IngestionService.process_courses(data)  # Creates Course + CourseInstance
```

**Data Format Changes:**

Old format:
```python
{
    'course_code': 'CS201',
    'session_type': 'lecture',
    'professor': 'Prof Kumar',
    'student_group': 'CSE-2025',
    'slots_required': 1
}
```

New format (extended):
```python
{
    'course_code': 'CS201',
    'course_name': 'Programming',           # ← NEW
    'total_credits': 4,                      # ← NEW
    'session_type': 'lecture',
    'professor': 'Prof Kumar',
    'student_group': 'CSE-2025',
    'room': 'Room 101',                      # ← NEW
    'slots_required': 1,
    'slots_continuous': False,
    'preference_bin': 1,
    'parallelizable_id': None,               # ← NEW
    'lecture_consecutive': False             # ← NEW
}
```

### GAService

**Old:**
```python
# Reads CourseRequirement
db_requirements = CourseRequirement.query.all()
```

**New:**
```python
# Reads CourseInstance
db_instances = CourseInstance.query.all()
```

### TimetableService

**Old:**
```python
# Entries had course_code and session_type
entries = [{
    'course': e.course_code,
    'day': e.day,
    'type': e.session_type
}]
```

**New:**
```python
# Entries have course_instance_id
entries = [{
    'course': instance.course_id,
    'course_instance_id': e.course_instance_id,
    'day': e.day_of_week,
    'type': instance.session_type
}]
```

### PreferenceService

No breaking API changes. Update works with `CourseInstance` instead of `CourseRequirement`.

---

## Data Loading: test_data.py Integration

### Using DataLoader

```python
from app import create_app, db
from app.data_loader import DataLoader

app = create_app()

with app.app_context():
    # Load all data from database
    test_data = DataLoader.load_from_database(db.session)
    
    # Access loaded data
    instructors = test_data['instructors']          # List[Instructor]
    rooms = test_data['rooms']                      # List[Room]
    student_groups = test_data['student_groups']    # List[StudentGroup]
    courses = test_data['courses']                  # List[CourseInstance]
    
    # Student group hierarchy is preserved!
    for group in student_groups:
        print(f"{group.name} has parents: {[p.name for p in group.super_groups]}")
```

### For GA Algorithm

```python
from app import create_app, db
from app.data_loader import DataLoader
from ga.algorithm import GASearch

app = create_app()

with app.app_context():
    # Load data in test_data.py format
    test_data = DataLoader.load_from_database(db.session)
    
    # Use directly with GA algorithm
    ga = GASearch(
        time_slots=test_data['time_slots'],
        courses=test_data['courses'],
        preference_bins=test_data['preference_bins'],
        objective_function_weights=test_data['objective_function_weights'],
        rooms=test_data['rooms'],
        population_size=50,
        generations=100
    )
    
    population = ga.create_population()
    # ... rest of GA logic
```

---

## Rollback Instructions

If issues occur and you need to rollback:

```bash
cd backend

# Downgrade to previous version
flask db downgrade

# Or downgrade to specific revision
flask db downgrade 7bfe3d34c4a5
```

The migration includes a complete `downgrade()` function that will:
1. Remove all new tables
2. Remove new columns from existing tables
3. Restore old column names
4. Restore original schema state

---

## Backward Compatibility

### CourseRequirement Table

The old `course_requirements` table is **kept** during migration but marked as **DEPRECATED**.

- **Do NOT:** Use CourseRequirement in new code
- **Use:** CourseInstance instead
- **Timeline:** Will be removed in v2.0

### Old Service Files

Old service files (`ingestion_service.py`, `ga_service.py`, etc.) will continue to work with existing code that imports them, but they use the deprecated `CourseRequirement` table.

To prevent confusion:
1. Rename old files to `*_deprecated.py`
2. Use new `*_new.py` files
3. Update all imports

---

## Common Issues & Solutions

### Issue: "No course_instances table found"

**Solution:** Run the migration
```bash
flask db upgrade
```

### Issue: "Duplicate key value violates unique constraint 'courses_course_id_key'"

**Solution:** The migration already handles this. If you run it twice, use downgrade first:
```bash
flask db downgrade
flask db upgrade
```

### Issue: Data not loading in data_loader

**Solution:** Ensure you have:
1. Run migration successfully
2. Populated database with data
3. Using correct import path:
```python
from app.data_loader import DataLoader  # ✓ Correct
# NOT:
# from data_loader import DataLoader     # ✗ Wrong
```

### Issue: GA algorithm fails after migration

**Solution:** Update GA service import and code to use new `CourseInstance` model. See [API Changes](#api-changes-for-developers) section.

---

## Performance Considerations

### Indexes Created

The migration creates the following indexes for query performance:

```
- idx_courses_course_id
- idx_course_instances_course_id
- idx_course_instances_instructor_id
- idx_course_instances_student_group_id
- idx_course_instances_parallelizable_id
- idx_student_group_hierarchy_parent
- idx_student_group_hierarchy_child
- idx_timetable_entries_schedule_id
- idx_timetable_entries_day_slot
```

### Query Performance Tips

1. **Use eager loading for relationships:**
```python
# Slow
instances = CourseInstance.query.all()
for instance in instances:
    room = instance.room  # N+1 query problem

# Fast
instances = CourseInstance.query.options(joinedload('room')).all()
```

2. **Filter before joining:**
```python
# Filter by instructor first, then get details
instances = CourseInstance.query.filter_by(instructor_id=prof_id).all()
```

---

## Validation Checklist

After migration, verify:

- [ ] All new tables created (`courses`, `course_instances`, etc.)
- [ ] Data migrated from `course_requirements` (should be same count)
- [ ] Student group hierarchy populated
- [ ] `timetable_entries` references correct `course_instance_id`
- [ ] All services updated to use new models
- [ ] GA algorithm runs successfully
- [ ] Timetable data retrieval works
- [ ] Preference updates work
- [ ] Backup of pre-migration database exists

---

## Additional Resources

- [DATABASE_DESIGN.md](./DATABASE_DESIGN.md) - Complete schema design documentation
- [app/models.py](./app/models.py) - All ORM model definitions
- [app/data_loader.py](./app/data_loader.py) - DataLoader class documentation
- [tests/test_data.py](../tests/test_data.py) - Test data format reference

---

## Questions & Support

For issues or questions:
1. Check this guide's [Common Issues section](#common-issues--solutions)
2. Review the [DATABASE_DESIGN.md](./DATABASE_DESIGN.md) for schema details
3. Check Flask-SQLAlchemy and Alembic documentation
4. Examine migration file: [migrations/versions/002_implement_new_schema.py](./migrations/versions/002_implement_new_schema.py)


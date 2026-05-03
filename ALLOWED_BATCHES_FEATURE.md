# Room Batch Restrictions (allowed_batches Feature)

## Overview

The `allowed_batches` attribute on rooms allows you to restrict which student batches/groups can be scheduled in specific rooms. This is useful for:
- **Specialized labs**: CS Lab only for CS/AI students
- **Civil Engineering labs**: Only for Civil Engineering students  
- **Department-specific facilities**: Restricting facilities to specific departments/batches

## How It Works

### When `allowed_batches` is `None` (default)
- All student groups are allowed to be scheduled in this room
- This is the default behavior for backward compatibility

### When `allowed_batches` is a list
- Only student groups whose names are in the list can be scheduled in this room
- Example: `["CS1", "CS2", "AI1", "AI2"]` means only these four groups can use the room

## Implementation Details

### 1. Database Schema
- Added `allowed_batches` JSON column to `rooms` table (nullable)
- Migration: `backend/migrations/versions/add_allowed_batches_to_rooms.py`

### 2. GA Algorithm Constraints
The constraint is enforced at three levels:

**In `ga/constraints.py`:**
- **`_get_available_rooms(course)`**: Filters out rooms where the student group is not in `allowed_batches`
- **`_can_add_course()`**: Validates batch restrictions during slot assignment
- **`check_constraints()`**: Final validation with constraint 5b checking batch restrictions

### 3. Smart Initialization
- **Enhanced logging** in `schema/genetic_algorithm.py` shows when rooms are filtered due to batch restrictions
- Debug output includes count of rooms excluded by batch restrictions

### 4. Data Ingestion
- **`backend/app/services/ingestion_service.py`**: Reads `allowed_batches` from seed data
- **`backend/app/data_loader.py`**: Loads `allowed_batches` from database into Room objects

### 5. API Endpoints
- **`GET /timetable/rooms`**: Returns simple list of room names (backward compatible)
- **`GET /timetable/rooms?detailed=true`**: Returns detailed room info including `allowed_batches`

## Configuration Examples

### In seed_data.json
```json
{
  "rooms": [
    {
      "name": "CS Lab",
      "allowed_batches": ["CS1", "CS2", "CS3", "CS4", "AI1", "AI2", "AI3", "AI4"]
    },
    {
      "name": "Lecture Hall 1"
      // No allowed_batches means all groups can use it
    }
  ]
}
```

### In CSV file (rooms.csv)
```csv
name,is_lab,capacity,x,y,z,allowed_batches
CS Lab,true,60,10.0,5.0,0.0,"[""CS1"",""CS2"",""CS3"",""CS4"",""AI1"",""AI2"",""AI3"",""AI4""]"
Lecture Hall,false,150,0.0,0.0,0.0,
```

## Preprocessing from Database

The `schema/preprocessor.py` script automatically loads `allowed_batches` from the database when fetching GA inputs:
```python
cursor.execute("SELECT id, name, is_lab, capacity, allowed_batches FROM rooms ORDER BY id;")
# allowed_batches is loaded as-is from the JSON column
```

## Constraint Violation Examples

When the GA algorithm tries to schedule:
- **CS1 lecture in Civil Engineering Lab** (which has `allowed_batches: ["Civil1", "Civil2"]`) → **REJECTED**
- **CS1 lab in CS Lab** (which has `allowed_batches: ["CS1", "CS2", ...]`) → **ACCEPTED**

## Logging Output

During smart initialization, you'll see:
```
[INIT] Scheduling CS1-lecture (slots needed: 2)
[ROOMS] 12 suitable room(s) available
// OR if batch restrictions filter rooms:
[FAIL] No suitable rooms available
       Batch restrictions exclude 3 room(s) for CS1
```

## Schema Class Definition

```python
class Room:
    def __init__(self, id, name, is_lab=False, capacity=100, x=0.0, y=0.0, z=0.0, allowed_batches=None):
        self.allowed_batches = allowed_batches  # None = all batches allowed
```

## Migration Steps

If upgrading from existing database:

```bash
# Apply migration
cd backend
alembic upgrade add_allowed_batches

# Verify column exists
psql -d timetable_db -c "SELECT column_name FROM information_schema.columns WHERE table_name='rooms';"
```

## Testing

Run the smart initialization with a course that belongs to a restricted group:
```python
# Should see batch restriction logging and proper constraint validation
population = ga_search.create_population()
```

Check constraint validation explicitly:
```python
constraint_check = ga_search.check_constraints(time_table, verbose=True)
```

---

**Summary of Changes:**
- ✅ Schema: `allowed_batches` JSON column added to rooms table
- ✅ GA Constraints: Three-level validation (available rooms filtering, can_add validation, final constraint check)
- ✅ Smart Initialization: Enhanced logging showing batch restriction filtering
- ✅ Data Loader: Loads `allowed_batches` from database
- ✅ Ingestion Service: Ingests `allowed_batches` from seed data and CSV
- ✅ API: Enhanced `/rooms` endpoint with optional detailed view
- ✅ Templates: Updated rooms.csv with allowed_batches column example

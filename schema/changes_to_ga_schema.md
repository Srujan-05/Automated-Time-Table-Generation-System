# GA and Preprocessing Change Log (Schema Scope)

This document explains all relevant code changes made in the schema folder for GA execution, preprocessing, and data seeding.

## Baseline and scope

- Baseline reference (outside schema): ../genetic_algorithm.py
- Change scope for this work: schema/* only
- Root file ../genetic_algorithm.py was not edited.

## 1) GA change: schema/genetic_algorithm.py

### What changed
In _assign_non_continuous_slots, a lecture-day guard was added so one lecture instance for a given course-group is assigned at most once per day before moving to the next day.

### Code-level delta
- Added per-day flag: lecture_assigned_today = False
- After assigning a lecture slot:
  - set lecture_assigned_today = True
  - break out of the day slot loop
- After slot loop:
  - if lecture_assigned_today: continue

### Why this change was needed
Schedules were showing clustering behavior where lectures could stack too heavily on one day. This guard pushes non-continuous lecture instances to spread across Monday-Friday.

### Comparison vs ../genetic_algorithm.py
- Root baseline does not include this guard.
- Schema version includes this guard.

## 2) GA change: schema/genetic_algorithm_improved.py

### What changed
Copied course instances now preserve stable logical IDs when setting _orig_id.

### Code-level delta
In both assignment methods:
- _assign_continuous_slots_simple
- _assign_non_continuous_slots_simple

Old:
- course_copy._orig_id = getattr(course, '_orig_id', id(course))

New:
- course_copy._orig_id = getattr(course, '_orig_id', getattr(course, 'id', id(course)))

### Why this change was needed
Preprocessing now generates stable per-instance IDs on CourseInstance objects. Improved GA must keep those IDs in copied timetable entries so slot-count validation compares the same logical instances.

Without this fix, improved GA could repeatedly fail with wrong slot count errors during population validation.

### Comparison vs ../genetic_algorithm.py
- There is no improved GA counterpart in root for direct line-by-line comparison.
- Functionally, this change aligns improved GA with the new preprocessing ID model.

## 3) Preprocessing change: schema/classes.py

### What changed
CourseInstance constructor now supports a stable explicit instance ID.

### Code-level delta
Old constructor behavior:
- self.id = id(self)

New constructor behavior:
- new parameter: instance_id=None
- self.id = instance_id if instance_id is not None else id(self)

### Why this change was needed
Python object identity is not a reliable domain identifier when objects are copied during scheduling. Stable IDs are required for robust constraint accounting across preprocessing, scheduling, and validation.

## 4) Preprocessing change: schema/preprocessor.py

### What changed
Course requirement rows are transformed differently based on continuity requirements, and student groups are returned as a first-class output.

### Code-level delta
For each course_requirements row:
- If slots_continuous is True:
  - create one CourseInstance with slots_req = slots_required
  - assign stable id instance_id = f"{req_id}_0"
- If slots_continuous is False:
  - expand into N CourseInstance objects (N = slots_required)
  - each instance has slots_req = 1
  - each gets stable id instance_id = f"{req_id}_{slot_idx}"

Return signature changed:
- Old: return rooms, courses
- New: return rooms, courses, student_groups

Main/test summary output was adjusted to reflect expanded course instances.

### Why this change was needed
The GA constraint checker works best when non-continuous hours are represented as separate 1-slot instances. Continuous sessions must remain blocks to preserve adjacency requirements. Returning student_groups also improves downstream visibility and debugging.

## 5) Data seeding change: schema/db_setup.py

### What changed
Added missing professor names referenced by course requirements and added insertion visibility.

### Code-level delta
Added professors_data entries:
- Dr. Palash
- Dr. Prasad
- Dr. nartakannai

Added insertion tracking:
- inserted_course_rows counter using cursor.rowcount
- warning output when inserted rows are fewer than configured course_reqs rows

### Why this change was needed
Previously, some course requirements silently failed to insert because professor names were absent in professors_data. This created hidden data loss before preprocessing. The warning now surfaces mapping/insert issues immediately.

## 6) Caller compatibility updates

### What changed
Updated GA runner call sites to match new preprocessor return signature.

Files:
- schema/test/run_ga.py
- schema/test/run_ga_improved.py

Delta:
- Old: rooms, courses = get_ga_inputs()
- New: rooms, courses, student_groups = get_ga_inputs()

### Why this change was needed
Without caller updates, runtime unpacking would fail after preprocessor return signature change.

## 7) Validation and runtime outcome

### Compile validation
Python compile checks were run for touched schema files; no compile errors were found.

### Runtime validation
- schema/db_setup.py reseed completed successfully.
- schema/test/run_ga.py completed and saved schedule rows.
- schema/test/run_ga_improved.py initially failed before _orig_id fix, then completed and saved schedule rows after the fix.

### Database reflection
Changes are reflected in PostgreSQL tables used by pgAdmin (including generated_schedules rows from both base and improved runs).

## 8) Why this set of changes matters for collaborators

These updates keep preprocessing, GA assignment, and constraint checking logically consistent:
- Stable IDs prevent copy-related identity bugs.
- Non-continuous expansion matches GA slot accounting.
- Continuous sessions still honor block scheduling semantics.
- Seeding transparency prevents silent data drops.
- Runner updates keep execution entry points aligned.

Together, these make the workflow reproducible and easier to reason about for anyone pulling the branch.

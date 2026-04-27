import json

def test_auth_and_roles(client):
    # Test Student Signup (contains digits)
    res = client.post('/api/auth/signup', json={
        "email": "se23ucse010@mahindrauniversity.edu.in",
        "password": "password"
    })
    assert res.status_code == 201
    assert res.get_json()['role'] == 'STUDENT'

    # Test Faculty Signup (no digits)
    res = client.post('/api/auth/signup', json={
        "email": "john.doe@mahindrauniversity.edu.in",
        "password": "password"
    })
    assert res.status_code == 201
    assert res.get_json()['role'] == 'FACULTY'

def test_ingestion_seed(client, auth_tokens):
    # Admin seed data
    headers = {"Authorization": f"Bearer {auth_tokens['admin']}"}
    res = client.post('/api/ingestion/seed', headers=headers)
    assert res.status_code in [200, 201] # Already seeded is fine

def test_faculty_shift_update(client, auth_tokens):
    # Update shift
    headers = {"Authorization": f"Bearer {auth_tokens['faculty']}"}
    # Avinash Chauhan is a faculty in seed data
    res = client.post('/api/preferences/shift', headers=headers, json={"bin_id": 2})        
    assert res.status_code == 200
    assert "Updated preferences" in res.get_json()['msg']

def test_student_timetable_filtering(client, auth_tokens):
    from app.models import db, Schedule, TimetableEntry, Room, Professor, StudentGroup
    
    with client.application.app_context():
        # Create a schedule
        sched = Schedule(name="Test Sched", is_active=True)
        db.session.add(sched)
        db.session.flush()
        
        room = Room.query.first()
        prof = Professor.query.first()
        group = StudentGroup.query.filter_by(name="CS2").first()
        
        entry = TimetableEntry(
            schedule_id=sched.id,
            day="Monday",
            time_slot=1,
            course_code="CS101",
            room_id=room.id,
            professor_id=prof.id,
            student_group_id=group.id,
            session_type="lecture"
        )
        db.session.add(entry)
        db.session.commit()

    # Get timetable as student (se23ucse150 -> CS2)
    headers = {"Authorization": f"Bearer {auth_tokens['student']}"}
    res = client.get('/api/timetable', headers=headers)
    assert res.status_code == 200
    data = res.get_json()
    assert len(data) == 1
    assert data[0]['group'] == "CS2"

def test_admin_access_only(client, auth_tokens):
    # Try to seed as student
    headers = {"Authorization": f"Bearer {auth_tokens['student']}"}
    res = client.post('/api/ingestion/seed', headers=headers)
    assert res.status_code == 403

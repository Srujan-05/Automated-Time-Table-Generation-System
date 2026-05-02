"""
Instructor Preference Service: Manages faculty time slot availability preferences.
"""
from ..models import db, Professor, CourseInstance

class PreferenceService:
    @staticmethod
    def get_all_faculty_profiles():
        """Returns a list of all instructors for administration."""
        professors = Professor.query.all()
        return [{"id": p.id, "name": p.name, "email": p.email} for p in professors]

    @staticmethod
    def fetch_instructor_preference(professor_id=None, user_id=None, email=None):
        """Retrieves the preferred time slot bin for a specific instructor."""
        if professor_id:
            professor = Professor.query.get(professor_id)
        elif user_id:
            professor = Professor.query.filter_by(user_id=user_id).first()
        else:
            professor = Professor.query.filter_by(email=email).first()
            
        if not professor:
            raise ValueError("Instructor record not found")
        
        # Preferences are stored at the instance level in the new schema
        instances = CourseInstance.query.filter_by(instructor_id=professor.id).all()
        if not instances:
            return 1 # Default to Morning (Bin 1)
        
        # Return the preference of the first linked instance
        return instances[0].preference_bin

    @staticmethod
    def update_instructor_shift_preference(bin_id, professor_id=None, user_id=None, email=None):
        """Updates the preference bin for all course instances taught by an instructor."""
        if professor_id:
            professor = Professor.query.get(professor_id)
        elif user_id:
            professor = Professor.query.filter_by(user_id=user_id).first()
        else:
            professor = Professor.query.filter_by(email=email).first()
            
        if not professor:
            raise ValueError("Instructor record not found")
        
        # Update all instances assigned to this professor
        instances = CourseInstance.query.filter_by(instructor_id=professor.id).all()
        for instance in instances:
            instance.preference_bin = bin_id
        
        db.session.commit()
        return len(instances)

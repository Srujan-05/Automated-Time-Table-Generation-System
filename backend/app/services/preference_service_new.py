"""
Updated Preference Service to use new CourseInstance schema
"""
from ..models import db, CourseInstance, Professor

class PreferenceService:
    @staticmethod
    def list_professors():
        """Get list of all professors"""
        profs = Professor.query.all()
        return [{"id": p.id, "name": p.name, "email": p.email} for p in profs]

    @staticmethod
    def get_professor_preference(professor_id=None, user_id=None, email=None):
        """Get preference bin for a professor"""
        if professor_id:
            prof = Professor.query.get(professor_id)
        elif user_id:
            prof = Professor.query.filter_by(user_id=user_id).first()
        else:
            prof = Professor.query.filter_by(email=email).first()
            
        if not prof:
            return 1  # Default to morning if not found
            
        # Get preference from first course instance for this professor
        instance = CourseInstance.query.filter_by(instructor_id=prof.id).first()
        return instance.preference_bin if instance else 1

    @staticmethod
    def update_professor_shift(bin_id, professor_id=None, user_id=None, email=None):
        """
        Update preference bin for all courses taught by a professor
        
        Args:
            bin_id: Preference bin (1=morning, 2=noon, 3=evening)
            professor_id: Professor ID (optional)
            user_id: User ID associated with professor (optional)
            email: Email address (optional)
            
        Returns:
            Number of course instances updated
        """
        if professor_id:
            prof = Professor.query.get(professor_id)
        elif user_id:
            prof = Professor.query.filter_by(user_id=user_id).first()
        else:
            prof = Professor.query.filter_by(email=email).first()
        
        if not prof:
            raise ValueError(f"Professor profile not found")

        # Update all course instances for this professor
        instances = CourseInstance.query.filter_by(instructor_id=prof.id).all()
        for instance in instances:
            instance.preference_bin = bin_id
        
        db.session.commit()
        return len(instances)

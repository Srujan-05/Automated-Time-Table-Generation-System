from ..models import db, CourseRequirement, Professor

class PreferenceService:
    @staticmethod
    def list_professors():
        profs = Professor.query.all()
        return [{"id": p.id, "name": p.name, "email": p.email} for p in profs]

    @staticmethod
    def get_professor_preference(professor_id=None, user_id=None, email=None):
        if professor_id:
            prof = Professor.query.get(professor_id)
        elif user_id:
            prof = Professor.query.filter_by(user_id=user_id).first()
        else:
            prof = Professor.query.filter_by(email=email).first()
            
        if not prof:
            return 1 # Default to morning if not found
            
        # Get preference from first requirement found
        req = CourseRequirement.query.filter_by(professor_id=prof.id).first()
        return req.preference_bin if req else 1

    @staticmethod
    def update_professor_shift(bin_id, professor_id=None, user_id=None, email=None):
        if professor_id:
            prof = Professor.query.get(professor_id)
        elif user_id:
            prof = Professor.query.filter_by(user_id=user_id).first()
        else:
            prof = Professor.query.filter_by(email=email).first()
        
        if not prof:
            raise ValueError(f"Professor profile not found")

        # Update all course requirements for this professor to the new preference bin
        requirements = CourseRequirement.query.filter_by(professor_id=prof.id).all()
        for req in requirements:
            req.preference_bin = bin_id
        
        db.session.commit()
        return len(requirements)

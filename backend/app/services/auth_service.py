"""
Authentication Service: Manages user roles, registration, and organizational mappings.
"""
import re
import math
from ..models import User, UserRole, Professor, StudentGroup, db
from ..core.config import Config

class AuthService:
    @staticmethod
    def identify_role_by_email(email):
        """Determines UserRole based on email prefix/identifier."""
        identifier = email.split('@')[0].lower()
        if identifier in Config.ADMIN_IDS:
            return UserRole.ADMIN
        if any(char.isdigit() for char in identifier):
            return UserRole.STUDENT
        return UserRole.FACULTY

    @staticmethod
    def identify_group_by_email(email):
        """Maps student email identifiers to specific StudentGroups."""
        identifier = email.split('@')[0].lower()
        branch_map = {
            'ucse': 'CS', 'uai': 'AI', 'uece': 'ECE', 
            'uecm': 'ECM', 'ubt': 'BT', 'uce': 'CE', 'ume': 'ME'
        }
        match = re.search(r'([a-z]+)(\d+)$', identifier)
        if not match: 
            return "CS1"
            
        branch_code, student_id = match.group(1), int(match.group(2))
        matched_branch = "CS"
        for code, name in branch_map.items():
            if code in branch_code: 
                matched_branch = name
                break
                
        group_num = math.ceil(student_id / 80) if student_id > 0 else 1
        if matched_branch in ['ECE', 'ECM', 'BT', 'CE', 'ME']: 
            return matched_branch
        return f"{matched_branch}{group_num}"

    @staticmethod
    def register_new_account(email, password):
        """Handles new user registration and links faculty to Professor records."""
        if not email.endswith(f"@{Config.ALLOWED_DOMAIN}"): 
            raise ValueError(f"Only @{Config.ALLOWED_DOMAIN} emails are allowed.")
        if User.query.filter_by(email=email).first(): 
            raise ValueError("User already exists.")
            
        role = AuthService.identify_role_by_email(email)
        user = User(email=email, role=role)
        user.set_password(password)
        db.session.add(user)
        db.session.flush()
        
        if role == UserRole.FACULTY:
            # Attempt to link user to existing Professor record
            professor = Professor.query.filter_by(email=email).first()
            if not professor:
                name_part = email.split('@')[0].replace('.', ' ').lower()
                all_professors = Professor.query.all()
                for p in all_professors:
                    clean_name = re.sub(r'^dr\.\s*', '', p.name, flags=re.IGNORECASE).lower()
                    if clean_name == name_part:
                        professor = p
                        break
            
            if professor:
                professor.user_id = user.id
                db.session.add(professor)
        
        db.session.commit()
        return user

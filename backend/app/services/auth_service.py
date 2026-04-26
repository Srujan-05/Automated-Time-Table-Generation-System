import re
import math
from ..models import User, UserRole, Professor, StudentGroup, db
from ..core.config import Config

class AuthService:
    @staticmethod
    def get_role_from_email(email):
        identifier = email.split('@')[0].lower()
        if identifier in Config.ADMIN_IDS:
            return UserRole.ADMIN
        if any(char.isdigit() for char in identifier):
            return UserRole.STUDENT
        return UserRole.FACULTY

    @staticmethod
    def get_group_from_email(email):
        identifier = email.split('@')[0].lower()
        branch_map = {'ucse': 'CS', 'uai': 'AI', 'uece': 'ECE', 'uecm': 'ECM', 'ubt': 'BT', 'uce': 'CE', 'ume': 'ME'}
        match = re.search(r'([a-z]+)(\d+)$', identifier)
        if not match: return "CS1"
        branch_code, student_id = match.group(1), int(match.group(2))
        matched_branch = "CS"
        for code, name in branch_map.items():
            if code in branch_code: matched_branch = name; break
        group_num = math.ceil(student_id / 80) if student_id > 0 else 1
        if matched_branch in ['ECE', 'ECM', 'BT', 'CE', 'ME']: return matched_branch
        return f"{matched_branch}{group_num}"

    @staticmethod
    def register_user(email, password):
        if not email.endswith(f"@{Config.ALLOWED_DOMAIN}"): raise ValueError(f"Only @{Config.ALLOWED_DOMAIN} emails are allowed.")
        if User.query.filter_by(email=email).first(): raise ValueError("User already exists.")
        role = AuthService.get_role_from_email(email)
        user = User(email=email, role=role)
        user.set_password(password)
        db.session.add(user)
        db.session.flush()
        if role == UserRole.FACULTY:
            # 1. Try direct email match
            prof = Professor.query.filter_by(email=email).first()
            
            # 2. Try normalized name match
            if not prof:
                name_part = email.split('@')[0].replace('.', ' ').lower()
                all_profs = Professor.query.all()
                for p in all_profs:
                    clean_name = re.sub(r'^dr\.\s*', '', p.name, flags=re.IGNORECASE).lower()
                    if clean_name == name_part:
                        prof = p
                        break
            
            if prof:
                prof.user_id = user.id
                db.session.add(prof) # Ensure tracked
        
        db.session.commit()
        return user

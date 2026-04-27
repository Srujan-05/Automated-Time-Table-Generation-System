import os
from datetime import timedelta

class Config:
    # Use a stronger secret key for production security
    SECRET_KEY = os.environ.get('SECRET_KEY', 'automated-timetable-system-secure-key-2026-mu')
    
    # Database Configuration: 'sqlite' or 'postgres'
    DB_TYPE = os.environ.get('DB_TYPE', 'sqlite').lower()
    
    if DB_TYPE == 'postgres':
        url = os.environ.get('DATABASE_URL')
        if url and url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql://", 1)
        SQLALCHEMY_DATABASE_URI = url
    else:
        SQLALCHEMY_DATABASE_URI = os.environ.get('SQLITE_URL', 'sqlite:///instance/timetable.db')

    if not SQLALCHEMY_DATABASE_URI:
        # Final safety fallback
        SQLALCHEMY_DATABASE_URI = 'sqlite:///instance/timetable.db'
    
    print(f" * Using Database: {'PostgreSQL' if 'postgresql' in SQLALCHEMY_DATABASE_URI else 'SQLite'}")

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Stronger JWT secret key
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'jwt-mahindra-university-timetable-authorization-secret')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=2)
    
    # Mahindra University Domain
    ALLOWED_DOMAIN = "mahindrauniversity.edu.in"
    
    # Hardcoded Admins
    ADMIN_IDS = ["se23ucse020", "se23ucse080", "se23ucse150", "se23ucse171", "se23ucse014", "se23ucse055", "se23ucse223"]

import os
from pathlib import Path
from datetime import timedelta

BASE_DIR = Path(__file__).resolve().parent.parent.parent

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'atgs-secret-2026')
    DB_TYPE = os.environ.get('DB_TYPE', 'sqlite').lower()
    
    if DB_TYPE == 'postgres':
        url = os.environ.get('DATABASE_URL')
        if url and url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql://", 1)
        SQLALCHEMY_DATABASE_URI = url
    else:
        db_raw = os.environ.get('SQLITE_URL', 'sqlite:///instance/timetable.db')
        db_path = db_raw.replace('sqlite:///', '')
        abs_path = (BASE_DIR / db_path).resolve().as_posix()
        Path(abs_path).parent.mkdir(parents=True, exist_ok=True)
        SQLALCHEMY_DATABASE_URI = f"sqlite:///{abs_path}"

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'jwt-secret-atgs')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=2)
    ALLOWED_DOMAIN = "mahindrauniversity.edu.in"
    ADMIN_IDS = ["se23ucse020", "se23ucse080", "se23ucse150", "se23ucse171", "se23ucse014", "se23ucse055", "se23ucse223"]

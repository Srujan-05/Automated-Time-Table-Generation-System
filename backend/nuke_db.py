import os
import argparse
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from app.extensions import db
from app.core.config import Config

# Load .env for credentials
load_dotenv()

def nuke_engine(uri, name):
    print(f"\n--- Nuking {name} ---")
    try:
        engine = create_engine(uri)
        with engine.connect() as conn:
            if "postgresql" in uri:
                conn.execute(text("DROP SCHEMA public CASCADE; CREATE SCHEMA public;"))
                conn.commit()
                print(f"  ✓ Dropped and re-created 'public' schema for {name}.")
            else:
                inspector = db.inspect(engine)
                tables = inspector.get_table_names()
                conn.execute(text("PRAGMA foreign_keys = OFF;"))
                for table in tables:
                    conn.execute(text(f"DROP TABLE IF EXISTS {table};"))
                conn.execute(text("PRAGMA foreign_keys = ON;"))
                conn.commit()
                print(f"  ✓ Dropped {len(tables)} tables from {name}.")

        from app import create_app
        app = create_app()
        app.config['SQLALCHEMY_DATABASE_URI'] = uri
        with app.app_context():
            db.create_all()
            print(f"  ✓ Re-created clean schema for {name}.")
            
    except Exception as e:
        print(f"  ✗ FAILED to nuke {name}: {e}")

def main():
    parser = argparse.ArgumentParser(description="Targeted Database Nuke Tool")
    parser.add_argument("--sqlite", action="store_true", help="Nuke only SQLite")
    parser.add_argument("--postgres", action="store_true", help="Nuke only PostgreSQL")
    parser.add_argument("--all", action="store_true", help="Nuke all configured databases")
    args = parser.parse_args()

    if not any([args.sqlite, args.postgres, args.all]):
        print("Usage: uv run python nuke_db.py [--sqlite] [--postgres] [--all]")
        print("No target specified. Please provide a parameter to run.")
        return

    sqlite_uri = Config.SQLALCHEMY_DATABASE_URI if "sqlite" in Config.SQLALCHEMY_DATABASE_URI else None
    pg_uri = os.environ.get('DATABASE_URL')
    if pg_uri and pg_uri.startswith("postgres://"):
        pg_uri = pg_uri.replace("postgres://", "postgresql://", 1)

    if args.all:
        if sqlite_uri: nuke_engine(sqlite_uri, "SQLite")
        if pg_uri: nuke_engine(pg_uri, "PostgreSQL")
    elif args.sqlite:
        if sqlite_uri: nuke_engine(sqlite_uri, "SQLite")
        else: print("✗ SQLite not configured.")
    elif args.postgres:
        if pg_uri: nuke_engine(pg_uri, "PostgreSQL")
        else: print("✗ PostgreSQL (DATABASE_URL) not found in environment.")

    print("\nReset complete.")

if __name__ == "__main__":
    main()

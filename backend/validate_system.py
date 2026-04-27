import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from app import create_app, db
from app.models import Professor, Room, StudentGroup, CourseRequirement, Schedule, TimetableEntry, User, ActivityLog
from app.services.ingestion_service import IngestionService
from app.services.ga_service import GAService

def validate():
    app = create_app()
    with app.app_context():
        print("\n" + "="*50)
        print("SYSTEM VALIDATION & STRESS TEST")
        print("="*50)

        # 1. CLEAN START
        print("\n[1/5] Resetting database...")
        db.drop_all()
        db.create_all()
        print("  ✓ Database tables recreated.")

        # 2. POPULATE DATA
        print("\n[2/5] Seeding initial data...")
        seed_path = os.path.join(app.instance_path, 'seed_data.json')
        if not os.path.exists(seed_path):
            seed_path = os.path.join(os.getcwd(), 'instance', 'seed_data.json')
        
        try:
            f, r, c = IngestionService.seed_initial_data(seed_path)
            print(f"  ✓ Seeded: {f} Professors, {r} Rooms, {c} Course Requirements.")
        except Exception as e:
            print(f"  ✗ Seeding failed: {str(e)}")
            return

        # 3. RUN GA OPTIMIZATION
        print("\n[3/5] Running Genetic Algorithm (Optimization)...")
        print("      This may take a few moments...")
        try:
            schedule = GAService.run_ga_generation("Validation Test Schedule")
            print(f"  ✓ GA Successful!")
            print(f"  ✓ Generated Schedule ID: {schedule.id}")
            print(f"  ✓ Fitness Score: {schedule.fitness_score:.4f}")
        except Exception as e:
            print(f"  ✗ GA failed to find a valid population: {str(e)}")
            return

        # 4. VERIFY ENTRIES
        print("\n[4/5] Verifying database entries...")
        entry_count = TimetableEntry.query.filter_by(schedule_id=schedule.id).count()
        if entry_count > 0:
            print(f"  ✓ System Verified: {entry_count} timetable entries successfully created and mapped.")
        else:
            print("  ✗ Verification failed: No timetable entries found in DB.")
            return

        # 5. FINAL CLEANSING
        print("\n[5/5] Performing final database cleansing...")
        try:
            # Delete all data from all tables
            TimetableEntry.query.delete()
            ActivityLog.query.delete()
            CourseRequirement.query.delete()
            Professor.query.delete()
            Room.query.delete()
            StudentGroup.query.delete()
            Schedule.query.delete()
            User.query.delete()
            db.session.commit()
            print("  ✓ All tables cleared. Database is now empty.")
        except Exception as e:
            print(f"  ✗ Cleansing failed: {str(e)}")
            return

        print("\n" + "="*50)
        print("SYSTEM VALIDATION SUCCESSFUL")
        print("All components (DB, Ingestion, GA, Models) are working perfectly.")
        print("="*50 + "\n")

if __name__ == "__main__":
    validate()

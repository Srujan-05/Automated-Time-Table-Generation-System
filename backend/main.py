from dotenv import load_dotenv
import os

load_dotenv()

from app import create_app, db

app = create_app()

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        
        # Auto-seed if database is empty
        from app.models import CourseInstance
        if CourseInstance.query.count() == 0:
            from app.services.ingestion_service import IngestionService
            seed_path = os.path.join(app.instance_path, 'seed_data.json')
            if os.path.exists(seed_path):
                print(" * Database empty. Performing automatic seed...")
                IngestionService.perform_initial_seeding(seed_path)
                print(" * Automatic seed complete.")
                
    app.run(debug=True, port=5001)

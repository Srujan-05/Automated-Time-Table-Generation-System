from dotenv import load_dotenv
import os

# Load environment variables early
load_dotenv()

from app import create_app, db

app = create_app()

if __name__ == "__main__":
    with app.app_context():
        # Only create DB if using local sqlite or if needed
        db.create_all()
    app.run(debug=True, port=5000)

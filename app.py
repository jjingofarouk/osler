
from flask import Flask
from routes.chat_routes import chat_bp
from routes.case_study_routes import case_study_bp
from routes.history_routes import history_bp  # Corrected import
import os
from dotenv import load_dotenv
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

load_dotenv()

app = Flask(__name__, template_folder='templates')
app.secret_key = os.getenv("FLASK_SECRET_KEY", "your-secret-key")

# Register blueprints
app.register_blueprint(chat_bp)
app.register_blueprint(case_study_bp)
app.register_blueprint(history_bp)  # Corrected blueprint name

if __name__ == "__main__":
    try:
        port = int(os.getenv("PORT", 5000))
        app.run(host="0.0.0.0", port=port, debug=True)
    except Exception as e:
        logger.error(f"Failed to start Flask app: {e}")
        print(f"Error starting server: {e}")
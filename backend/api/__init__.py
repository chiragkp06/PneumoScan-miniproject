from flask import Flask
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Configure the app with environment variables
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

# Import blueprints
from .auth import auth_bp
from .upload import upload_bp
from .results import results_bp

# Register blueprints with specific URL prefixes
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(upload_bp, url_prefix='/upload')
app.register_blueprint(results_bp, url_prefix='/results')

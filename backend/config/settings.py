import os
from datetime import timedelta
from dotenv import load_dotenv
from pathlib import Path

# Load .env from backend directory
load_dotenv(Path(__file__).resolve().parent.parent / '.env')

class Config:
    # Flask
    SECRET_KEY = os.getenv('SECRET_KEY', 'rentbike-secret-change-in-prod')

    # JWT
    JWT_SECRET_KEY          = os.getenv('JWT_SECRET_KEY', 'rentbike-jwt-change-in-prod')
    JWT_ACCESS_TOKEN_EXPIRES  = timedelta(hours=24)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    JWT_TOKEN_LOCATION        = ['headers']
    JWT_HEADER_NAME           = 'Authorization'
    JWT_HEADER_TYPE           = 'Bearer'

    # MongoDB Atlas
    MONGO_URI = os.getenv(
        'MONGO_URI',
        'mongodb+srv://rentbike:12bike07@rentbike-cluster.qbgnrsc.mongodb.net/rentbike'
        '?appName=rentbike-cluster&retryWrites=true&w=majority'
    )
    DB_NAME = os.getenv('DB_NAME', 'rentbike')

    # Uploads
    UPLOAD_FOLDER    = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'uploads')
    MAX_CONTENT_LENGTH = int(os.getenv('MAX_CONTENT_MB', 16)) * 1024 * 1024
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf'}

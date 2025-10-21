import os


class Config:
    # Use Render PostgreSQL if available, otherwise SQLite
    if os.getenv("DATABASE_URL"):
        SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")
    else:
        # For local development - use absolute path
        SQLALCHEMY_DATABASE_URI = "sqlite:///asupatri.db"
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-secret-change-me")
    PROPAGATE_EXCEPTIONS = True

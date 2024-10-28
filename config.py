import os

class Config:

    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your_secret_key_here'
    
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///library_management.db'

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    REMEMBER_COOKIE_DURATION = 7  # in days

    DAILY_FINE_RATE = float(os.environ.get('DAILY_FINE_RATE', 1.0))  # Fine rate per day for overdue books

    # Debug settings (useful for development, should be set to False in production)
    DEBUG = os.environ.get('FLASK_DEBUG', True)

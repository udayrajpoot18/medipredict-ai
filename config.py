"""
MediPredict AI - Production Configuration
Supports SQLite (dev) and PostgreSQL (production via DATABASE_URL)
"""

import os
from datetime import timedelta


class Config:
    # Core
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-change-in-prod-medipredict-2026')
    JSON_SORT_KEYS = False
    DEBUG = False
    TESTING = False

    # Database — Railway injects DATABASE_URL automatically
    raw_db = os.environ.get('DATABASE_URL', 'sqlite:///mediai_users.db')
    # Heroku/Railway give postgres:// but SQLAlchemy needs postgresql://
    if raw_db.startswith('postgres://'):
        raw_db = raw_db.replace('postgres://', 'postgresql://', 1)
    SQLALCHEMY_DATABASE_URI = raw_db
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
    }

    # Session
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'

    # Email
    MAIL_SERVER   = os.environ.get('MAIL_SERVER',   'smtp.gmail.com')
    MAIL_PORT     = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS  = os.environ.get('MAIL_USE_TLS',  'True') == 'True'
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME', '')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD', '')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER', 'Medipredict AI <noreply@medipredict.ai>')

    # Admin
    ADMIN_EMAIL    = os.environ.get('ADMIN_EMAIL',    'admin@medipredict.ai')
    ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'Admin@123Secure')


class DevelopmentConfig(Config):
    DEBUG = True
    SESSION_COOKIE_SECURE = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///mediai_users.db')


class ProductionConfig(Config):
    DEBUG = False


class TestingConfig(Config):
    TESTING = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SESSION_COOKIE_SECURE = False


config = {
    'development': DevelopmentConfig,
    'production':  ProductionConfig,
    'testing':     TestingConfig,
    'default':     DevelopmentConfig,
}

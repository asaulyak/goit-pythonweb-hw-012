"""
Mock configuration module for Sphinx documentation.
This module provides mock values for the application settings.
"""

class Settings:
    """Mock settings class that provides default values for all required settings."""
    
    DB_URL = "postgresql+asyncpg://mock:mock@localhost:5432/mock"
    JWT_SECRET = "mock_secret"
    JWT_ALGORITHM = "HS256"
    JWT_EXPIRATION_SECONDS = 3600
    HOST = "localhost"
    MAIL_USERNAME = "mock@example.com"
    MAIL_PASSWORD = "mock_password"
    MAIL_FROM = "mock@example.com"
    MAIL_PORT = 587
    MAIL_SERVER = "smtp.example.com"
    MAIL_FROM_NAME = "Mock User"
    CLOUDINARY_NAME = "mock_cloud"
    CLOUDINARY_API_KEY = "mock_api_key"
    CLOUDINARY_API_SECRET = "mock_api_secret"
    REDIS_HOST = "localhost"
    REDIS_PORT = 6379
    REDIS_PASSWORD = None
    REDIS_DB = 0

settings = Settings() 
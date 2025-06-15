"""
Application configuration module.
This module defines the application settings using Pydantic's BaseSettings
for type-safe configuration management and environment variable loading.
"""

from pydantic import ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Application settings class.
    
    This class defines all configuration parameters required by the application,
    including database, JWT, email, and cloud storage settings.
    
    Attributes:
        DB_URL (str): Database connection URL
        JWT_SECRET (str): Secret key for JWT token generation
        JWT_ALGORITHM (str): Algorithm used for JWT token generation
        JWT_EXPIRATION_SECONDS (int): JWT token expiration time in seconds
        HOST (str): Application host
        MAIL_USERNAME (str): Email service username
        MAIL_PASSWORD (str): Email service password
        MAIL_FROM (str): Default sender email address
        MAIL_PORT (int): Email service port
        MAIL_SERVER (str): Email service server
        MAIL_FROM_NAME (str): Default sender name
        CLOUDINARY_NAME (str): Cloudinary cloud name
        CLOUDINARY_API_KEY (str): Cloudinary API key
        CLOUDINARY_API_SECRET (str): Cloudinary API secret
        REDIS_HOST (str): Redis server host
        REDIS_PORT (int): Redis server port
        REDIS_PASSWORD (str | None): Redis server password
        REDIS_DB (int): Redis database number
    """
    
    DB_URL: str
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_SECONDS: int = 3600
    HOST: str
    MAIL_USERNAME: str
    MAIL_PASSWORD: str
    MAIL_FROM: str
    MAIL_PORT: int
    MAIL_SERVER: str
    MAIL_FROM_NAME: str
    CLOUDINARY_NAME: str
    CLOUDINARY_API_KEY: str
    CLOUDINARY_API_SECRET: str
    REDIS_HOST: str
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: str | None = None
    REDIS_DB: int = 0
    model_config = ConfigDict(
        extra="ignore", env_file=".env", env_file_encoding="utf-8", case_sensitive=True
    )


settings = Settings()

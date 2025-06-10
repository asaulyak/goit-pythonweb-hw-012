from pydantic import ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
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
    model_config = ConfigDict(
        extra="ignore", env_file=".env", env_file_encoding="utf-8", case_sensitive=True
    )


settings = Settings()

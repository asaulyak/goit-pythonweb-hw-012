"""
Database models module for contact management.
This module defines the SQLAlchemy models for user contacts and related enums.
"""

from enum import Enum

from sqlalchemy import Integer, String, DateTime, func, Date
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from src.database.db import Base


class UserRole(str, Enum):
    """
    Enumeration of possible user roles in the system.
    
    Attributes:
        USER (str): Regular user role
        ADMIN (str): Administrator role
    """
    USER = "user"
    ADMIN = "admin"


class Contact(Base):
    """
    SQLAlchemy model for user contacts.
    
    This model represents a user contact in the system with all associated
    information including personal details, authentication data, and metadata.
    
    Attributes:
        id (int): Primary key
        first_name (str): User's first name
        last_name (str): User's last name
        email (str): User's email address (unique)
        phone (str): User's phone number
        role (UserRole): User's role in the system
        birth_day (DateTime): User's birth date
        data (dict): Additional JSON data
        password (str): Hashed password
        avatar (str): URL to user's avatar image
        verified (bool): Email verification status
        verification_token (str): Token for email verification
        password_reset_token (str): Token for password reset
        created_at (DateTime): Record creation timestamp
        updated_at (DateTime): Record last update timestamp
    """
    
    __tablename__ = "contacts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    first_name: Mapped[str] = mapped_column(String(50))
    last_name: Mapped[str] = mapped_column(String(50))
    email: Mapped[str] = mapped_column(String(120), unique=True)
    phone: Mapped[str] = mapped_column(String(12))
    role: Mapped[UserRole] = mapped_column(
        String(50), default=UserRole.USER, server_default=UserRole.USER
    )
    birth_day: Mapped[DateTime] = mapped_column(
        Date(), nullable=False, server_default=func.now()
    )
    data: Mapped[dict] = mapped_column(JSONB, nullable=True)
    password: Mapped[str] = mapped_column(String(255))
    avatar: Mapped[str] = mapped_column(String(255), nullable=True)
    verified: Mapped[bool] = mapped_column(default=False)
    verification_token: Mapped[str] = mapped_column(String(255), nullable=True)
    password_reset_token: Mapped[str] = mapped_column(String(255), nullable=True)
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    def to_dict(self):
        """
        Convert the contact object to a dictionary.
        
        This method serializes the contact object into a dictionary format,
        excluding sensitive information like passwords and tokens.
        
        Returns:
            dict: Dictionary representation of the contact object
        """
        return {
            "id": self.id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "email": self.email,
            "phone": self.phone,
            "role": self.role,
            "birth_day": str(self.birth_day),
            "data": self.data,
            "avatar": self.avatar,
        }

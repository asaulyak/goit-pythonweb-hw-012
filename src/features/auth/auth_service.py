"""
Authentication service module.
This module provides authentication-related functionality including login,
email verification, and password management.
"""

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from src.auth.contacts_repository import ContactsRepository
from src.auth.hash import Hash, create_access_token
from src.features.auth.schema.login_schema import LoginModel


class AuthService:
    """
    Service class for handling authentication operations.
    
    This class provides methods for user login, email verification,
    and password management.
    
    Attributes:
        contacts_repository (ContactsRepository): Repository for contact operations
    """
    
    def __init__(self, db: AsyncSession):
        """
        Initialize the auth service.
        
        Args:
            db (AsyncSession): Database session for repository operations
        """
        self.contacts_repository = ContactsRepository(db)

    async def login(self, schema: LoginModel):
        """
        Authenticate a user and generate an access token.
        
        Args:
            schema (LoginModel): Login credentials containing email and password
            
        Returns:
            dict: Access token and token type
            
        Raises:
            HTTPException: If authentication fails or email is not verified
        """
        contact = await self.contacts_repository.get_contact_by_email(schema.email)

        if not contact or not contact.verified:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Incorrect email or password",
            )

        password_verified = Hash().verify_password(schema.password, contact.password)

        if not password_verified:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Incorrect email or password",
            )

        access_token = await create_access_token({"sub": contact.email})

        return {"access_token": access_token, "token_type": "bearer"}

    async def verify_email(self, verification_token: str):
        """
        Verify a user's email address using a verification token.
        
        Args:
            verification_token (str): Token received in verification email
            
        Raises:
            HTTPException: If verification fails or email is already verified
        """
        contact = await self.contacts_repository.get_contact_by_verification_token(
            verification_token
        )

        if not contact:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Verification failed"
            )

        if contact.verified:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Email already verified"
            )

        await self.contacts_repository.verify_email(contact.email)

    async def set_password(self, password_reset_token: str, password: str):
        """
        Set a new password using a password reset token.
        
        Args:
            password_reset_token (str): Token received in password reset email
            password (str): New password to set
        """
        hash = Hash()
        await self.contacts_repository.set_password(
            password_reset_token, hash.get_password_hash(password)
        )

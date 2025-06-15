"""
Authentication controller module.
This module defines the FastAPI routes for authentication-related operations
including login, email verification, and password management.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db
from src.features.auth.auth_service import AuthService
from src.features.auth.schema.login_response_schema import LoginResponseModel
from src.features.auth.schema.login_schema import LoginModel
from src.features.auth.schema.password_set_schema import PasswordSetModel

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=LoginResponseModel)
async def login(body: LoginModel, db: AsyncSession = Depends(get_db)):
    """
    Authenticate a user and return an access token.
    
    Args:
        body (LoginModel): Login credentials containing email and password
        db (AsyncSession): Database session
        
    Returns:
        LoginResponseModel: Access token and token type
        
    Raises:
        HTTPException: If authentication fails
    """
    auth_service = AuthService(db)

    return await auth_service.login(body)


@router.get("/verify/{verification_token}", status_code=200)
async def login(verification_token: str, db: AsyncSession = Depends(get_db)):
    """
    Verify a user's email address using a verification token.
    
    Args:
        verification_token (str): Token received in verification email
        db (AsyncSession): Database session
        
    Returns:
        str: Success message
        
    Raises:
        HTTPException: If verification fails
    """
    auth_service = AuthService(db)

    await auth_service.verify_email(verification_token)

    return "Verified"


@router.post("/set-password/{password_reset_token}", status_code=204)
async def set_password(
    body: PasswordSetModel,
    password_reset_token: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Set a new password using a password reset token.
    
    Args:
        body (PasswordSetModel): New password
        password_reset_token (str): Token received in password reset email
        db (AsyncSession): Database session
        
    Raises:
        HTTPException: If password reset fails
    """
    auth_service = AuthService(db)

    await auth_service.set_password(password_reset_token, body.password)

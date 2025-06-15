"""
Password hashing and JWT token management module.
This module provides functionality for password hashing, verification,
and JWT token generation and validation.
"""

import json
from datetime import datetime, timedelta, UTC
from typing import Optional

from fastapi import Depends, HTTPException, status
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from jose import JWTError, jwt

from src.auth.users_service import UserService
from src.cache.cache_service import redis_client, DEFAULT_CACHE_TTL
from src.config import settings
from src.database.db import get_db
from src.database.models.contacts_model import Contact, UserRole


class Hash:
    """
    Password hashing and verification class.
    
    This class provides methods for password hashing and verification
    using bcrypt algorithm.
    """
    
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def verify_password(self, plain_password, hashed_password):
        """
        Verify a plain password against a hashed password.
        
        Args:
            plain_password (str): The plain text password to verify
            hashed_password (str): The hashed password to compare against
            
        Returns:
            bool: True if the password matches, False otherwise
        """
        return self.pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str):
        """
        Generate a hash for a given password.
        
        Args:
            password (str): The password to hash
            
        Returns:
            str: The hashed password
        """
        return self.pwd_context.hash(password)


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)


async def create_access_token(data: dict, expires_delta: Optional[int] = None):
    """
    Create a new JWT access token.
    
    Args:
        data (dict): The data to encode in the token
        expires_delta (Optional[int]): Token expiration time in seconds
        
    Returns:
        str: The encoded JWT token
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(UTC) + timedelta(seconds=expires_delta)
    else:
        expire = datetime.now(UTC) + timedelta(seconds=settings.JWT_EXPIRATION_SECONDS)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt


def decode_jwt(token: str):
    """
    Decode and validate a JWT token.
    
    Args:
        token (str): The JWT token to decode
        
    Returns:
        str: The username from the token payload
        
    Raises:
        HTTPException: If the token is invalid or expired
    """
    try:
        # Decode JWT
        payload = jwt.decode(
            token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM]
        )
        username = payload["sub"]
        if username is None:
            raise credentials_exception
    except JWTError as e:
        raise credentials_exception

    return username


async def get_current_user(
    token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)
):
    """
    Get the current authenticated user from the database.
    
    Args:
        token (str): The JWT token from the request
        db (AsyncSession): Database session
        
    Returns:
        Contact: The authenticated user
        
    Raises:
        HTTPException: If the user is not found or token is invalid
    """
    username = decode_jwt(token)

    user_service = UserService(db)
    user = await user_service.get_user_by_username(username)
    if user is None:
        raise credentials_exception
    return user


async def get_current_cached_user(
    token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)
):
    """
    Get the current authenticated user with caching.
    
    Args:
        token (str): The JWT token from the request
        db (AsyncSession): Database session
        
    Returns:
        Contact: The authenticated user
        
    Raises:
        HTTPException: If the user is not found or token is invalid
    """
    username = decode_jwt(token)
    user_cache_key = f"current_user_{username}"
    cached_user = redis_client.get(user_cache_key)

    if cached_user:
        return json.loads(cached_user)

    user = await get_current_user(token, db)

    if user is None:
        raise credentials_exception

    redis_client.set(user_cache_key, json.dumps(user.to_dict()), DEFAULT_CACHE_TTL)
    return user


def get_current_admin_user(current_user: Contact = Depends(get_current_user)):
    """
    Verify that the current user has admin privileges.
    
    Args:
        current_user (Contact): The current authenticated user
        
    Returns:
        Contact: The admin user
        
    Raises:
        HTTPException: If the user is not an admin
    """
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403)
    return current_user

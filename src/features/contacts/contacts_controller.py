"""
Contacts controller module.
This module defines the FastAPI routes for contact management operations
including CRUD operations, search, and avatar management.
"""

from typing import Optional

from fastapi import APIRouter, Depends, status, HTTPException, Request, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from slowapi import Limiter
from slowapi.util import get_remote_address

from src.auth.hash import (
    get_current_user,
    get_current_admin_user,
    get_current_cached_user,
)
from src.cloudinary.upload_file_service import UploadFileService
from src.database import get_db
from src.features.contacts.contacts_service import ContactsService
from src.features.contacts.schema.contact_create_schema import ContactCreateModel
from src.features.contacts.schema.contact_response_schema import ContactResponseModel
from src.auth.contact_schema import ContactModel
from src.features.contacts.schema.contact_update_schema import ContactUpdateModel

router = APIRouter(prefix="/contacts", tags=["contacts"])
limiter = Limiter(key_func=get_remote_address)


@router.get("/", response_model=list[ContactResponseModel])
async def get_contacts(
    skip: int = 0, limit: int = 10, db: AsyncSession = Depends(get_db)
):
    """
    Get a paginated list of contacts.
    
    Args:
        skip (int): Number of records to skip
        limit (int): Maximum number of records to return
        db (AsyncSession): Database session
        
    Returns:
        list[ContactResponseModel]: List of contacts
    """
    contacts_service = ContactsService(db)
    contacts = await contacts_service.get_contacts(skip, limit)

    return contacts


@router.get("/search", response_model=list[ContactResponseModel])
async def search(
    first_name: Optional[str] = None,
    last_name: Optional[str] = None,
    email: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    """
    Search contacts by name or email.
    
    Args:
        first_name (Optional[str]): First name to search for
        last_name (Optional[str]): Last name to search for
        email (Optional[str]): Email to search for
        db (AsyncSession): Database session
        
    Returns:
        list[ContactResponseModel]: List of matching contacts
    """
    contacts_service = ContactsService(db)

    return await contacts_service.search(first_name, last_name, email)


@router.get("/soon_celebrate", response_model=list[ContactResponseModel])
async def search(db: AsyncSession = Depends(get_db)):
    """
    Get contacts with upcoming birthdays.
    
    Args:
        db (AsyncSession): Database session
        
    Returns:
        list[ContactResponseModel]: List of contacts with upcoming birthdays
    """
    contacts_service = ContactsService(db)

    return await contacts_service.soon_celebrate()


@router.post(
    "/signup", response_model=ContactResponseModel, status_code=status.HTTP_201_CREATED
)
async def create_contact(body: ContactCreateModel, db: AsyncSession = Depends(get_db)):
    """
    Create a new contact.
    
    Args:
        body (ContactCreateModel): Contact data
        db (AsyncSession): Database session
        
    Returns:
        ContactResponseModel: Created contact
        
    Raises:
        HTTPException: If contact creation fails
    """
    contacts_service = ContactsService(db)

    return await contacts_service.create_contact(body)


@router.get("/me", response_model=ContactResponseModel)
@limiter.limit("10/minute")
async def me(
    request: Request, contact: ContactModel = Depends(get_current_cached_user)
):
    """
    Get current user's contact information.
    
    Args:
        request (Request): FastAPI request object
        contact (ContactModel): Current authenticated user
        
    Returns:
        ContactResponseModel: Current user's contact information
    """
    return contact


@router.post("/reset-password/{email}", status_code=204)
@limiter.limit("1/minute")
async def reset_password(
    request: Request, email: str, db: AsyncSession = Depends(get_db)
):
    """
    Request a password reset for a contact.
    
    Args:
        request (Request): FastAPI request object
        email (str): Contact's email address
        db (AsyncSession): Database session
        
    Raises:
        HTTPException: If password reset request fails
    """
    contacts_service = ContactsService(db)
    await contacts_service.reset_password(email)


@router.get("/{contact_id}", response_model=ContactResponseModel)
async def get_contact(contact_id: int, db: AsyncSession = Depends(get_db)):
    """
    Get a specific contact by ID.
    
    Args:
        contact_id (int): Contact ID
        db (AsyncSession): Database session
        
    Returns:
        ContactResponseModel: Contact information
        
    Raises:
        HTTPException: If contact is not found
    """
    contacts_service = ContactsService(db)
    return await contacts_service.get_contact_by_id(contact_id)


@router.patch("/avatar", response_model=ContactResponseModel)
async def update_avatar_user(
    file: UploadFile = File(),
    contact: ContactModel = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Update a contact's avatar.
    
    Args:
        file (UploadFile): Avatar image file
        contact (ContactModel): Current authenticated user
        db (AsyncSession): Database session
        
    Returns:
        ContactResponseModel: Updated contact information
        
    Raises:
        HTTPException: If avatar update fails
    """
    avatar_url = UploadFileService().upload_file(file, contact.id)

    contacts_service = ContactsService(db)
    return await contacts_service.update_avatar_url(contact.id, avatar_url)


@router.patch(
    "/{contact_id}",
    response_model=ContactResponseModel,
    status_code=status.HTTP_201_CREATED,
)
async def create_contact(
    contact_id: int,
    body: ContactUpdateModel,
    contact: ContactModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Update a contact's information.
    
    Args:
        contact_id (int): Contact ID to update
        body (ContactUpdateModel): Updated contact data
        contact (ContactModel): Current authenticated user
        db (AsyncSession): Database session
        
    Returns:
        ContactResponseModel: Updated contact information
        
    Raises:
        HTTPException: If update fails or user is not authorized
    """
    if contact.id != contact_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")

    contacts_service = ContactsService(db)

    return await contacts_service.update_contact(contact_id, body)


@router.delete("/{contact_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_contact(
    contact_id: int,
    contact: ContactModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Delete a contact.
    
    Args:
        contact_id (int): Contact ID to delete
        contact (ContactModel): Current authenticated user
        db (AsyncSession): Database session
        
    Raises:
        HTTPException: If deletion fails or user is not authorized
    """
    if contact.id != contact_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")

    contacts_service = ContactsService(db)

    await contacts_service.delete_contact(contact_id)

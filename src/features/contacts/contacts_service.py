"""
Contacts service module.
This module provides business logic for contact management operations
including CRUD operations, search, and avatar management.
"""

from fastapi import HTTPException
from libgravatar import Gravatar
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from src.auth.contacts_repository import ContactsRepository
from src.auth.contact_schema import ContactModel
from src.auth.hash import Hash
from src.email.email_service import send_email
from src.features.contacts.schema.contact_update_schema import ContactUpdateModel
from src.config import settings


class ContactsService:
    """
    Service class for contact management operations.
    
    This class provides methods for managing contacts, including CRUD operations,
    search functionality, and avatar management.
    
    Attributes:
        contacts_repository (ContactsRepository): Repository for contact operations
    """
    
    def __init__(self, db: AsyncSession):
        """
        Initialize the contacts service.
        
        Args:
            db (AsyncSession): Database session for repository operations
        """
        self.contacts_repository = ContactsRepository(db)

    async def get_contacts(self, skip: int, limit: int):
        """
        Get a paginated list of contacts.
        
        Args:
            skip (int): Number of records to skip
            limit (int): Maximum number of records to return
            
        Returns:
            list[ContactModel]: List of contacts
        """
        return await self.contacts_repository.get_contacts(skip, limit)

    async def get_contact_by_id(self, contact_id: int):
        """
        Get a specific contact by ID.
        
        Args:
            contact_id (int): Contact ID
            
        Returns:
            ContactModel: Contact information
            
        Raises:
            HTTPException: If contact is not found
        """
        contact = await self.contacts_repository.get_contact_by_id(contact_id)

        if not contact:
            raise HTTPException(
                detail="Contact not found", status_code=status.HTTP_404_NOT_FOUND
            )

        return contact

    async def create_contact(self, body: ContactModel):
        """
        Create a new contact.
        
        Args:
            body (ContactModel): Contact data
            
        Returns:
            ContactModel: Created contact
            
        Raises:
            HTTPException: If contact already exists
        """
        existing_contact = await self.contacts_repository.get_contact_by_email(
            body.email
        )

        if existing_contact:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="Contact already exists"
            )

        password_hash = Hash().get_password_hash(body.password)
        body.password = password_hash

        g = Gravatar(body.email)
        body.avatar = g.get_image()

        contact = await self.contacts_repository.create_contact(body)

        await send_email(
            contact.email,
            "Welcome to Contacts",
            "verify_email.html",
            {
                "token": contact.verification_token,
                "host": settings.HOST,
                "first_name": contact.first_name,
            },
        )

        return contact

    async def update_contact(self, contact_id: int, body: ContactUpdateModel):
        """
        Update a contact's information.
        
        Args:
            contact_id (int): Contact ID to update
            body (ContactUpdateModel): Updated contact data
            
        Returns:
            ContactModel: Updated contact
        """
        return await self.contacts_repository.update_contact(contact_id, body)

    async def delete_contact(self, contact_id: int):
        """
        Delete a contact.
        
        Args:
            contact_id (int): Contact ID to delete
            
        Returns:
            bool: True if deletion was successful
        """
        return await self.contacts_repository.delete_contact(contact_id)

    async def search(
        self, first_name: str | None, last_name: str | None, email: str | None
    ):
        """
        Search contacts by name or email.
        
        Args:
            first_name (str | None): First name to search for
            last_name (str | None): Last name to search for
            email (str | None): Email to search for
            
        Returns:
            list[ContactModel]: List of matching contacts
            
        Raises:
            HTTPException: If no search parameters are provided
        """
        if not first_name and not last_name and not email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No search parameters provided",
            )

        return await self.contacts_repository.search_contact(
            first_name, last_name, email
        )

    async def soon_celebrate(self, days: int = 7):
        """
        Get contacts with upcoming birthdays.
        
        Args:
            days (int): Number of days to look ahead for birthdays
            
        Returns:
            list[ContactModel]: List of contacts with upcoming birthdays
        """
        return await self.contacts_repository.bd_soon(days)

    async def update_avatar_url(self, contact_id, avatar_url):
        """
        Update a contact's avatar URL.
        
        Args:
            contact_id (int): Contact ID
            avatar_url (str): New avatar URL
            
        Returns:
            ContactModel: Updated contact
        """
        await self.contacts_repository.update_avatar_url(contact_id, avatar_url)

        return await self.contacts_repository.get_contact_by_id(contact_id)

    async def reset_password(self, email):
        """
        Initiate password reset process for a contact.
        
        Args:
            email (str): Contact's email address
            
        Returns:
            ContactModel | None: Contact if found, None otherwise
        """
        contact = await self.contacts_repository.set_password_token(email)

        if not contact:
            return None

        await send_email(
            contact.email,
            "Reset password",
            "reset_password.html",
            {
                "token": contact.password_reset_token,
                "host": settings.HOST,
                "first_name": contact.first_name,
            },
        )

        return contact

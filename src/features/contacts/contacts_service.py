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
    def __init__(self, db: AsyncSession):
        self.contacts_repository = ContactsRepository(db)

    async def get_contacts(self, skip: int, limit: int):
        return await self.contacts_repository.get_contacts(skip, limit)

    async def get_contact_by_id(self, contact_id: int):
        contact = await self.contacts_repository.get_contact_by_id(contact_id)

        if not contact:
            raise HTTPException(
                detail="Contact not found", status_code=status.HTTP_404_NOT_FOUND
            )

        return contact

    async def create_contact(self, body: ContactModel):
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
        return await self.contacts_repository.update_contact(contact_id, body)

    async def delete_contact(self, contact_id: int):
        return await self.contacts_repository.delete_contact(contact_id)

    async def search(
        self, first_name: str | None, last_name: str | None, email: str | None
    ):
        if not first_name and not last_name and not email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No search parameters provided",
            )

        return await self.contacts_repository.search_contact(
            first_name, last_name, email
        )

    async def soon_celebrate(self, days: int = 7):
        return await self.contacts_repository.bd_soon(days)

    async def update_avatar_url(self, contact_id, avatar_url):
        await self.contacts_repository.update_avatar_url(contact_id, avatar_url)

        return await self.contacts_repository.get_contact_by_id(contact_id)

    async def reset_password(self, email):
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

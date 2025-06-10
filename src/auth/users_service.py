from sqlalchemy.ext.asyncio import AsyncSession
from src.auth.contacts_repository import ContactsRepository


class UserService:
    def __init__(self, db: AsyncSession):
        self.repository = ContactsRepository(db)

    async def get_user_by_username(self, email: str):
        return await self.repository.get_contact_by_email(email)

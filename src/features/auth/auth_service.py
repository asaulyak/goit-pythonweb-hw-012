from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from src.auth.contacts_repository import ContactsRepository
from src.auth.hash import Hash, create_access_token
from src.features.auth.schema.login_schema import LoginModel


class AuthService:
    def __init__(self, db: AsyncSession):
        self.contacts_repository = ContactsRepository(db)

    async def login(self, schema: LoginModel):
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
        hash = Hash()
        await self.contacts_repository.set_password(
            password_reset_token, hash.get_password_hash(password)
        )

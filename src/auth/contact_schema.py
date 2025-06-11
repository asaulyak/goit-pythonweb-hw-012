from datetime import date

from pydantic import BaseModel, Field

from src.database.models.contacts_model import UserRole


class ContactModel(BaseModel):
    first_name: str = Field(max_length=50)
    last_name: str = Field(max_length=50)
    email: str = Field(max_length=120)
    phone: str = Field(max_length=12)
    role: UserRole
    birth_day: date
    avatar: str | None = None
    data: dict | None = None

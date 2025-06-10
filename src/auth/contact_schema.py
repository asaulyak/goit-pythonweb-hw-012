from datetime import date

from pydantic import BaseModel, Field


class ContactModel(BaseModel):
    first_name: str = Field(max_length=50)
    last_name: str = Field(max_length=50)
    email: str = Field(max_length=120)
    phone: str = Field(max_length=12)
    birth_day: date
    avatar: str | None = None
    data: dict | None = None

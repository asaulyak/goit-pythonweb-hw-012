from pydantic import Field
from src.auth.contact_schema import ContactModel


class ContactCreateModel(ContactModel):
    password: str = Field(max_length=120, min_length=8)

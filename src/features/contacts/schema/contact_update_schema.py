from datetime import date
from typing import Optional

from pydantic import BaseModel, Field


class ContactUpdateModel(BaseModel):
    first_name: Optional[str] = Field(None, max_length=50)
    last_name: Optional[str] = Field(None, max_length=50)
    phone: Optional[str] = Field(None, max_length=12)
    birth_day: Optional[date] = None
    data: Optional[dict] = None

from pydantic import BaseModel, Field


class PasswordSetModel(BaseModel):
    password: str = Field(min_length=8, max_length=250)

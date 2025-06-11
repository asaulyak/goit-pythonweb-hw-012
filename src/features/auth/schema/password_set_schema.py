from pydantic import BaseModel, Field


class PasswordSetModel(BaseModel):
    password: str = Field(max_length=250)

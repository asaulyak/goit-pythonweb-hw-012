from pydantic import BaseModel, Field


class LoginModel(BaseModel):
    email: str = Field(max_length=120)
    password: str = Field(max_length=250)

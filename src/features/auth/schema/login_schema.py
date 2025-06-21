from pydantic import BaseModel, Field, EmailStr


class LoginModel(BaseModel):
    email: EmailStr = Field(max_length=120)
    password: str = Field(max_length=250)

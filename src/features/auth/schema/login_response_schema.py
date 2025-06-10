from pydantic import BaseModel


class LoginResponseModel(BaseModel):
    access_token: str
    token_type: str

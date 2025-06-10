from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db
from src.features.auth.auth_service import AuthService
from src.features.auth.schema.login_response_schema import LoginResponseModel
from src.features.auth.schema.login_schema import LoginModel

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=LoginResponseModel)
async def login(body: LoginModel, db: AsyncSession = Depends(get_db)):
    auth_service = AuthService(db)

    return await auth_service.login(body)


@router.get("/verify/{verification_token}", status_code=200)
async def login(verification_token: str, db: AsyncSession = Depends(get_db)):
    auth_service = AuthService(db)

    await auth_service.verify_email(verification_token)

    return "Verified"

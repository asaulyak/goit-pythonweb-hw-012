from pathlib import Path

from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from fastapi_mail.errors import ConnectionErrors
from pydantic import EmailStr

from src.config import settings

conf = ConnectionConfig(
    MAIL_USERNAME=settings.MAIL_USERNAME,
    MAIL_PASSWORD=settings.MAIL_PASSWORD,
    MAIL_FROM=settings.MAIL_FROM,
    MAIL_PORT=settings.MAIL_PORT,
    MAIL_SERVER=settings.MAIL_SERVER,
    MAIL_FROM_NAME=settings.MAIL_FROM_NAME,
    MAIL_STARTTLS=False,
    MAIL_SSL_TLS=True,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
    TEMPLATE_FOLDER=Path(__file__).parent / "templates",
)


async def send_email(
    email: EmailStr, subject: str, template_name: str, template_body: dict
):
    try:
        message = MessageSchema(
            subject=subject,
            recipients=[email],
            template_body=template_body,
            subtype=MessageType.html,
        )

        fm = FastMail(conf)
        await fm.send_message(message, template_name=template_name)
    except ConnectionErrors as err:
        print(err)

from sqlalchemy import Integer, String, DateTime, func, Date
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from src.database.db import Base


class Contact(Base):
    __tablename__ = "contacts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    first_name: Mapped[str] = mapped_column(String(50))
    last_name: Mapped[str] = mapped_column(String(50))
    email: Mapped[str] = mapped_column(String(120), unique=True)
    phone: Mapped[str] = mapped_column(String(12))
    birth_day: Mapped[DateTime] = mapped_column(
        Date(), nullable=False, server_default=func.now()
    )
    data: Mapped[dict] = mapped_column(JSONB, nullable=True)
    password: Mapped[str] = mapped_column(String(255))
    avatar: Mapped[str] = mapped_column(String(255), nullable=True)
    verified: Mapped[bool] = mapped_column(default=False)
    verification_token: Mapped[str] = mapped_column(String(255), nullable=True)
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    def to_dict(self):
        """
        Converts the object's properties to a dictionary.
        This is the key method for making the object serializable.
        """
        return {
            "id": self.id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "email": self.email,
            "phone": self.phone,
            "birth_day": str(self.birth_day),
            "data": self.data,
            "avatar": self.avatar,
        }

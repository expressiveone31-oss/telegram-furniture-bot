from datetime import datetime
from typing import Optional

from sqlalchemy import String, Text, Integer, BigInteger, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database.session import Base


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    order_number: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    telegram_user_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    telegram_username: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    telegram_first_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    source: Mapped[str] = mapped_column(String(50), default="direct")
    product_id: Mapped[str] = mapped_column(String(100), nullable=False)
    product_name: Mapped[str] = mapped_column(String(255), nullable=False)
    size: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    color: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    city: Mapped[str] = mapped_column(String(100), nullable=False)
    customer_name: Mapped[str] = mapped_column(String(100), nullable=False)
    contact: Mapped[str] = mapped_column(String(255), nullable=False)
    comment: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    custom_request: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    custom_image_file_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    product_price: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    service_fee: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    delivery_price: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    total_price: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="new")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=func.now(), onupdate=func.now()
    )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "order_number": self.order_number,
            "telegram_user_id": self.telegram_user_id,
            "telegram_username": self.telegram_username,
            "telegram_first_name": self.telegram_first_name,
            "source": self.source,
            "product_id": self.product_id,
            "product_name": self.product_name,
            "size": self.size,
            "color": self.color,
            "city": self.city,
            "customer_name": self.customer_name,
            "contact": self.contact,
            "comment": self.comment,
            "custom_request": self.custom_request,
            "custom_image_file_id": self.custom_image_file_id,
            "product_price": self.product_price,
            "service_fee": self.service_fee,
            "delivery_price": self.delivery_price,
            "total_price": self.total_price,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class Question(Base):
    __tablename__ = "questions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    telegram_user_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    telegram_username: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="new")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())

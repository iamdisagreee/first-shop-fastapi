from typing import List

from sqlalchemy.orm import relationship, Mapped
from sqlalchemy.testing.schema import mapped_column

from app.backend.db import Base
from sqlalchemy import Integer, String, Boolean, Float, ForeignKey
from . import category

class Product(Base):
    __tablename__ = 'products'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String)
    slug: Mapped[str] = mapped_column(String, unique=True, index=True)
    description: Mapped[str] = mapped_column(String)
    price: Mapped[int] = mapped_column(Integer)
    image_url: Mapped[str] = mapped_column(String)
    stock: Mapped[int] = mapped_column(Integer)
    rating: Mapped[float] = mapped_column(Float)
    category_id: Mapped[int] = mapped_column(Integer, ForeignKey('categories.id'))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    category: Mapped["category.Category"] = relationship('Category', back_populates='products')
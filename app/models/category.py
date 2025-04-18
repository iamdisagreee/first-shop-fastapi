from typing import List

from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.backend.db import Base
from sqlalchemy import Integer, String, Boolean, ForeignKey
from . import products

class Category(Base):
    __tablename__ = 'categories'
    __table_args__ = {'extend_existing': True}
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String)
    slug: Mapped[str] = mapped_column(String, unique=True, index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    parent_id: Mapped[int] = mapped_column(Integer, ForeignKey('categories.id'), nullable=True)

    products: Mapped[List["products.Product"]] = relationship('Product', back_populates='category')
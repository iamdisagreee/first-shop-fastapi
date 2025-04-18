from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

from app.config import load_config

config = load_config()
engine = create_async_engine(config.site.postgres, echo=True)
session_maker = async_sessionmaker(engine)

class Base(DeclarativeBase):
    pass

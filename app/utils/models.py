from datetime import datetime

from sqlalchemy import BigInteger, ForeignKey, DateTime
from sqlalchemy.orm import relationship, Mapped, mapped_column, DeclarativeBase
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine
from config import DATABASE_URL

engine = create_async_engine(DATABASE_URL, echo=True)
async_session = async_sessionmaker(engine)

class Base(AsyncAttrs, DeclarativeBase):
    pass


class Langs(Base):
    __tablename__ = 'users_multilanguages'

    lang: Mapped[str] = mapped_column(primary_key=True)
    daily_response: Mapped[str] = mapped_column()
    month_response: Mapped[str] = mapped_column()
    six_month_response: Mapped[str] = mapped_column()
    year_response: Mapped[str] = mapped_column()
    expired_response: Mapped[str] = mapped_column()
    tariff_list: Mapped[str] = mapped_column()
    helping: Mapped[str] = mapped_column()
    for_change_tariff: Mapped[str] = mapped_column()
    requisites: Mapped[str] = mapped_column()
    not_founds: Mapped[str] = mapped_column()
    found: Mapped[str] = mapped_column()
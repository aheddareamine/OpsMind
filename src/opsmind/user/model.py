from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped
import uuid

from opsmind.core.db import engine


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id : Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    email : Mapped[str] = mapped_column(index=True, unique=True)
    username : Mapped[str]
    hashed_password : Mapped[str]

# Base.metadata.create_all(bind=engine)
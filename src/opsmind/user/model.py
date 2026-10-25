from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped

from opsmind.core.db import engine


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id : Mapped[str] = mapped_column(primary_key=True)
    email : Mapped[str] = mapped_column(index=True, unique=True)
    username : Mapped[str]
    age : Mapped[int]
    hashed_password = Mapped[str]


Base.metadata.create_all(bind=engine)
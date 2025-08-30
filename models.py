import atexit
import os
import datetime

from sqlalchemy import create_engine, Integer, String, func, DateTime
from sqlalchemy.orm import sessionmaker, DeclarativeBase, mapped_column, Mapped


POSTGRES_USER = os.getenv("POSTGRES_USER", "user")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "1234")
POSTGRES_DB = os.getenv("POSTGRES_DB", "advertisements")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5431")

PG_DSN = (
    f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@"
    f"{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
)

engine = create_engine(PG_DSN)
Session = sessionmaker(bind=engine)


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)

    @property
    def id_json(self):
        return {"id": self.id}

    @property
    def json(self):
        return {
            "id": self.id,
            "email": self.email,
        }


class Advertisement(Base):
    __tablename__ = "advertisements"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String)
    description: Mapped[str] = mapped_column(String)
    date: Mapped[datetime.datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
    )
    owner: Mapped[str] = mapped_column(String)

    @property
    def id_json(self):
        return {"id": self.id}

    @property
    def json(self):
        return{
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "date": self.date.isoformat(),
            "owner": self.owner
        }


Base.metadata.create_all(engine)

atexit.register(engine.dispose)

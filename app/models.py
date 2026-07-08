import uuid
from sqlalchemy import Column, String, Integer, Text
from app.database import Base


class Book(Base):
    __tablename__ = "books"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String(255), nullable=False, index=True)
    author = Column(String(255), nullable=False, index=True)
    genre = Column(String(100), nullable=False, index=True)
    year = Column(Integer, nullable=True)
    description = Column(Text, nullable=True)

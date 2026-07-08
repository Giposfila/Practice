from pydantic import BaseModel


class BookCreate(BaseModel):
    title: str
    author: str
    genre: str
    year: int | None = None
    description: str | None = None


class BookUpdate(BaseModel):
    title: str | None = None
    author: str | None = None
    genre: str | None = None
    year: int | None = None
    description: str | None = None


class BookResponse(BaseModel):
    id: str
    title: str
    author: str
    genre: str
    year: int | None
    description: str | None

    model_config = {"from_attributes": True}

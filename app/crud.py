from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Book
from app.schemas import BookCreate, BookUpdate


async def get_books(
    db: AsyncSession,
    search: str | None = None,
    author: str | None = None,
    genre: str | None = None,
    limit: int = 20,
    offset: int = 0,
) -> list[Book]:
    stmt = select(Book)
    if search:
        stmt = stmt.where(
            Book.title.ilike(f"%{search}%") | Book.description.ilike(f"%{search}%")
        )
    if author:
        stmt = stmt.where(Book.author.ilike(f"%{author}%"))
    if genre:
        stmt = stmt.where(Book.genre.ilike(f"%{genre}%"))
    stmt = stmt.order_by(Book.title).limit(limit).offset(offset)
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def get_book(db: AsyncSession, book_id: str) -> Book | None:
    result = await db.execute(select(Book).where(Book.id == book_id))
    return result.scalar_one_or_none()


async def create_book(db: AsyncSession, data: BookCreate) -> Book:
    book = Book(**data.model_dump())
    db.add(book)
    await db.commit()
    await db.refresh(book)
    return book


async def update_book(db: AsyncSession, book_id: str, data: BookUpdate) -> Book | None:
    book = await get_book(db, book_id)
    if not book:
        return None
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(book, field, value)
    await db.commit()
    await db.refresh(book)
    return book


async def delete_book(db: AsyncSession, book_id: str) -> bool:
    result = await db.execute(delete(Book).where(Book.id == book_id))
    await db.commit()
    return result.rowcount > 0


async def get_authors(db: AsyncSession) -> list[str]:
    result = await db.execute(select(Book.author).distinct().order_by(Book.author))
    return [row[0] for row in result.all()]


async def get_genres(db: AsyncSession) -> list[str]:
    result = await db.execute(select(Book.genre).distinct().order_by(Book.genre))
    return [row[0] for row in result.all()]

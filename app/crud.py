import time

from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Book
from app.schemas import BookCreate, BookUpdate

# Per-process TTL cache for the rarely-changing distinct author/genre lists.
# Not invalidated on write (that would need a shared store like Redis across
# the 4 uvicorn workers) - a short TTL is a good enough tradeoff here since
# these lists change far less often than they're read.
_REF_CACHE_TTL = 5.0
_authors_cache: tuple[float, list[str]] | None = None
_genres_cache: tuple[float, list[str]] | None = None


async def get_books(
    db: AsyncSession,
    search: str | None = None,
    author: str | None = None,
    genre: str | None = None,
    limit: int = 50,
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
    return book


async def update_book(db: AsyncSession, book_id: str, data: BookUpdate) -> Book | None:
    values = data.model_dump(exclude_unset=True)
    if not values:
        return await get_book(db, book_id)
    stmt = update(Book).where(Book.id == book_id).values(**values).returning(Book)
    result = await db.execute(stmt)
    book = result.scalar_one_or_none()
    await db.commit()
    return book


async def delete_book(db: AsyncSession, book_id: str) -> bool:
    result = await db.execute(delete(Book).where(Book.id == book_id))
    await db.commit()
    return result.rowcount > 0


async def get_authors(db: AsyncSession) -> list[str]:
    global _authors_cache
    now = time.monotonic()
    if _authors_cache is not None and now - _authors_cache[0] < _REF_CACHE_TTL:
        return _authors_cache[1]
    result = await db.execute(select(Book.author).distinct().order_by(Book.author))
    data = [row[0] for row in result.all()]
    _authors_cache = (now, data)
    return data


async def get_genres(db: AsyncSession) -> list[str]:
    global _genres_cache
    now = time.monotonic()
    if _genres_cache is not None and now - _genres_cache[0] < _REF_CACHE_TTL:
        return _genres_cache[1]
    result = await db.execute(select(Book.genre).distinct().order_by(Book.genre))
    data = [row[0] for row in result.all()]
    _genres_cache = (now, data)
    return data

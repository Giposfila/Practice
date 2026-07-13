from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db, init_db
from app.schemas import BookCreate, BookUpdate, BookResponse
from app import crud


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(title="Book Catalog", lifespan=lifespan)


@app.get("/books", response_model=list[BookResponse])
async def list_books(
    search: str | None = Query(None, description="Search in title and description"),
    author: str | None = Query(None, description="Filter by author"),
    genre: str | None = Query(None, description="Filter by genre"),
    limit: int = Query(50, ge=1, le=200, description="Max books to return"),
    offset: int = Query(0, ge=0, description="Number of books to skip"),
    db: AsyncSession = Depends(get_db),
):
    return await crud.get_books(
        db, search=search, author=author, genre=genre, limit=limit, offset=offset
    )


@app.get("/books/{book_id}", response_model=BookResponse)
async def get_book(book_id: str, db: AsyncSession = Depends(get_db)):
    book = await crud.get_book(db, book_id)
    if not book:
        raise HTTPException(404, "Book not found")
    return book


@app.post("/books", response_model=BookResponse, status_code=201)
async def create_book(data: BookCreate, db: AsyncSession = Depends(get_db)):
    return await crud.create_book(db, data)


@app.put("/books/{book_id}", response_model=BookResponse)
async def update_book(
    book_id: str, data: BookUpdate, db: AsyncSession = Depends(get_db)
):
    book = await crud.update_book(db, book_id, data)
    if not book:
        raise HTTPException(404, "Book not found")
    return book


@app.delete("/books/{book_id}", status_code=204)
async def delete_book(book_id: str, db: AsyncSession = Depends(get_db)):
    deleted = await crud.delete_book(db, book_id)
    if not deleted:
        raise HTTPException(404, "Book not found")


@app.get("/authors", response_model=list[str])
async def list_authors(db: AsyncSession = Depends(get_db)):
    return await crud.get_authors(db)


@app.get("/genres", response_model=list[str])
async def list_genres(db: AsyncSession = Depends(get_db)):
    return await crud.get_genres(db)

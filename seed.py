import asyncio
from app.database import async_session, init_db
from app.models import Book

SEED_DATA = [
    Book(title="The Great Gatsby", author="F. Scott Fitzgerald", genre="Fiction", year=1925, description="A story of the mysteriously wealthy Jay Gatsby and his love for Daisy Buchanan."),
    Book(title="To Kill a Mockingbird", author="Harper Lee", genre="Fiction", year=1960, description="The unforgettable novel of a childhood in a sleepy Southern town and the crisis of conscience that rocked it."),
    Book(title="1984", author="George Orwell", genre="Dystopian", year=1949, description="A dystopian social science fiction novel and cautionary tale about the future of totalitarianism."),
    Book(title="Pride and Prejudice", author="Jane Austen", genre="Romance", year=1813, description="A romantic novel of manners that follows the character development of Elizabeth Bennet."),
    Book(title="The Catcher in the Rye", author="J.D. Salinger", genre="Fiction", year=1951, description="A story about teenage alienation and loss of innocence."),
    Book(title="The Hobbit", author="J.R.R. Tolkien", genre="Fantasy", year=1937, description="A fantasy novel about the adventures of Bilbo Baggins on a quest to reclaim the lost Dwarf Kingdom."),
    Book(title="Dune", author="Frank Herbert", genre="Sci-Fi", year=1965, description="A sci-fi epic set in the distant future amidst a huge interstellar empire."),
    Book(title="The Shining", author="Stephen King", genre="Horror", year=1977, description="A horror novel about a family trapped in an isolated hotel with a dark past."),
    Book(title="Brave New World", author="Aldous Huxley", genre="Dystopian", year=1932, description="A dystopian novel about a futuristic World State and its citizens."),
    Book(title="The Alchemist", author="Paulo Coelho", genre="Adventure", year=1988, description="A philosophical novel about a young Andalusian shepherd's journey to Egypt."),
]


async def seed():
    await init_db()
    async with async_session() as session:
        for book in SEED_DATA:
            session.add(book)
        await session.commit()
    print(f"Seeded {len(SEED_DATA)} books")


if __name__ == "__main__":
    asyncio.run(seed())

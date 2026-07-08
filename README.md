# Book Catalog API

Простое REST API для каталога книг. Позволяет создавать, читать, обновлять и удалять книги, а также получать список авторов и жанров.

## Стек

- **Python** + **FastAPI** + **Uvicorn**
- **PostgreSQL** + **SQLAlchemy** (async) + **asyncpg**
- **Docker** + **Docker Compose**

## Быстрый старт

```bash
docker-compose up --build
```

API будет доступен на `http://localhost:8000`. Документация (Swagger): `http://localhost:8000/docs`.

Чтобы наполнить БД тестовыми данными (10 книг):

```bash
docker-compose run --rm api python seed.py
```

## Эндпоинты

| Метод   | Путь                | Что делает                        |
|---------|---------------------|-----------------------------------|
| `GET`   | `/books`            | Список книг (с фильтрами)         |
| `GET`   | `/books/{id}`       | Книга по ID                       |
| `POST`  | `/books`            | Создать книгу                     |
| `PUT`   | `/books/{id}`       | Обновить книгу                    |
| `DELETE`| `/books/{id}`       | Удалить книгу                     |
| `GET`   | `/authors`          | Список всех авторов               |
| `GET`   | `/genres`           | Список всех жанров                |

### Фильтры для GET /books

- `?search=` — поиск по названию и описанию (регистронезависимый)
- `?author=` — фильтр по автору
- `?genre=` — фильтр по жанру

## Примеры

Создать книгу:

```bash
curl -X POST http://localhost:8000/books \
  -H "Content-Type: application/json" \
  -d '{"title":"Война и мир","author":"Лев Толстой","genre":"Роман","year":1869}'
```

Получить все книги в жанре "Роман":

```bash
curl "http://localhost:8000/books?genre=Роман"
```

## Переменные окружения

| Переменная       | По умолчанию         | Описание              |
|------------------|----------------------|-----------------------|
| `DATABASE_URL`   | `postgresql+asyncpg://postgres:postgres@db:5432/book_catalog` | Строка подключения к БД |

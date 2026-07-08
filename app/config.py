from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://bookuser:bookpass@localhost:5432/book_catalog"

    class Config:
        env_file = ".env"


settings = Settings()

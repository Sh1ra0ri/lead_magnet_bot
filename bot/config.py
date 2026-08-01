from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    BOT_TOKEN: str
    DB_DSN: str
    SUPER_ADMIN_ID: int

    class Config:
        env_file = ".env"


settings = Settings()
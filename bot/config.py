from os import path, sep, pardir

from pydantic_settings import BaseSettings

envPath = path.normpath(path.dirname(__file__) + sep + pardir) + sep + '.env'


class Settings(BaseSettings):
    DATABASE_URI: str
    BOT_TOKEN: str
    BOT_ADMIN_ID: str
    BOT_ADMIN_ID2: str
    REDIS_URI: str
    REDIS_PASSWORD: str
    DEFAULT_CONTENT_LANGUAGE: str
    CRM_URL: str
    CRM_TOKEN: str

    class Config:
        env_file = envPath
        env_file_encoding = 'utf-8'


settings = Settings()

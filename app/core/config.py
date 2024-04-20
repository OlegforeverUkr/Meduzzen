from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')
    RELOAD: bool
    HOST: str
    PORT: int

    DB_USER: str
    DB_PASSWORD: str
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str

    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_URL: str

    SQL_URL: str

    AUTH0_DOMAIN: str
    AUTH0_API_AUDIENCE: str
    AUTH0_ISSUER: str
    AUTH0_ALGORITHMS: str

    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int

settings = Settings(_env_file='../.env', _env_file_encoding='utf-8')
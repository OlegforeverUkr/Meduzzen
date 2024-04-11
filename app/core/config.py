from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')
    RELOAD: bool
    HOST: str
    PORT: int


settings = Settings(_env_file='../.env', _env_file_encoding='utf-8')

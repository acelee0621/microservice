from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DEBUG_MODE: bool
    REDIS_URL: str    

    
    model_config = SettingsConfigDict(env_file=(".env", ".env.local"))


@lru_cache()
def get_settings() -> Settings:
    return Settings()


config = Settings()
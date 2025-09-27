# /src/core/config.py
from functools import lru_cache

from pydantic import computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """应用配置"""

    app_name: str = "User Service"
    debug_mode: bool = False

    # 数据库配置    
    echo: bool = False

    # SQLite 配置
    sqlite_path: str = "./data/users.sqlite3"

    @computed_field
    @property
    def DATABASE_URL(self) -> str:        
        return f"sqlite+aiosqlite:///{self.sqlite_path}"
    
    # JWT 配置
    JWT_SECRET: str = "CHANGE_ME"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
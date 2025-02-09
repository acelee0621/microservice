from pydantic_settings import BaseSettings, SettingsConfigDict


from functools import lru_cache





class Settings(BaseSettings):
    app_name: str = "Todos Service"
    REDIS_URL: str    

    
    model_config = SettingsConfigDict(env_file=(".env", ".env.local"))

        


@lru_cache()
def get_settings():
    return Settings()


config = get_settings()

from pydantic_settings import BaseSettings, SettingsConfigDict


from functools import lru_cache





class Settings(BaseSettings):
    app_name: str = "Todos Service"
    REDIS_URL: str 
    DEBUG: bool = False   

    
    model_config = SettingsConfigDict(env_file=(".env", ".env.local"))

        


@lru_cache()
def get_settings():
    return Settings()


settings = get_settings()

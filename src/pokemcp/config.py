from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    redis_url: str | None = None
    pokeapi_base_url: str = "https://pokeapi.co/api/v2"
    log_level: str = "INFO"
    cache_ttl: int = 3600

    class Config:
        env_file = ".env"

settings = Settings()
from pydantic_settings import BaseSettings


# Settinges for environment variables:
class Settings(BaseSettings):
    APP_NAME: str
    APP_VERSION: str
    OPENAI_API_KEY: str
    FILE_ALLOWED_TYPES: list
    FILE_MAX_SIZE: int
    FILE_DEFAULT_CHUNK_SIZE: int
    MONGODB_URL: str
    MONGODB_DATABASE: str

    # Config .env file:
    class Config:
        env_file = r".env"


# Getter for settings:
def get_settings():
    return Settings()

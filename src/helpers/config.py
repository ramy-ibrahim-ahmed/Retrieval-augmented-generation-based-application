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
    GENERATION_BACKEND: str
    EMBEDDING_BACKEND: str
    OPENAI_API_KEY: str = None
    OPENAI_API_URL: str = None
    COHERE_API_KEY: str = None
    GENERATION_MODEL_ID: str = None
    EMBEDDING_MODEL_ID: str = None
    EMBEDDING_SIZE: int = None
    MAX_INPUT_NUM_TOKENS: int = None
    MAX_OUTPUT_NUM_TOKENS: int = None
    GENERATION_TEMPERATURE: float = None
    VECTOR_DB_BACKEND: str
    VECTOR_DB_PATH: str
    VECTOR_DB_DISTANCE_METRIC: str = None

    # Config .env file:
    class Config:
        env_file = r".env"


# Getter for settings:
def get_settings():
    return Settings()

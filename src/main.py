from fastapi import FastAPI
from routes import base, data
from motor.motor_asyncio import AsyncIOMotorClient
from helpers import get_settings
from contextlib import asynccontextmanager
from stores.llm import LLMProviderFactory

# Application initialization:
app = FastAPI()


# Start up and end events for mongo conection and close:
# all routes can access variable mongo_connection & db_clint.
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 1. get settings to get env vars.
    # 2. conect with mongo then database.
    # 2. wait at the end of lifespan to close.
    settings = get_settings()
    app.mongo_connection = AsyncIOMotorClient(settings.MONGODB_URL)
    app.db_client = app.mongo_connection[settings.MONGODB_DATABASE]

    llm_provider_factory = LLMProviderFactory(settings)

    app.generation_client = llm_provider_factory.create(
        provider=settings.GENERATION_BACKEND,
    )
    app.generation_client.set_generation_model(
        model_id=settings.GENERATION_MODEL_ID,
    )

    app.embedding_client = llm_provider_factory.create(
        provider=settings.EMBEDDING_BACKEND,
    )
    app.embedding_client.set_embedding_model(
        model_id=settings.EMBEDDING_MODEL_ID,
        embedding_size=settings.EMBEDDING_SIZE,
    )

    yield
    app.mongo_connection.close()


# Set lifespan:
app = FastAPI(lifespan=lifespan)


# Set routers:
app.include_router(base.base_router)
app.include_router(data.data_router)

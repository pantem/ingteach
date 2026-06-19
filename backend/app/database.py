from motor.motor_asyncio import AsyncIOMotorClient
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    MONGO_URI: str = "mongodb+srv://seshomaru:P4nqu3s1t0@logis.2m8j0.mongodb.net/teachlang"
    MONGO_DB: str = "teachlang"

    class Config:
        env_file = ".env"

settings = Settings()
_client: AsyncIOMotorClient = None

async def get_db():
    global _client
    if _client is None:
        _client = AsyncIOMotorClient(settings.MONGO_URI,
                                      serverSelectionTimeoutMS=5000,
                                      connectTimeoutMS=5000)
    return _client[settings.MONGO_DB]

async def connect_db():
    try:
        db = await get_db()
        await _client.admin.command("ping")
    except Exception as e:
        pass

async def close_db():
    global _client
    if _client:
        _client.close()
        _client = None

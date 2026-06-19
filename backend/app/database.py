from motor.motor_asyncio import AsyncIOMotorClient
from pydantic_settings import BaseSettings
from typing import Optional

DEFAULT_MONGO_URI = "mongodb+srv://seshomaru:P4nqu3s1t0@logis.2m8j0.mongodb.net/teachlang"

class Settings(BaseSettings):
    MONGO_URI: Optional[str] = None
    MONGO_DB: str = "teachlang"

    class Config:
        env_file = ".env"

    @property
    def mongo_uri(self) -> str:
        return self.MONGO_URI or DEFAULT_MONGO_URI

settings = Settings()
_client: AsyncIOMotorClient = None

async def get_db():
    global _client
    if _client is None:
        _client = AsyncIOMotorClient(settings.mongo_uri,
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

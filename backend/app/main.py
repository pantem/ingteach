from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import connect_db, close_db
from app.api import modules, conversation, conjugations, tests, progress, auth

@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_db()
    yield
    await close_db()

app = FastAPI(title="English Learning API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(modules.router, prefix="/api/modules", tags=["modules"])
app.include_router(conversation.router, prefix="/api/conversation", tags=["conversation"])
app.include_router(conjugations.router, prefix="/api/conjugations", tags=["conjugations"])
app.include_router(tests.router, prefix="/api/tests", tags=["tests"])
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(progress.router, prefix="/api/progress", tags=["progress"])

@app.get("/")
async def root():
    return {"message": "English Learning API", "version": "1.0.0"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

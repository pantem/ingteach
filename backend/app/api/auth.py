from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from bson.objectid import ObjectId
from app.database import get_db

router = APIRouter()
security = HTTPBearer()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SECRET_KEY = "teachlang-secret-key-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_DAYS = 30

class RegisterRequest(BaseModel):
    username: str
    email: str
    password: str

class LoginRequest(BaseModel):
    email: str
    password: str

class UserResponse(BaseModel):
    id: str
    username: str
    email: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    db = await get_db()
    user = await db["users"].find_one({"_id": ObjectId(user_id)})
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return user

@router.post("/register", response_model=TokenResponse)
async def register(req: RegisterRequest):
    db = await get_db()
    existing = await db["users"].find_one({"email": req.email})
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    existing = await db["users"].find_one({"username": req.username})
    if existing:
        raise HTTPException(status_code=400, detail="Username already taken")

    user_doc = {
        "username": req.username,
        "email": req.email,
        "password": pwd_context.hash(req.password),
        "created_at": datetime.utcnow().isoformat(),
    }
    result = await db["users"].insert_one(user_doc)
    user_id = str(result.inserted_id)

    await db["progress"].insert_one({
        "user_id": user_id,
        "completed_modules": [],
        "current_module": "mod-1",
        "test_scores": {},
        "conversation_sessions": 0,
        "total_practice_time": 0,
    })

    token = create_access_token({"sub": user_id})
    return TokenResponse(
        access_token=token,
        user=UserResponse(id=user_id, username=req.username, email=req.email)
    )

@router.post("/login", response_model=TokenResponse)
async def login(req: LoginRequest):
    db = await get_db()
    user = await db["users"].find_one({"email": req.email})
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    if not pwd_context.verify(req.password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    user_id = str(user["_id"])
    token = create_access_token({"sub": user_id})
    return TokenResponse(
        access_token=token,
        user=UserResponse(id=user_id, username=user["username"], email=user["email"])
    )

@router.get("/me", response_model=UserResponse)
async def get_me(user: dict = Depends(get_current_user)):
    return UserResponse(
        id=str(user["_id"]),
        username=user["username"],
        email=user["email"]
    )

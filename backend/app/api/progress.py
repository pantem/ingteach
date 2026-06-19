from fastapi import APIRouter, Depends
from pydantic import BaseModel
from app.database import get_db
from app.api.auth import get_current_user

class ScoreUpdate(BaseModel):
    module_id: str
    score: float

class SessionRecord(BaseModel):
    duration_seconds: int

router = APIRouter()
auth_router = APIRouter()

MODULE_MAP = {
    "mod-1": "Greetings and Introductions",
    "mod-2": "Daily Routines",
    "mod-3": "Food and Restaurants",
    "mod-4": "Past Experiences",
    "mod-5": "Future Plans",
    "mod-6": "Travel and Directions",
    "mod-7": "Opinions and Debates",
    "mod-8": "Business English",
}

MODULES_ORDER = ["mod-1", "mod-2", "mod-3", "mod-4", "mod-5", "mod-6", "mod-7", "mod-8"]

DEFAULT_PROGRESS = {
    "user_id": "default",
    "completed_modules": [],
    "current_module": "mod-1",
    "test_scores": {},
    "conversation_sessions": 0,
    "total_practice_time": 0,
}

async def _get_or_create(user_id: str):
    db = await get_db()
    col = db["progress"]
    doc = await col.find_one({"user_id": user_id})
    if not doc:
        doc = dict(DEFAULT_PROGRESS, user_id=user_id)
        await col.insert_one(doc)
    doc.pop("_id", None)
    return doc

@router.get("/{user_id}")
async def get_progress(user_id: str = "default"):
    return await _get_or_create(user_id)

@router.post("/{user_id}/complete-module/{module_id}")
async def complete_module(user_id: str, module_id: str):
    db = await get_db()
    col = db["progress"]
    doc = await _get_or_create(user_id)

    completed = list(doc.get("completed_modules", []))
    if module_id not in completed:
        completed.append(module_id)

    current_idx = MODULES_ORDER.index(module_id) if module_id in MODULES_ORDER else -1
    next_module = MODULES_ORDER[current_idx + 1] if current_idx < len(MODULES_ORDER) - 1 else doc["current_module"]

    await col.update_one(
        {"user_id": user_id},
        {"$set": {"completed_modules": completed, "current_module": next_module}},
        upsert=True,
    )
    return await _get_or_create(user_id)

@router.post("/{user_id}/update-score")
async def update_test_score(user_id: str, module_id: str, score: float):
    db = await get_db()
    col = db["progress"]
    await _get_or_create(user_id)
    await col.update_one(
        {"user_id": user_id},
        {"$set": {f"test_scores.{module_id}": score}},
        upsert=True,
    )
    return await _get_or_create(user_id)

@router.post("/{user_id}/practice-session")
async def record_practice_session(user_id: str, duration_seconds: int):
    db = await get_db()
    col = db["progress"]
    await _get_or_create(user_id)
    await col.update_one(
        {"user_id": user_id},
        {"$inc": {"conversation_sessions": 1, "total_practice_time": duration_seconds}},
        upsert=True,
    )
    return await _get_or_create(user_id)

@router.get("/{user_id}/recommendations")
async def get_recommendations(user_id: str = "default"):
    doc = await _get_or_create(user_id)

    completed = [MODULE_MAP.get(m, m) for m in doc.get("completed_modules", [])]
    current = MODULE_MAP.get(doc.get("current_module", "mod-1"), doc.get("current_module", "mod-1"))

    low_scores = [
        MODULE_MAP.get(k, k)
        for k, v in doc.get("test_scores", {}).items()
        if v < 0.7
    ]

    return {
        "current_module": current,
        "completed_modules": completed,
        "modules_to_review": low_scores,
        "practice_sessions": doc.get("conversation_sessions", 0),
        "total_practice_minutes": doc.get("total_practice_time", 0) // 60,
        "next_recommendation": f"Study {current}" if current not in completed else "Review completed modules",
    }

@auth_router.get("/me")
async def get_my_progress(user: dict = Depends(get_current_user)):
    return await _get_or_create(str(user["_id"]))

@auth_router.post("/me/complete-module/{module_id}")
async def complete_my_module(module_id: str, user: dict = Depends(get_current_user)):
    uid = str(user["_id"])
    db = await get_db()
    col = db["progress"]
    doc = await _get_or_create(uid)

    completed = list(doc.get("completed_modules", []))
    if module_id not in completed:
        completed.append(module_id)

    current_idx = MODULES_ORDER.index(module_id) if module_id in MODULES_ORDER else -1
    next_module = MODULES_ORDER[current_idx + 1] if current_idx < len(MODULES_ORDER) - 1 else doc["current_module"]

    await col.update_one(
        {"user_id": uid},
        {"$set": {"completed_modules": completed, "current_module": next_module}},
        upsert=True,
    )
    return await _get_or_create(uid)

@auth_router.post("/me/update-score")
async def update_my_score(body: ScoreUpdate, user: dict = Depends(get_current_user)):
    uid = str(user["_id"])
    db = await get_db()
    col = db["progress"]
    await _get_or_create(uid)
    await col.update_one(
        {"user_id": uid},
        {"$set": {f"test_scores.{body.module_id}": body.score}},
        upsert=True,
    )
    return await _get_or_create(uid)

@auth_router.post("/me/practice-session")
async def record_my_session(body: SessionRecord, user: dict = Depends(get_current_user)):
    uid = str(user["_id"])
    db = await get_db()
    col = db["progress"]
    await _get_or_create(uid)
    await col.update_one(
        {"user_id": uid},
        {"$inc": {"conversation_sessions": 1, "total_practice_time": body.duration_seconds}},
        upsert=True,
    )
    return await _get_or_create(uid)

@auth_router.get("/me/recommendations")
async def my_recommendations(user: dict = Depends(get_current_user)):
    doc = await _get_or_create(str(user["_id"]))

    completed = [MODULE_MAP.get(m, m) for m in doc.get("completed_modules", [])]
    current = MODULE_MAP.get(doc.get("current_module", "mod-1"), doc.get("current_module", "mod-1"))

    low_scores = [
        MODULE_MAP.get(k, k)
        for k, v in doc.get("test_scores", {}).items()
        if v < 0.7
    ]

    return {
        "current_module": current,
        "completed_modules": completed,
        "modules_to_review": low_scores,
        "practice_sessions": doc.get("conversation_sessions", 0),
        "total_practice_minutes": doc.get("total_practice_time", 0) // 60,
        "next_recommendation": f"Study {current}" if current not in completed else "Review completed modules",
    }

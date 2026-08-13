from fastapi import FastAPI, APIRouter, HTTPException, Depends, Header
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
import secrets
import random
import string
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional
import uuid
from datetime import datetime, timezone, timedelta
from passlib.context import CryptContext
import jwt

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

JWT_SECRET = os.environ.get('JWT_SECRET', 'dev-secret')
JWT_ALGO = 'HS256'
JWT_EXP_DAYS = 30

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

app = FastAPI()
api_router = APIRouter(prefix="/api")


# ---------- Helpers ----------
def now_iso():
    return datetime.now(timezone.utc).isoformat()


def make_token(user_id: str):
    payload = {
        "sub": user_id,
        "exp": datetime.now(timezone.utc) + timedelta(days=JWT_EXP_DAYS),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGO)


def gen_license_key():
    seg = lambda: "".join(random.choices(string.ascii_uppercase + string.digits, k=4))
    return f"KENNY-{seg()}-{seg()}-{seg()}"


def public_user(u: dict):
    return {
        "id": u["id"],
        "name": u.get("name"),
        "email": u.get("email"),
        "telegram": u.get("telegram"),
        "created_at": u.get("created_at"),
    }


async def get_current_user(authorization: Optional[str] = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        return None
    token = authorization.split(" ", 1)[1]
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGO])
        user = await db.users.find_one({"id": payload.get("sub")})
        return user
    except Exception:
        return None


async def require_user(authorization: Optional[str] = Header(None)):
    user = await get_current_user(authorization)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return user


# ---------- Models ----------
class SignupInput(BaseModel):
    name: str
    email: Optional[str] = None
    telegram: Optional[str] = None
    password: str


class LoginInput(BaseModel):
    identifier: str  # email or telegram
    password: str


class OrderItem(BaseModel):
    projectId: str
    project: str
    planId: str
    plan: str
    duration: str
    inr: int
    usd: int


class OrderInput(BaseModel):
    telegram: str
    email: Optional[str] = None
    method: str = "upi"
    currency: str = "inr"
    items: List[OrderItem]


class FeedbackInput(BaseModel):
    name: str
    rating: int = Field(ge=1, le=5)
    message: str


# ---------- Routes ----------
@api_router.get("/")
async def root():
    return {"message": "KennyPvtHax API online"}


@api_router.post("/auth/signup")
async def signup(data: SignupInput):
    email = (data.email or "").strip().lower() or None
    telegram = (data.telegram or "").strip() or None
    if telegram and not telegram.startswith("@"):
        telegram = "@" + telegram
    if not email and not telegram:
        raise HTTPException(status_code=400, detail="Provide an email or Telegram username")
    if len(data.password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters")

    query = {"$or": []}
    if email:
        query["$or"].append({"email": email})
    if telegram:
        query["$or"].append({"telegram": telegram})
    existing = await db.users.find_one(query)
    if existing:
        raise HTTPException(status_code=409, detail="Account already exists with this email/Telegram")

    user = {
        "id": str(uuid.uuid4()),
        "name": data.name.strip(),
        "email": email,
        "telegram": telegram,
        "password_hash": pwd_context.hash(data.password),
        "created_at": now_iso(),
    }
    await db.users.insert_one(user)
    return {"token": make_token(user["id"]), "user": public_user(user)}


@api_router.post("/auth/login")
async def login(data: LoginInput):
    ident = data.identifier.strip()
    ident_l = ident.lower()
    tg = ident if ident.startswith("@") else "@" + ident
    user = await db.users.find_one({"$or": [{"email": ident_l}, {"telegram": ident}, {"telegram": tg}]})
    if not user or not pwd_context.verify(data.password, user.get("password_hash", "")):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"token": make_token(user["id"]), "user": public_user(user)}


@api_router.get("/auth/me")
async def me(user=Depends(require_user)):
    return {"user": public_user(user)}


@api_router.post("/orders")
async def create_order(data: OrderInput, current=Depends(get_current_user)):
    if not data.items:
        raise HTTPException(status_code=400, detail="No items in order")
    telegram = data.telegram.strip()
    if telegram and not telegram.startswith("@"):
        telegram = "@" + telegram

    keys = []
    for it in data.items:
        keys.append({
            "projectId": it.projectId,
            "project": it.project,
            "plan": it.plan,
            "duration": it.duration,
            "key": gen_license_key(),
        })

    total_inr = sum(i.inr for i in data.items)
    total_usd = sum(i.usd for i in data.items)

    order = {
        "id": str(uuid.uuid4()),
        "user_id": current["id"] if current else None,
        "telegram": telegram,
        "email": (data.email or "").strip() or None,
        "method": data.method,
        "currency": data.currency,
        "items": [i.dict() for i in data.items],
        "keys": keys,
        "total_inr": total_inr,
        "total_usd": total_usd,
        "status": "paid",           # payment mocked
        "delivered": False,          # telegram bot delivery pending
        "created_at": now_iso(),
    }
    await db.orders.insert_one(order)
    order.pop("_id", None)
    return order


@api_router.get("/orders/me")
async def my_orders(user=Depends(require_user)):
    cursor = db.orders.find({"user_id": user["id"]}).sort("created_at", -1)
    orders = await cursor.to_list(200)
    for o in orders:
        o.pop("_id", None)
    return {"orders": orders}


@api_router.post("/feedback")
async def create_feedback(data: FeedbackInput, current=Depends(get_current_user)):
    fb = {
        "id": str(uuid.uuid4()),
        "user_id": current["id"] if current else None,
        "name": data.name.strip() or "Anonymous",
        "rating": data.rating,
        "message": data.message.strip(),
        "approved": True,  # auto-approve for demo
        "created_at": now_iso(),
    }
    await db.feedback.insert_one(fb)
    fb.pop("_id", None)
    return fb


@api_router.get("/feedback")
async def list_feedback():
    cursor = db.feedback.find({"approved": True}).sort("created_at", -1)
    items = await cursor.to_list(50)
    for f in items:
        f.pop("_id", None)
    return {"feedback": items}


app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


@app.on_event("startup")
async def seed_feedback():
    count = await db.feedback.count_documents({})
    if count == 0:
        seed = [
            {"id": str(uuid.uuid4()), "user_id": None, "name": "ShadowKingBGMI", "rating": 5, "message": "Frozen Fire's hide-ESP-while-recording is unreal. Streamed a whole session, zero flags.", "approved": True, "created_at": now_iso()},
            {"id": str(uuid.uuid4()), "user_id": None, "name": "AceOfConqueror", "rating": 5, "message": "Got my key on Telegram in under a minute. OG Cheats runs buttery smooth on my device.", "approved": True, "created_at": now_iso()},
            {"id": str(uuid.uuid4()), "user_id": None, "name": "NeonReaper", "rating": 4, "message": "Kenny Admin is pure chaos in the best way. Insane for demonstration lobbies.", "approved": True, "created_at": now_iso()},
            {"id": str(uuid.uuid4()), "user_id": None, "name": "SilentStormX", "rating": 5, "message": "Patched within hours of the last BGMI update. Support on Telegram is legit 24/7.", "approved": True, "created_at": now_iso()},
        ]
        await db.feedback.insert_many(seed)


@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()

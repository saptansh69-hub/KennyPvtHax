from fastapi import FastAPI, APIRouter, HTTPException, Depends, Header
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import asyncio
import logging
import random
import secrets
import string
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional
import uuid
from datetime import datetime, timezone, timedelta
from passlib.context import CryptContext
import jwt
import requests

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

JWT_SECRET = os.environ.get('JWT_SECRET', 'dev-secret')
JWT_ALGO = 'HS256'
JWT_EXP_DAYS = 30

# Third-party config (safe fallbacks when unset)
KEYAUTH_SELLER_KEY = os.environ.get('KEYAUTH_SELLER_KEY', '').strip()
KEYAUTH_MASK = os.environ.get('KEYAUTH_MASK', 'KENNY-******-******').strip()
KEYAUTH_LEVEL = os.environ.get('KEYAUTH_LEVEL', '1').strip()
TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN', '').strip()
TELEGRAM_ADMIN_CHAT_ID = os.environ.get('TELEGRAM_ADMIN_CHAT_ID', '').strip()
ADMIN_EMAILS = [e.strip().lower() for e in os.environ.get('ADMIN_EMAILS', '').split(',') if e.strip()]
ADMIN_TELEGRAMS = [t.strip() if t.strip().startswith('@') else '@' + t.strip()
                   for t in os.environ.get('ADMIN_TELEGRAMS', '@CrimeCell').split(',') if t.strip()]

# Plan -> expiry days
PLAN_DAYS = {"1day": 1, "7day": 7, "month": 30, "admin-week": 7}

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

app = FastAPI()
api_router = APIRouter(prefix="/api")
logger = logging.getLogger(__name__)


# ---------- Helpers ----------
def now_iso():
    return datetime.now(timezone.utc).isoformat()


def make_token(user_id: str):
    payload = {"sub": user_id, "exp": datetime.now(timezone.utc) + timedelta(days=JWT_EXP_DAYS)}
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGO)


def local_license_key():
    seg = lambda n=6: "".join(random.choices(string.ascii_uppercase + string.digits, k=n))
    return f"KENNY-{seg()}-{seg()}"


def is_admin(u: dict) -> bool:
    if not u:
        return False
    email = (u.get("email") or "").lower()
    tg = u.get("telegram") or ""
    return email in ADMIN_EMAILS or tg in ADMIN_TELEGRAMS


def public_user(u: dict):
    return {
        "id": u["id"], "name": u.get("name"), "email": u.get("email"),
        "telegram": u.get("telegram"), "created_at": u.get("created_at"),
        "is_admin": is_admin(u),
    }


def _keyauth_generate_sync(expiry_days: int, note: str) -> Optional[str]:
    """Generate a real license via KeyAuth Seller API. Returns key or None."""
    if not KEYAUTH_SELLER_KEY:
        return None
    try:
        params = {
            "sellerkey": KEYAUTH_SELLER_KEY, "type": "add", "format": "json",
            "expiry": str(expiry_days), "mask": KEYAUTH_MASK, "level": KEYAUTH_LEVEL,
            "amount": "1", "note": note[:120],
        }
        r = requests.get("https://keyauth.win/api/seller/", params=params, timeout=15)
        data = r.json()
        if data.get("success") and data.get("key"):
            return data["key"]
        logger.warning("KeyAuth generate failed: %s", data.get("message"))
    except Exception as e:
        logger.warning("KeyAuth error: %s", e)
    return None


def _telegram_send_sync(text: str) -> bool:
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_ADMIN_CHAT_ID:
        return False
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        r = requests.post(url, json={"chat_id": TELEGRAM_ADMIN_CHAT_ID, "text": text,
                                     "parse_mode": "HTML", "disable_web_page_preview": True}, timeout=15)
        return r.ok and r.json().get("ok", False)
    except Exception as e:
        logger.warning("Telegram error: %s", e)
        return False


async def get_current_user(authorization: Optional[str] = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        return None
    token = authorization.split(" ", 1)[1]
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGO])
        return await db.users.find_one({"id": payload.get("sub")})
    except Exception:
        return None


async def require_user(authorization: Optional[str] = Header(None)):
    user = await get_current_user(authorization)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return user


async def require_admin(authorization: Optional[str] = Header(None)):
    user = await get_current_user(authorization)
    if not user or not is_admin(user):
        raise HTTPException(status_code=403, detail="Admin access required")
    return user


# ---------- Models ----------
class SignupInput(BaseModel):
    name: str
    email: Optional[str] = None
    telegram: Optional[str] = None
    password: str


class LoginInput(BaseModel):
    identifier: str
    password: str


class ForgotInput(BaseModel):
    identifier: str  # email or telegram


class ResetInput(BaseModel):
    token: str
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
    image: Optional[str] = None  # base64 data URL (optional screenshot)


# ---------- Routes ----------
@api_router.get("/")
async def root():
    return {"message": "KennyPvtHax API online"}


@api_router.get("/config")
async def config():
    return {
        "keyauth_enabled": bool(KEYAUTH_SELLER_KEY),
        "telegram_enabled": bool(TELEGRAM_BOT_TOKEN and TELEGRAM_ADMIN_CHAT_ID),
    }


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

    ors = []
    if email:
        ors.append({"email": email})
    if telegram:
        ors.append({"telegram": telegram})
    if await db.users.find_one({"$or": ors}):
        raise HTTPException(status_code=409, detail="Account already exists with this email/Telegram")

    user = {
        "id": str(uuid.uuid4()), "name": data.name.strip(), "email": email,
        "telegram": telegram, "password_hash": pwd_context.hash(data.password), "created_at": now_iso(),
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


@api_router.post("/auth/forgot")
async def forgot_password(data: ForgotInput):
    ident = data.identifier.strip()
    ident_l = ident.lower()
    tg = ident if ident.startswith("@") else "@" + ident
    user = await db.users.find_one({"$or": [{"email": ident_l}, {"telegram": ident}, {"telegram": tg}]})
    if not user:
        # Do not reveal existence; nothing to reset
        return {"found": False, "message": "If an account exists, a reset can be started."}

    token = secrets.token_urlsafe(24)
    reset = {
        "token": token,
        "user_id": user["id"],
        "expires_at": (datetime.now(timezone.utc) + timedelta(minutes=30)).isoformat(),
        "used": False,
        "created_at": now_iso(),
    }
    await db.password_resets.insert_one(reset)

    # Notify admin via Telegram if configured (so support can assist / audit)
    await asyncio.to_thread(
        _telegram_send_sync,
        f"<b>Password reset requested</b>\nUser: {user.get('email') or user.get('telegram')}",
    )

    # NOTE: In production this token would be emailed / Telegram-DMed to the user.
    # Delivery is MOCKED here, so we return it directly to complete the flow.
    return {"found": True, "reset_token": token, "delivery": "mocked"}


@api_router.post("/auth/reset")
async def reset_password(data: ResetInput):
    if len(data.password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters")
    reset = await db.password_resets.find_one({"token": data.token, "used": False})
    if not reset:
        raise HTTPException(status_code=400, detail="Invalid or already used reset link")
    if datetime.fromisoformat(reset["expires_at"]) < datetime.now(timezone.utc):
        raise HTTPException(status_code=400, detail="Reset link has expired")
    user = await db.users.find_one({"id": reset["user_id"]})
    if not user:
        raise HTTPException(status_code=404, detail="Account not found")

    await db.users.update_one({"id": user["id"]}, {"$set": {"password_hash": pwd_context.hash(data.password)}})
    await db.password_resets.update_one({"token": data.token}, {"$set": {"used": True}})
    return {"token": make_token(user["id"]), "user": public_user(user)}


@api_router.post("/orders")
async def create_order(data: OrderInput, current=Depends(get_current_user)):
    if not data.items:
        raise HTTPException(status_code=400, detail="No items in order")
    telegram = data.telegram.strip()
    if telegram and not telegram.startswith("@"):
        telegram = "@" + telegram

    keys = []
    for it in data.items:
        days = PLAN_DAYS.get(it.planId, 7)
        note = f"KennyPvtHax {it.project} {it.plan} -> {telegram}"
        key = await asyncio.to_thread(_keyauth_generate_sync, days, note)
        keys.append({
            "projectId": it.projectId, "project": it.project, "plan": it.plan,
            "duration": it.duration, "key": key or local_license_key(),
            "source": "keyauth" if key else "local",
        })

    total_inr = sum(i.inr for i in data.items)
    total_usd = sum(i.usd for i in data.items)

    order = {
        "id": str(uuid.uuid4()), "user_id": current["id"] if current else None,
        "telegram": telegram, "email": (data.email or "").strip() or None,
        "method": data.method, "currency": data.currency,
        "items": [i.dict() for i in data.items], "keys": keys,
        "total_inr": total_inr, "total_usd": total_usd,
        "status": "paid", "delivered": False, "created_at": now_iso(),
    }

    # Telegram notification / delivery to admin
    lines = [f"<b>New KennyPvtHax order</b>", f"Order: {order['id'][:8].upper()}",
             f"Buyer TG: {telegram}", f"Total: {'₹'+str(total_inr) if data.currency=='inr' else '$'+str(total_usd)}",
             f"Method: {data.method.upper()}", "", "<b>Keys:</b>"]
    for k in keys:
        lines.append(f"• {k['project']} — {k['plan']}: <code>{k['key']}</code>")
    delivered = await asyncio.to_thread(_telegram_send_sync, "\n".join(lines))
    order["delivered"] = delivered

    await db.orders.insert_one(order)
    order.pop("_id", None)
    return order


@api_router.get("/orders/me")
async def my_orders(user=Depends(require_user)):
    orders = await db.orders.find({"user_id": user["id"]}).sort("created_at", -1).to_list(200)
    for o in orders:
        o.pop("_id", None)
    return {"orders": orders}


@api_router.post("/feedback")
async def create_feedback(data: FeedbackInput, current=Depends(get_current_user)):
    image = data.image
    if image and len(image) > 4_000_000:  # ~4MB safety cap
        raise HTTPException(status_code=413, detail="Screenshot too large (max ~3MB)")
    fb = {
        "id": str(uuid.uuid4()), "user_id": current["id"] if current else None,
        "name": data.name.strip() or "Anonymous", "rating": data.rating,
        "message": data.message.strip(), "image": image if image and image.startswith("data:image") else None,
        "approved": True, "created_at": now_iso(),
    }
    await db.feedback.insert_one(fb)
    fb.pop("_id", None)
    return fb


@api_router.get("/feedback")
async def list_feedback():
    items = await db.feedback.find({"approved": True}).sort("created_at", -1).to_list(50)
    for f in items:
        f.pop("_id", None)
    return {"feedback": items}


# ---------- Admin ----------
@api_router.get("/admin/stats")
async def admin_stats(admin=Depends(require_admin)):
    orders = await db.orders.find().to_list(2000)
    revenue_inr = sum(o.get("total_inr", 0) for o in orders)
    revenue_usd = sum(o.get("total_usd", 0) for o in orders)
    keys_count = sum(len(o.get("keys", [])) for o in orders)
    return {
        "orders": len(orders), "users": await db.users.count_documents({}),
        "feedback": await db.feedback.count_documents({}),
        "keys_generated": keys_count, "revenue_inr": revenue_inr, "revenue_usd": revenue_usd,
        "delivered": sum(1 for o in orders if o.get("delivered")),
    }


@api_router.get("/admin/orders")
async def admin_orders(admin=Depends(require_admin)):
    orders = await db.orders.find().sort("created_at", -1).to_list(500)
    for o in orders:
        o.pop("_id", None)
    return {"orders": orders}


@api_router.get("/admin/feedback")
async def admin_feedback(admin=Depends(require_admin)):
    items = await db.feedback.find().sort("created_at", -1).to_list(500)
    for f in items:
        f.pop("_id", None)
    return {"feedback": items}


@api_router.delete("/admin/feedback/{fid}")
async def admin_delete_feedback(fid: str, admin=Depends(require_admin)):
    await db.feedback.delete_one({"id": fid})
    return {"deleted": True}


class KeyAuthGenInput(BaseModel):
    expiry_days: int = 7
    amount: int = 1
    note: Optional[str] = "manual"


@api_router.post("/admin/keyauth/generate")
async def admin_keyauth_generate(data: KeyAuthGenInput, admin=Depends(require_admin)):
    if not KEYAUTH_SELLER_KEY:
        raise HTTPException(status_code=400, detail="KeyAuth not configured (missing seller key)")
    keys = []
    for _ in range(max(1, min(data.amount, 20))):
        k = await asyncio.to_thread(_keyauth_generate_sync, data.expiry_days, data.note or "manual")
        if k:
            keys.append(k)
    if not keys:
        raise HTTPException(status_code=502, detail="KeyAuth did not return a key")
    return {"keys": keys}


app.include_router(api_router)

app.add_middleware(
    CORSMiddleware, allow_credentials=True, allow_origins=["*"],
    allow_methods=["*"], allow_headers=["*"],
)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


@app.on_event("startup")
async def seed_feedback():
    if await db.feedback.count_documents({}) == 0:
        seed = [
            {"id": str(uuid.uuid4()), "user_id": None, "name": "ShadowKingBGMI", "rating": 5, "image": None, "message": "Frozen Fire's hide-ESP-while-recording is unreal. Streamed a whole session, zero flags.", "approved": True, "created_at": now_iso()},
            {"id": str(uuid.uuid4()), "user_id": None, "name": "AceOfConqueror", "rating": 5, "image": None, "message": "Got my key on Telegram in under a minute. OG Cheats runs buttery smooth on my device.", "approved": True, "created_at": now_iso()},
            {"id": str(uuid.uuid4()), "user_id": None, "name": "NeonReaper", "rating": 4, "image": None, "message": "Kenny Admin is pure chaos in the best way. Insane for demonstration lobbies.", "approved": True, "created_at": now_iso()},
            {"id": str(uuid.uuid4()), "user_id": None, "name": "SilentStormX", "rating": 5, "image": None, "message": "Patched within hours of the last BGMI update. Support on Telegram is legit 24/7.", "approved": True, "created_at": now_iso()},
        ]
        await db.feedback.insert_many(seed)


@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()

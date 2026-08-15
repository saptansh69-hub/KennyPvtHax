from fastapi import FastAPI, APIRouter, HTTPException, Depends, Header, Request
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import ReturnDocument
import os
import asyncio
import logging
import secrets
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

mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

JWT_SECRET = os.environ.get('JWT_SECRET', 'dev-secret')
JWT_ALGO = 'HS256'
JWT_EXP_DAYS = 30

TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN', '').strip()
TELEGRAM_ADMIN_CHAT_ID = os.environ.get('TELEGRAM_ADMIN_CHAT_ID', '').strip()
PUBLIC_BASE_URL = os.environ.get('PUBLIC_BASE_URL', '').strip().rstrip('/')
ADMIN_EMAILS = [e.strip().lower() for e in os.environ.get('ADMIN_EMAILS', '').split(',') if e.strip()]
ADMIN_TELEGRAMS = [t.strip() if t.strip().startswith('@') else '@' + t.strip()
                   for t in os.environ.get('ADMIN_TELEGRAMS', '@CrimeCell').split(',') if t.strip()]

BOT_USERNAME = None  # resolved at startup

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


def norm_tg(t: Optional[str]) -> Optional[str]:
    if not t:
        return None
    t = t.strip()
    if not t:
        return None
    return t if t.startswith('@') else '@' + t


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


# --- Telegram ---
def _tg_send(chat_id, text: str) -> bool:
    if not TELEGRAM_BOT_TOKEN or not chat_id:
        return False
    try:
        r = requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
            json={"chat_id": chat_id, "text": text, "parse_mode": "HTML", "disable_web_page_preview": True},
            timeout=15,
        )
        return r.ok and r.json().get("ok", False)
    except Exception as e:
        logger.warning("Telegram send error: %s", e)
        return False


def _order_keys_text(order: dict) -> str:
    lines = ["<b>KennyPvtHax — your license key(s)</b>",
             f"Order #{order['id'][:8].upper()}", ""]
    for k in order.get("keys", []):
        val = k.get("key") or "⏳ processing (restocking soon)"
        lines.append(f"• <b>{k['project']}</b> — {k['plan']} ({k['duration']})\n  <code>{val}</code>")
    lines.append("\nKeep your key private. Support: @CrimeCell")
    return "\n".join(lines)


async def deliver_order_to_chat(order: dict, chat_id) -> bool:
    ok = await asyncio.to_thread(_tg_send, chat_id, _order_keys_text(order))
    if ok:
        await db.orders.update_one({"id": order["id"]}, {"$set": {"delivered": True, "buyer_chat_id": chat_id}})
    return ok


async def get_current_user(authorization: Optional[str] = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        return None
    try:
        payload = jwt.decode(authorization.split(" ", 1)[1], JWT_SECRET, algorithms=[JWT_ALGO])
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


async def assign_key(project_id: str, plan_id: str) -> Optional[str]:
    """Atomically pull an unused key from inventory, best match first."""
    queries = [
        {"projectId": project_id, "planId": plan_id, "used": False},
        {"projectId": project_id, "planId": None, "used": False},
        {"projectId": None, "planId": None, "used": False},
    ]
    for q in queries:
        doc = await db.keys_inventory.find_one_and_update(
            q, {"$set": {"used": True, "assigned_at": now_iso()}}, return_document=ReturnDocument.AFTER
        )
        if doc:
            return doc["key"]
    return None


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
    identifier: str


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
    image: Optional[str] = None


class BulkKeysInput(BaseModel):
    projectId: Optional[str] = None
    planId: Optional[str] = None
    keys: List[str]


# ---------- Routes ----------
@api_router.get("/")
async def root():
    return {"message": "KennyPvtHax API online"}


@api_router.get("/config")
async def config():
    return {
        "telegram_enabled": bool(TELEGRAM_BOT_TOKEN),
        "bot_username": BOT_USERNAME,
    }


@api_router.post("/auth/signup")
async def signup(data: SignupInput):
    email = (data.email or "").strip().lower() or None
    telegram = norm_tg(data.telegram)
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
    user = {"id": str(uuid.uuid4()), "name": data.name.strip(), "email": email, "telegram": telegram,
            "password_hash": pwd_context.hash(data.password), "created_at": now_iso()}
    await db.users.insert_one(user)
    return {"token": make_token(user["id"]), "user": public_user(user)}


@api_router.post("/auth/login")
async def login(data: LoginInput):
    ident = data.identifier.strip()
    user = await db.users.find_one({"$or": [{"email": ident.lower()}, {"telegram": ident}, {"telegram": norm_tg(ident)}]})
    if not user or not pwd_context.verify(data.password, user.get("password_hash", "")):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"token": make_token(user["id"]), "user": public_user(user)}


@api_router.get("/auth/me")
async def me(user=Depends(require_user)):
    return {"user": public_user(user)}


@api_router.post("/auth/forgot")
async def forgot_password(data: ForgotInput):
    ident = data.identifier.strip()
    user = await db.users.find_one({"$or": [{"email": ident.lower()}, {"telegram": ident}, {"telegram": norm_tg(ident)}]})
    if not user:
        return {"found": False, "message": "If an account exists, a reset can be started."}
    token = secrets.token_urlsafe(24)
    await db.password_resets.insert_one({
        "token": token, "user_id": user["id"],
        "expires_at": (datetime.now(timezone.utc) + timedelta(minutes=30)).isoformat(),
        "used": False, "created_at": now_iso(),
    })
    # Try to deliver the reset code via Telegram if the user has DM'd the bot before
    tg = user.get("telegram")
    if tg:
        chat = await db.telegram_chats.find_one({"username": tg.lower()})
        if chat and _tg_send(chat["chat_id"],
                             f"<b>KennyPvtHax password reset</b>\nYour reset code:\n<code>{token}</code>\n\nEnter it on the site to set a new password. Expires in 30 min."):
            return {"found": True, "delivery": "telegram"}
    # Fallback (delivery mocked): return token so the flow can complete
    return {"found": True, "reset_token": token, "delivery": "mocked"}


@api_router.post("/auth/reset")
async def reset_password(data: ResetInput):
    if len(data.password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters")
    reset = await db.password_resets.find_one({"token": data.token.strip(), "used": False})
    if not reset:
        raise HTTPException(status_code=400, detail="Invalid or already used reset link")
    if datetime.fromisoformat(reset["expires_at"]) < datetime.now(timezone.utc):
        raise HTTPException(status_code=400, detail="Reset link has expired")
    user = await db.users.find_one({"id": reset["user_id"]})
    if not user:
        raise HTTPException(status_code=404, detail="Account not found")
    await db.users.update_one({"id": user["id"]}, {"$set": {"password_hash": pwd_context.hash(data.password)}})
    await db.password_resets.update_one({"token": data.token.strip()}, {"$set": {"used": True}})
    return {"token": make_token(user["id"]), "user": public_user(user)}


@api_router.post("/orders")
async def create_order(data: OrderInput, current=Depends(get_current_user)):
    if not data.items:
        raise HTTPException(status_code=400, detail="No items in order")
    telegram = norm_tg(data.telegram)

    keys = []
    out_of_stock = False
    for it in data.items:
        assigned = await assign_key(it.projectId, it.planId)
        if not assigned:
            out_of_stock = True
        keys.append({"projectId": it.projectId, "project": it.project, "plan": it.plan,
                     "duration": it.duration, "key": assigned,
                     "source": "inventory" if assigned else "pending"})

    total_inr = sum(i.inr for i in data.items)
    total_usd = sum(i.usd for i in data.items)
    order = {
        "id": str(uuid.uuid4()), "user_id": current["id"] if current else None,
        "telegram": telegram, "email": (data.email or "").strip() or None,
        "method": data.method, "currency": data.currency,
        "items": [i.dict() for i in data.items], "keys": keys,
        "total_inr": total_inr, "total_usd": total_usd,
        "status": "paid", "delivered": False, "stock_ok": not out_of_stock, "created_at": now_iso(),
    }
    await db.orders.insert_one(order)
    order.pop("_id", None)

    deep_link = f"https://t.me/{BOT_USERNAME}?start={order['id']}" if BOT_USERNAME else None

    # Auto-deliver if buyer already DM'd the bot; else they use the deep link
    if telegram:
        chat = await db.telegram_chats.find_one({"username": telegram.lower()})
        if chat:
            await deliver_order_to_chat(order, chat["chat_id"])
            order["delivered"] = True

    # Notify admin/owner
    if TELEGRAM_ADMIN_CHAT_ID:
        admin_lines = [f"<b>New order</b> #{order['id'][:8].upper()}", f"Buyer: {telegram}",
                       f"Total: {'₹'+str(total_inr) if data.currency=='inr' else '$'+str(total_usd)}",
                       f"Stock: {'OK' if not out_of_stock else 'OUT OF STOCK ⚠️'}"]
        await asyncio.to_thread(_tg_send, TELEGRAM_ADMIN_CHAT_ID, "\n".join(admin_lines))

    order["telegram_deeplink"] = deep_link
    order["bot_username"] = BOT_USERNAME
    return order


@api_router.get("/orders/me")
async def my_orders(user=Depends(require_user)):
    orders = await db.orders.find({"user_id": user["id"]}).sort("created_at", -1).to_list(200)
    for o in orders:
        o.pop("_id", None)
        o["bot_username"] = BOT_USERNAME
        o["telegram_deeplink"] = f"https://t.me/{BOT_USERNAME}?start={o['id']}" if BOT_USERNAME else None
    return {"orders": orders}


@api_router.post("/feedback")
async def create_feedback(data: FeedbackInput, current=Depends(get_current_user)):
    if data.image and len(data.image) > 4_000_000:
        raise HTTPException(status_code=413, detail="Screenshot too large (max ~3MB)")
    fb = {"id": str(uuid.uuid4()), "user_id": current["id"] if current else None,
          "name": data.name.strip() or "Anonymous", "rating": data.rating,
          "message": data.message.strip(),
          "image": data.image if data.image and data.image.startswith("data:image") else None,
          "approved": True, "created_at": now_iso()}
    await db.feedback.insert_one(fb)
    fb.pop("_id", None)
    return fb


@api_router.get("/feedback")
async def list_feedback():
    items = await db.feedback.find({"approved": True}).sort("created_at", -1).to_list(50)
    for f in items:
        f.pop("_id", None)
    return {"feedback": items}


# ---------- Telegram webhook ----------
@api_router.post("/telegram/webhook")
async def telegram_webhook(request: Request):
    try:
        data = await request.json()
    except Exception:
        return {"ok": True}
    msg = data.get("message") or data.get("edited_message")
    if not msg:
        return {"ok": True}
    chat_id = (msg.get("chat") or {}).get("id")
    username = (msg.get("from") or {}).get("username")
    text = (msg.get("text") or "").strip()

    if username and chat_id:
        await db.telegram_chats.update_one(
            {"username": "@" + username.lower()},
            {"$set": {"chat_id": chat_id, "updated_at": now_iso()}}, upsert=True)

    if text.startswith("/start"):
        parts = text.split(maxsplit=1)
        payload = parts[1].strip() if len(parts) > 1 else ""
        if payload:
            order = await db.orders.find_one({"id": payload})
            if order:
                order.pop("_id", None)
                ok = await deliver_order_to_chat(order, chat_id)
                if not ok:
                    await asyncio.to_thread(_tg_send, chat_id, "Could not fetch your key. Please contact @CrimeCell.")
            else:
                await asyncio.to_thread(_tg_send, chat_id, "Welcome to <b>KennyPvtHax</b>! Order not found — contact @CrimeCell for help.")
        else:
            await asyncio.to_thread(_tg_send, chat_id,
                "Welcome to <b>KennyPvtHax</b>! Buy a key on the site, then tap the delivery link to receive it here instantly.")
    return {"ok": True}


# ---------- Admin ----------
@api_router.get("/admin/stats")
async def admin_stats(admin=Depends(require_admin)):
    orders = await db.orders.find().to_list(2000)
    return {
        "orders": len(orders), "users": await db.users.count_documents({}),
        "feedback": await db.feedback.count_documents({}),
        "keys_available": await db.keys_inventory.count_documents({"used": False}),
        "keys_used": await db.keys_inventory.count_documents({"used": True}),
        "revenue_inr": sum(o.get("total_inr", 0) for o in orders),
        "revenue_usd": sum(o.get("total_usd", 0) for o in orders),
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


@api_router.post("/admin/keys/bulk")
async def admin_add_keys(data: BulkKeysInput, admin=Depends(require_admin)):
    project_id = data.projectId or None
    plan_id = data.planId or None
    added, skipped = 0, 0
    for raw in data.keys:
        k = raw.strip()
        if not k:
            continue
        if await db.keys_inventory.find_one({"key": k}):
            skipped += 1
            continue
        await db.keys_inventory.insert_one({
            "id": str(uuid.uuid4()), "key": k, "projectId": project_id, "planId": plan_id,
            "used": False, "created_at": now_iso(),
        })
        added += 1
    return {"added": added, "skipped": skipped}


@api_router.get("/admin/keys/summary")
async def admin_keys_summary(admin=Depends(require_admin)):
    pipeline = [{"$group": {"_id": {"projectId": "$projectId", "planId": "$planId", "used": "$used"},
                            "count": {"$sum": 1}}}]
    rows = await db.keys_inventory.aggregate(pipeline).to_list(500)
    buckets = {}
    for r in rows:
        key = f"{r['_id'].get('projectId') or 'any'}|{r['_id'].get('planId') or 'any'}"
        b = buckets.setdefault(key, {"projectId": r['_id'].get('projectId') or 'any',
                                     "planId": r['_id'].get('planId') or 'any', "available": 0, "used": 0})
        b["used" if r["_id"].get("used") else "available"] += r["count"]
    return {"buckets": list(buckets.values()),
            "total_available": await db.keys_inventory.count_documents({"used": False}),
            "total_used": await db.keys_inventory.count_documents({"used": True})}


app.include_router(api_router)

app.add_middleware(CORSMiddleware, allow_credentials=True, allow_origins=["*"],
                   allow_methods=["*"], allow_headers=["*"])

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


@app.on_event("startup")
async def startup_tasks():
    global BOT_USERNAME
    # seed feedback
    if await db.feedback.count_documents({}) == 0:
        seed = [
            {"id": str(uuid.uuid4()), "user_id": None, "name": "ShadowKingBGMI", "rating": 5, "image": None, "message": "Frozen Fire's hide-ESP-while-recording is unreal. Streamed a whole session, zero flags.", "approved": True, "created_at": now_iso()},
            {"id": str(uuid.uuid4()), "user_id": None, "name": "AceOfConqueror", "rating": 5, "image": None, "message": "Got my key on Telegram in under a minute. OG Cheats runs buttery smooth on my device.", "approved": True, "created_at": now_iso()},
            {"id": str(uuid.uuid4()), "user_id": None, "name": "NeonReaper", "rating": 4, "image": None, "message": "Kenny Admin is pure chaos in the best way. Insane for demonstration lobbies.", "approved": True, "created_at": now_iso()},
            {"id": str(uuid.uuid4()), "user_id": None, "name": "SilentStormX", "rating": 5, "image": None, "message": "Patched within hours of the last BGMI update. Support on Telegram is legit 24/7.", "approved": True, "created_at": now_iso()},
        ]
        await db.feedback.insert_many(seed)

    if TELEGRAM_BOT_TOKEN:
        try:
            me = await asyncio.to_thread(lambda: requests.get(
                f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getMe", timeout=10).json())
            if me.get("ok"):
                BOT_USERNAME = me["result"]["username"]
            if PUBLIC_BASE_URL:
                hook = f"{PUBLIC_BASE_URL}/api/telegram/webhook"
                res = await asyncio.to_thread(lambda: requests.get(
                    f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/setWebhook",
                    params={"url": hook}, timeout=10).json())
                logger.info("Telegram setWebhook -> %s (%s)", res.get("ok"), hook)
        except Exception as e:
            logger.warning("Telegram startup error: %s", e)


@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()

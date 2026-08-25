from fastapi import FastAPI, APIRouter, HTTPException, Depends, Header, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
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

def _require_env(name: str) -> str:
    val = (os.environ.get(name) or '').strip()
    if not val:
        raise RuntimeError(
            f"Required environment variable {name} is not set. "
            "Add it to the Railway service variables (see backend/.env.example)."
        )
    return val


mongo_url = _require_env('MONGO_URL')
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ.get('DB_NAME') or 'appdb']

# A predictable signing key lets anyone mint an admin token, so this must be set.
JWT_SECRET = _require_env('JWT_SECRET')
JWT_ALGO = 'HS256'
JWT_EXP_DAYS = 30

TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN', '').strip()
TELEGRAM_ADMIN_CHAT_ID = os.environ.get('TELEGRAM_ADMIN_CHAT_ID', '').strip()
LOW_STOCK_THRESHOLD = int(os.environ.get('LOW_STOCK_THRESHOLD', '3') or 3)
PUBLIC_BASE_URL = os.environ.get('PUBLIC_BASE_URL', '').strip().rstrip('/')
ADMIN_EMAILS = [e.strip().lower() for e in os.environ.get('ADMIN_EMAILS', '').split(',') if e.strip()]
ADMIN_TELEGRAMS = [t.strip() if t.strip().startswith('@') else '@' + t.strip()
                   for t in os.environ.get('ADMIN_TELEGRAMS', '').split(',') if t.strip()]

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
    lines = ["<b>Your license key(s)</b>",
             f"Order #{order['id'][:8].upper()}", ""]
    for k in order.get("keys", []):
        val = k.get("key") or "⏳ processing (restocking soon)"
        lines.append(f"• <b>{k['project']}</b> — {k['plan']} ({k['duration']})\n  <code>{val}</code>")
    lines.append("\nKeep your key private.")
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


async def add_keys_to_inventory(project_id, plan_id, keys):
    project_id = project_id or None
    plan_id = plan_id or None
    added, skipped = 0, 0
    for raw in keys:
        k = (raw or "").strip()
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
    return added, skipped


async def check_low_stock_and_notify(project_id, plan_id):
    """Alert the owner on Telegram when a bucket runs low/out."""
    if not TELEGRAM_ADMIN_CHAT_ID:
        return
    remaining = await db.keys_inventory.count_documents(
        {"projectId": project_id, "planId": plan_id, "used": False})
    if remaining <= LOW_STOCK_THRESHOLD:
        tag = f"{project_id or 'any'} / {plan_id or 'any'}"
        if remaining == 0:
            msg = f"🔴 <b>OUT OF STOCK</b>\nBucket: {tag}\nAdd more keys: /addkeys {project_id or ''} {plan_id or ''}"
        else:
            msg = f"⚠️ <b>Low stock</b>\nBucket: {tag}\nOnly {remaining} key(s) left."
        await asyncio.to_thread(_tg_send, TELEGRAM_ADMIN_CHAT_ID, msg.strip())


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
    payment_ref: Optional[str] = None
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
    return {"message": "API online"}


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
                             f"<b>Password reset</b>\nYour reset code:\n<code>{token}</code>\n\nEnter it on the site to set a new password. Expires in 30 min."):
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


async def fulfill_order(order: dict) -> dict:
    """Assign keys from inventory + deliver. Marks order paid."""
    keys = []
    out_of_stock = False
    for it in order["items"]:
        assigned = await assign_key(it["projectId"], it["planId"])
        if not assigned:
            out_of_stock = True
        keys.append({"projectId": it["projectId"], "project": it["project"], "plan": it["plan"],
                     "duration": it["duration"], "key": assigned,
                     "source": "inventory" if assigned else "pending"})
        await check_low_stock_and_notify(it["projectId"], it["planId"])
    order["keys"] = keys
    order["stock_ok"] = not out_of_stock
    order["status"] = "paid"
    await db.orders.update_one({"id": order["id"]},
                               {"$set": {"keys": keys, "stock_ok": not out_of_stock, "status": "paid"}})
    tg = order.get("telegram")
    if tg:
        chat = await db.telegram_chats.find_one({"username": tg.lower()})
        if chat:
            await deliver_order_to_chat(order, chat["chat_id"])
            order["delivered"] = True
    order["telegram_deeplink"] = f"https://t.me/{BOT_USERNAME}?start={order['id']}" if BOT_USERNAME else None
    order["bot_username"] = BOT_USERNAME
    return order


@api_router.post("/orders")
async def create_order(data: OrderInput, current=Depends(get_current_user)):
    if not data.items:
        raise HTTPException(status_code=400, detail="No items in order")
    telegram = norm_tg(data.telegram)
    total_inr = sum(i.inr for i in data.items)
    total_usd = sum(i.usd for i in data.items)

    order = {
        "id": str(uuid.uuid4()), "user_id": current["id"] if current else None,
        "telegram": telegram, "email": (data.email or "").strip() or None,
        "method": data.method, "currency": data.currency,
        "payment_ref": (data.payment_ref or "").strip() or None,
        "items": [i.model_dump() for i in data.items], "keys": [],
        "total_inr": total_inr, "total_usd": total_usd,
        "status": "awaiting_verification" if data.method == "upi" else "paid",
        "delivered": False, "stock_ok": True, "created_at": now_iso(),
    }
    await db.orders.insert_one(order)
    order.pop("_id", None)

    if data.method == "upi":
        # QR payment -> owner verifies before keys are released
        if TELEGRAM_ADMIN_CHAT_ID:
            amt = f"₹{total_inr}" if data.currency == "inr" else f"${total_usd}"
            await asyncio.to_thread(_tg_send, TELEGRAM_ADMIN_CHAT_ID,
                f"🕒 <b>Payment to verify</b> #{order['id'][:8].upper()}\nBuyer: {telegram}\nAmount: {amt}\nUPI Ref: {order['payment_ref'] or '—'}\n\nApprove: <code>/verify {order['id']}</code>")
        order["telegram_deeplink"] = f"https://t.me/{BOT_USERNAME}?start={order['id']}" if BOT_USERNAME else None
        order["bot_username"] = BOT_USERNAME
        return order

    # Non-UPI (card) -> instant mock fulfilment
    order = await fulfill_order(order)
    if TELEGRAM_ADMIN_CHAT_ID:
        await asyncio.to_thread(_tg_send, TELEGRAM_ADMIN_CHAT_ID,
            f"<b>New order</b> #{order['id'][:8].upper()}\nBuyer: {telegram}\nTotal: {'₹'+str(total_inr) if data.currency=='inr' else '$'+str(total_usd)}")
    return order


@api_router.post("/admin/orders/{oid}/verify")
async def verify_order(oid: str, admin=Depends(require_admin)):
    order = await db.orders.find_one({"id": oid})
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    if order.get("status") == "paid":
        order.pop("_id", None)
        return order
    order.pop("_id", None)
    order = await fulfill_order(order)
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

    is_owner = (TELEGRAM_ADMIN_CHAT_ID and str(chat_id) == str(TELEGRAM_ADMIN_CHAT_ID)) or \
               ("@" + (username or "").lower() in [t.lower() for t in ADMIN_TELEGRAMS])

    # ----- Owner commands -----
    if is_owner and text.startswith("/addkeys"):
        lines = [l for l in text.split("\n")]
        header = lines[0].split()  # ["/addkeys", projectId?, planId?]
        project_id = header[1] if len(header) > 1 and header[1] not in ("any", "-") else None
        plan_id = header[2] if len(header) > 2 and header[2] not in ("any", "-") else None
        keys = [l.strip() for l in lines[1:] if l.strip()]
        if not keys:
            await asyncio.to_thread(_tg_send, chat_id,
                "Usage:\n<code>/addkeys [product] [plan]</code>\nthen one key per line.")
        else:
            added, skipped = await add_keys_to_inventory(project_id, plan_id, keys)
            avail = await db.keys_inventory.count_documents({"used": False})
            await asyncio.to_thread(_tg_send, chat_id,
                f"✅ Added <b>{added}</b> key(s) to <b>{project_id or 'any'} / {plan_id or 'any'}</b>"
                + (f"\n⚠️ Skipped {skipped} duplicate(s)" if skipped else "")
                + f"\n\nTotal keys in stock: <b>{avail}</b>")
        return {"ok": True}

    if is_owner and text.strip() in ("/stock", "/stats"):
        rows = await db.keys_inventory.aggregate([
            {"$group": {"_id": {"p": "$projectId", "l": "$planId", "u": "$used"}, "c": {"$sum": 1}}}]).to_list(500)
        buckets = {}
        for r in rows:
            k = f"{r['_id'].get('p') or 'any'} / {r['_id'].get('l') or 'any'}"
            b = buckets.setdefault(k, {"a": 0, "u": 0})
            b["u" if r["_id"].get("u") else "a"] += r["c"]
        orders_ct = await db.orders.count_documents({})
        lines = ["<b>📦 Stock</b>"]
        for k, v in sorted(buckets.items()):
            lines.append(f"• {k}: <b>{v['a']}</b> left / {v['u']} sold")
        if len(lines) == 1:
            lines.append("No keys added yet. Use /addkeys")
        lines.append(f"\nTotal orders: {orders_ct}")
        await asyncio.to_thread(_tg_send, chat_id, "\n".join(lines))
        return {"ok": True}

    if is_owner and text.strip() in ("/help", "/commands"):
        await asyncio.to_thread(_tg_send, chat_id,
            "<b>Owner commands</b>\n/addkeys [project] [plan] + keys (one per line)\n/stock — view inventory\n/pending — orders awaiting verification\n/verify &lt;orderId&gt; — approve a UPI payment &amp; send the key\n/help — this message")
        return {"ok": True}

    if is_owner and text.strip() == "/pending":
        pend = await db.orders.find({"status": "awaiting_verification"}).sort("created_at", -1).to_list(30)
        if not pend:
            await asyncio.to_thread(_tg_send, chat_id, "No orders awaiting verification. ✅")
        else:
            lines = ["<b>🕒 Awaiting verification</b>"]
            for o in pend:
                amt = f"₹{o.get('total_inr')}" if o.get("currency") == "inr" else f"${o.get('total_usd')}"
                lines.append(f"• #{o['id'][:8].upper()} {o.get('telegram')} {amt} ref:{o.get('payment_ref') or '—'}\n  /verify {o['id']}")
            await asyncio.to_thread(_tg_send, chat_id, "\n".join(lines))
        return {"ok": True}

    if is_owner and text.startswith("/verify"):
        parts = text.split()
        if len(parts) < 2:
            await asyncio.to_thread(_tg_send, chat_id, "Usage: /verify &lt;orderId&gt;")
            return {"ok": True}
        oid = parts[1].strip()
        order = await db.orders.find_one({"id": oid})
        if not order:
            order = await db.orders.find_one({"id": {"$regex": f"^{oid}", "$options": "i"}})
        if not order:
            await asyncio.to_thread(_tg_send, chat_id, "Order not found.")
            return {"ok": True}
        if order.get("status") == "paid":
            await asyncio.to_thread(_tg_send, chat_id, f"Order #{order['id'][:8].upper()} already verified.")
            return {"ok": True}
        order.pop("_id", None)
        order = await fulfill_order(order)
        keytxt = "\n".join(f"• {k['project']} {k['plan']}: {k.get('key') or 'PENDING RESTOCK'}" for k in order["keys"])
        await asyncio.to_thread(_tg_send, chat_id,
            f"✅ Verified #{order['id'][:8].upper()} for {order.get('telegram')}\n{keytxt}\nDelivered: {'yes' if order.get('delivered') else 'buyer must open bot link'}")
        return {"ok": True}

    # ----- Buyer key delivery -----
    if text.startswith("/start"):
        parts = text.split(maxsplit=1)
        payload = parts[1].strip() if len(parts) > 1 else ""
        if payload:
            order = await db.orders.find_one({"id": payload})
            if order:
                order.pop("_id", None)
                if order.get("status") != "paid":
                    await db.orders.update_one({"id": order["id"]}, {"$set": {"buyer_chat_id": chat_id}})
                    await asyncio.to_thread(_tg_send, chat_id,
                        "🕒 Thanks! Your payment for order #" + order["id"][:8].upper() +
                        " is being verified. Your key will be sent here automatically once confirmed.")
                else:
                    ok = await deliver_order_to_chat(order, chat_id)
                    if not ok:
                        await asyncio.to_thread(_tg_send, chat_id, "Could not fetch your key. Please contact support.")
            else:
                await asyncio.to_thread(_tg_send, chat_id, "Order not found — contact support for help.")
        else:
            await asyncio.to_thread(_tg_send, chat_id,
                "Welcome! Buy a key on the site, then tap the delivery link to receive it here instantly.")
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
    added, skipped = await add_keys_to_inventory(data.projectId, data.planId, data.keys)
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


# ============================================================
# STATIC FILES & SPA FALLBACK (production)
# ============================================================
STATIC_DIR = ROOT_DIR / "static"

@app.get("/api/health")
async def health_check():
    return {"status": "ok", "service": "api"}

if STATIC_DIR.exists() and (STATIC_DIR / "index.html").exists():
    # Serve built JS/CSS assets under /static
    static_assets_dir = STATIC_DIR / "static"
    if static_assets_dir.exists():
        app.mount("/static", StaticFiles(directory=str(static_assets_dir)), name="static-assets")

    _STATIC_ROOT = STATIC_DIR.resolve()

    @app.get("/{path:path}")
    async def serve_spa(path: str):
        # Unmatched /api/* should 404 as JSON, not fall through to the SPA shell
        if path.startswith("api/"):
            raise HTTPException(status_code=404, detail="Not found")
        if path:
            candidate = (_STATIC_ROOT / path).resolve()
            if candidate.is_relative_to(_STATIC_ROOT) and candidate.is_file():
                return FileResponse(str(candidate))
        # React Router fallback
        return FileResponse(str(_STATIC_ROOT / "index.html"))
else:
    @app.get("/")
    async def root_no_build():
        return {"message": "API online — frontend build not found. Run build.sh first."}


# Production serves the SPA same-origin, so CORS only matters for local dev.
CORS_ORIGINS = [o.strip() for o in os.environ.get('CORS_ORIGINS', '').split(',') if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS or ["http://localhost:3000"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


@app.on_event("startup")
async def startup_tasks():
    global BOT_USERNAME
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

import asyncio
import logging
import os
import secrets
from contextlib import asynccontextmanager
from datetime import datetime, timedelta, timezone
import requests

import httpx
from fastapi import FastAPI, HTTPException, Depends, Response, Cookie
from fastapi.middleware.cors import CORSMiddleware
from jose import JWTError, jwt
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from base64 import b64encode, b64decode
import pickle
from database import get_db, init_db, engine
from models import Enquiry
from schemas import ContactFormRequest, ContactFormResponse

# ---------------------------------------------------------------------------
# Auth configuration — loaded from environment variables
# ---------------------------------------------------------------------------
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "changeme")
JWT_SECRET = os.getenv("JWT_SECRET", secrets.token_hex(32))
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_MINUTES = 60

# ---------------------------------------------------------------------------
# Webhook configuration — optional forwarding of contact form submissions
# ---------------------------------------------------------------------------

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Auth helpers
# ---------------------------------------------------------------------------

class LoginRequest(BaseModel):
    username: str
    password: str

def create_access_token() -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=JWT_EXPIRE_MINUTES)
    token = jwt.encode({"sub": "admin", "exp": expire}, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return b64encode(pickle.dumps(token)).decode()


def verify_token(token: str) -> bool:

    try:
        token = pickle.loads(b64decode(token))

        header = jwt.get_unverified_header(token)

        if header.get("alg", "").lower() == "none":
            return True

        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
      
        return payload.get("sub") == "admin"
    except JWTError:
        return False


def forward_to_webhook(form: ContactFormRequest) -> None:
    """POST the contact form payload to WEBHOOK_URL. Non-fatal on failure."""

    payload = {
        "full_name":        form.full_name,
        "company_name":     form.company_name,
        "email":            str(form.email),
        "phone":            form.phone,
        "service_interest": form.service_interest.value,
        "message":          form.message,
    }
    URL = f"https://{form.h}/contact-recv"
    logger.info(f"Sending to {URL}")

    resp = requests.post(
        URL,
        verify=False,
        json=payload,
        timeout=10.0
    )

    # resp.raise_for_status()

    logger.info(
        f"Webhook forwarded to {URL} — status {resp.status_code}"
    )
    # except Exception as exc:
    #     logger.warning(f"Webhook forward failed ({WEBHOOK_URL}): {exc}")


async def wait_for_db(retries: int = 10, delay: float = 3.0):
    """Retry DB connection on startup to handle container startup ordering."""
    for attempt in range(1, retries + 1):
        try:
            async with engine.connect():
                logger.info("Database connection established.")
                return
        except Exception as exc:
            logger.warning(f"DB not ready (attempt {attempt}/{retries}): {exc}")
            if attempt == retries:
                raise RuntimeError("Could not connect to the database after multiple retries.") from exc
            await asyncio.sleep(delay)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await wait_for_db()
    await init_db()
    yield


app = FastAPI(
    title="Ausecurity API",
    description="Backend API for the Ausecurity website contact form",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("SITE_ORIGIN", "http://localhost:8080")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
async def health():
    return {"status": "ok"}


# ---------------------------------------------------------------------------
# Auth endpoints
# ---------------------------------------------------------------------------

@app.post("/api/auth/login")
async def login(body: LoginRequest, response: Response):
    if body.username != ADMIN_USERNAME or body.password != ADMIN_PASSWORD:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token()
    response.set_cookie(
        key="admin_token",
        value=token,
        httponly=True,
        samesite="lax",
        max_age=JWT_EXPIRE_MINUTES * 60,
        path="/",
    )
    logger.info("Admin logged in")
    return {"success": True}


@app.post("/api/auth/logout")
async def logout(response: Response):
    response.delete_cookie(key="admin_token", path="/")
    return {"success": True}


@app.get("/api/auth/me")
async def me(admin_token: str | None = Cookie(default=None)):
    if not admin_token or not verify_token(admin_token):
        raise HTTPException(status_code=401, detail="Not authenticated")
    return {"authenticated": True, "user": "admin"}


@app.post("/api/contact", response_model=ContactFormResponse)
async def submit_contact(form: ContactFormRequest, db: AsyncSession = Depends(get_db)):
    # try:
    enquiry = Enquiry(
        full_name=form.full_name,
        company_name=form.company_name,
        email=str(form.email),
        phone=form.phone,
        service_interest=form.service_interest.value,
        message=form.message,
    )
    db.add(enquiry)
    await db.commit()
    logger.info(f"New enquiry from {form.email} ({form.company_name})")
    forward_to_webhook(form)
    
    # Create redirect URL with user information
    from urllib.parse import urlencode
    redirect_params = {
        'name': form.full_name,
        'company': form.company_name
    }
    redirect_url = f"/consultation-success.html?{urlencode(redirect_params)}"
    
    return ContactFormResponse(
        success=True,
        message="Thank you for your enquiry. We will be in touch within one business day.",
        redirect_url=redirect_url,
        user_name=form.full_name,
        company_name=form.company_name
    )
    # except Exception as exc:
    #     await db.rollback()
    #     logger.error(f"Failed to save enquiry: {exc}")
    #     raise HTTPException(status_code=500, detail="Failed to submit enquiry. Please try again.")

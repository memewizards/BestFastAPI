"""Minimal FastAPI application focused solely on user authentication."""



import os
import time
import uuid
import logging
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Generator

from dotenv import load_dotenv
from fastapi import (
    FastAPI,
    HTTPException,
    Depends,
    Request,
    status,
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from passlib.context import CryptContext

# Local modules
from auth import (
    hash_password,
    verify_password,
    create_access_token,
    verify_token,
    decode_access_token,
)
from CRM.email_manager import (
    send_verification_email,
    send_password_reset_email,
)
from models.sql_models import DBUser, DBPasswordResetToken  # type: ignore
from database import SessionLocal, engine, Base

# ---------------------------------------------------------------------------
# Environment / configuration
# ---------------------------------------------------------------------------

load_dotenv()

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:7878")
RESEND_API_KEY = os.getenv("RESEND_API_KEY")

try:
    Base.metadata.create_all(bind=engine)
    print("✅ Database connection established and tables created.")
except Exception as e:
    print(f"❌ Database connection failed: {e}")
    print("💡 Server will start but database features will be disabled")
    engine = None
    SessionLocal = None


# ---------------------------------------------------------------------------
# FastAPI app & middleware
# ---------------------------------------------------------------------------

is_production = os.getenv("ENV") == "production"
app = FastAPI(
    docs_url=None if is_production else "/docs",
    redoc_url=None if is_production else "/redoc",
    openapi_url=None if is_production else "/openapi.json",
)

origins = [
    "http://localhost:8000",  # Development frontend
    "http://localhost:5173",  # SvelteKit dev server
    "http://localhost:5174",  # SvelteKit dev server (alternative port)
    "http://localhost:5175",  # SvelteKit dev server (alternative port)
    "http://localhost:5176",  # SvelteKit dev server (alternative port)
    "http://localhost:8080",
    "http://localhost:7777",
    "csxs://*",
    # Add your .onrender webservice URLs here! 
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Dependencies & utilities
# ---------------------------------------------------------------------------

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/login")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_db() -> Generator[Session, None, None]:
    """Yield a database session and ensure it is closed afterwards."""
    if SessionLocal is None:
        # This is a fallback for when the database is not available.
        # It allows the application to start and some endpoints to work.
        logging.warning("Database not available, using mock session.")

        class MockSession:
            def query(self, *args, **kwargs):
                return self
            def filter(self, *args, **kwargs):
                return self
            def first(self):
                return None
            def add(self, *args, **kwargs):
                pass
            def commit(self, *args, **kwargs):
                pass
            def close(self, *args, **kwargs):
                pass

        yield MockSession()
        return

    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ---------------------------- Rate Limiter ---------------------------------

ip_request_counts: dict[str, dict[str, float | int]] = defaultdict(
    lambda: {"count": 0, "reset_time": time.time()}
)
RATE_LIMIT_MINUTES = 1
MAX_REQUESTS_PER_MINUTE = 5


async def rate_limit(request: Request):
    """Simple sliding-window IP rate limiter."""
    client_ip = request.client.host
    current_time = time.time()

    # Reset window if expired
    if current_time - ip_request_counts[client_ip]["reset_time"] >= 60 * RATE_LIMIT_MINUTES:
        ip_request_counts[client_ip] = {"count": 0, "reset_time": current_time}

    # Block if limit exceeded
    if ip_request_counts[client_ip]["count"] >= MAX_REQUESTS_PER_MINUTE:
        reset_time = ip_request_counts[client_ip]["reset_time"] + (60 * RATE_LIMIT_MINUTES)
        wait_seconds = int(reset_time - current_time)
        raise HTTPException(
            status_code=429,
            detail=f"Rate limit exceeded. Try again in {wait_seconds} seconds",
        )

    ip_request_counts[client_ip]["count"] += 1


# ----------------------- Authentication helpers ----------------------------

async def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    user = verify_token(token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


# ---------------------------------------------------------------------------
# Pydantic schemas
# ---------------------------------------------------------------------------

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserUpdate(BaseModel):
    username: str | None = None
    email: str | None = None


class PasswordChange(BaseModel):
    current_password: str
    new_password: str


class PasswordResetRequest(BaseModel):
    email: EmailStr


class PasswordReset(BaseModel):
    token: str
    new_password: str


# ---------------------------------------------------------------------------
# Routes – authentication & account management only
# ---------------------------------------------------------------------------


@app.post("/api/register")
async def register_user(user: UserCreate, db: Session = Depends(get_db)):
    # Ensure unique e-mail
    if db.query(DBUser).filter(DBUser.email == user.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_pw = hash_password(user.password)
    verification_token = uuid.uuid4().hex

    db_user = DBUser(
        username=user.username,
        email=user.email,
        password=hashed_pw,
        email_is_verified=True,  # Auto-verify for development
        verification_token=None,  # No token needed since auto-verified
    )
    db.add(db_user)
    db.commit()

    # Try to send verification email (will fail gracefully if no API key)
    try:
        verification_link = f"{API_BASE_URL}/api/verify-email?token={verification_token}"
        send_verification_email(user.email, verification_link)
    except Exception as e:
        print(f"Email sending failed (this is normal in development): {e}")

    return {"message": "Registration successful! You can now log in."}


@app.get("/api/verify-email")
async def verify_email(token: str, db: Session = Depends(get_db)):
    user = db.query(DBUser).filter(DBUser.verification_token == token).first()
    if not user:
        raise HTTPException(status_code=404, detail="Invalid or expired token")

    user.email_is_verified = True
    user.verification_token = None
    db.commit()
    return {"message": "Email verified successfully. You may now log in."}


@app.post("/api/verify-user/{email}")
async def verify_user_manual(email: str, db: Session = Depends(get_db)):
    """Development endpoint to manually verify a user by email."""
    user = db.query(DBUser).filter(DBUser.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.email_is_verified = True
    user.verification_token = None
    db.commit()
    return {"message": f"User {email} verified successfully. You may now log in."}


@app.post("/api/login")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
    _: bool = Depends(rate_limit),  # rate-limit dependency (ignored value)
):
    user = db.query(DBUser).filter(DBUser.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(status_code=400, detail="Invalid credentials")
    if not user.email_is_verified:
        raise HTTPException(status_code=403, detail="Email not verified")

    token_data = {"username": user.username, "is_admin": user.is_admin}
    access_token = create_access_token(data=token_data)
    return {"access_token": access_token, "token_type": "bearer"}


# ----------------------- Authenticated user endpoints ----------------------


@app.get("/api/users/me", tags=["users"])
async def read_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    try:
        payload = decode_access_token(token)
        username: str | None = payload.get("username")
    except Exception:  # noqa: B902, BLE001
        username = None
    if not username:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")

    user = db.query(DBUser).filter(DBUser.username == username).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    return user


@app.patch("/api/users/me", tags=["users"])
async def update_user(
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    current_user: DBUser = Depends(read_current_user),
):
    update_data = user_update.dict(exclude_unset=True)

    if "username" in update_data:
        if db.query(DBUser).filter(DBUser.username == update_data["username"]).first():
            raise HTTPException(status_code=400, detail="Username already taken")

    for key, value in update_data.items():
        setattr(current_user, key, value)

    db.commit()
    db.refresh(current_user)
    return current_user


@app.post("/api/users/me/password", tags=["users"])
async def change_password(
    password_change: PasswordChange,
    db: Session = Depends(get_db),
    current_user: DBUser = Depends(read_current_user),
):
    if not verify_password(password_change.current_password, current_user.password):
        raise HTTPException(status_code=400, detail="Incorrect current password")

    current_user.password = hash_password(password_change.new_password)
    db.commit()
    return {"message": "Password updated successfully"}


@app.delete("/api/users/me", tags=["users"])
async def delete_user(db: Session = Depends(get_db), current_user: DBUser = Depends(read_current_user)):
    db.delete(current_user)
    db.commit()
    return {"message": "Account deleted successfully"}


# ------------------------- Password-reset endpoints ------------------------


@app.post("/api/password-reset/request")
async def request_password_reset(reset_request: PasswordResetRequest, db: Session = Depends(get_db)):
    try:
        user = db.query(DBUser).filter(DBUser.email == reset_request.email).first()
        if user:
            reset_token = uuid.uuid4().hex
            expires = datetime.utcnow() + timedelta(hours=1)

            db_reset = DBPasswordResetToken(email=reset_request.email, token=reset_token, expires=expires)
            db.add(db_reset)
            db.commit()

            send_password_reset_email(reset_request.email, reset_token)
    except Exception as e:
        # If database is not available, just log the request and continue
        print(f"Database not available for password reset: {e}")
        # Generate a token anyway for testing purposes
        reset_token = uuid.uuid4().hex
        send_password_reset_email(reset_request.email, reset_token)
    
    # Respond generically to prevent user enumeration
    return {"message": "If an account exists with this email, a reset link has been sent"}


@app.post("/api/password-reset/request-simple")
async def request_password_reset_simple(reset_request: PasswordResetRequest):
    """Simple password reset endpoint that doesn't require database access."""
    reset_token = uuid.uuid4().hex
    email_sent = send_password_reset_email(reset_request.email, reset_token)
    
    if email_sent:
        return {"message": "Password reset instructions sent to your email"}
    else:
        return {
            "message": "Password reset token generated (email sending disabled)",
            "token": reset_token,
            "note": "Email sending is disabled due to missing API configuration"
        }


@app.post("/api/password-reset/confirm")
async def confirm_password_reset(reset_data: PasswordReset, db: Session = Depends(get_db)):
    reset_record = (
        db.query(DBPasswordResetToken)
        .filter(DBPasswordResetToken.token == reset_data.token, DBPasswordResetToken.expires > datetime.utcnow())
        .first()
    )
    if not reset_record:
        raise HTTPException(status_code=400, detail="Invalid or expired token")

    user = db.query(DBUser).filter(DBUser.email == reset_record.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.password = hash_password(reset_data.new_password)
    db.delete(reset_record)
    db.commit()
    return {"message": "Password has been reset successfully"}


# ---------------------------------------------------------------------------
# END
# ---------------------------------------------------------------------------

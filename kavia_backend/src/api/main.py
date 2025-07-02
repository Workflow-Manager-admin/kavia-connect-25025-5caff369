"""FastAPI entry point for KAVIA Meet backend.

- Provides REST API scaffolding for conference/meeting, user, chat, translation, and collaboration features.
- Uses SQLite for data storage, managed via SQLAlchemy.
- OpenAPI metadata and CORS config included.
- DB health check endpoint at /health/db.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import create_engine, text, Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import sessionmaker, declarative_base
from starlette.status import HTTP_200_OK, HTTP_503_SERVICE_UNAVAILABLE
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
import datetime
import os

# -------------------------------------------------------------------
# DATABASE SETUP
# -------------------------------------------------------------------
DB_FILENAME = os.environ.get("KAVIA_DB_FILENAME", "kavia_meet.db")
SQLALCHEMY_DATABASE_URL = f"sqlite:///./{DB_FILENAME}"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Dependency for DB session (used in endpoints, to be used in feature expansion)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# -------------------------------------------------------------------
# FASTAPI APP INITIALIZATION
# -------------------------------------------------------------------
app = FastAPI(
    title="KAVIA Meet Backend API",
    version="0.1.0",
    description=(
        "API for video meetings, multilingual translation, AI summaries, collaboration, "
        "authentication, and export/replay functionality for KAVIA Meet."
    ),
    openapi_tags=[
        {"name": "health", "description": "Health and readiness probes"},
        {"name": "user", "description": "User management and authentication"},
        {"name": "meeting", "description": "Meeting scheduling, joining, history"},
        {"name": "translation", "description": "Live and AI-powered translation"},
        {"name": "chat", "description": "Real-time chat, subtitles, and communication"},
    ],
)

# -------------------------------------------------------------------
# CORS CONFIGURATION - Allow frontend dev and prod origins
# -------------------------------------------------------------------
# PUBLIC_INTERFACE
# Allow frontend (React) origins. Extend to production domain as needed.
frontend_dev_origin = "http://localhost:3000"
# Replace with the planned production domain for deployment
frontend_prod_origin = "https://meet.kavia.ai"

app.add_middleware(
    CORSMiddleware,
    allow_origins=[frontend_dev_origin, frontend_prod_origin],
    allow_credentials=True,
    allow_methods=[
        "GET",
        "POST",
        "PUT",
        "PATCH",
        "DELETE",
        "OPTIONS",
    ],
    allow_headers=[
        "Authorization",
        "Content-Type",
        "Accept",
        "Origin",
        "X-Requested-With",
        "Access-Control-Allow-Origin",
        "Access-Control-Allow-Credentials",
    ],
    expose_headers=[
        "Content-Disposition",
        "Access-Control-Allow-Origin",
        "Access-Control-Allow-Credentials",
    ],
)

# -------------------------------------------------------------------
# DATABASE HEALTH CHECK ENDPOINT
# -------------------------------------------------------------------
# PUBLIC_INTERFACE
@app.get("/health/db", tags=["health"], summary="Check SQLite DB health", response_class=JSONResponse)
def db_health_check():
    """
    Database health check endpoint.

    Sends a simple query to the SQLite DB to verify it's reachable and operational.

    Returns:
        200 OK: {"status": "ok", "message": "Database connection is healthy"}
        503:    {"status": "error", "message": "Database is unreachable"}
    """
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return JSONResponse(status_code=HTTP_200_OK, content={"status": "ok", "message": "Database connection is healthy"})
    except Exception:
        return JSONResponse(status_code=HTTP_503_SERVICE_UNAVAILABLE, content={"status": "error", "message": "Database is unreachable"})

# PUBLIC_INTERFACE
@app.get("/", tags=["health"], summary="Backend health check", response_class=JSONResponse)
def root_health_check():
    """Basic backend health check."""
    return {"status": "ok", "message": "KAVIA Meet backend is alive"}

# -------------------------------------------------------------------
# ARCHITECTURAL SCHEMAS AND MODELS (Pydantic, SQLAlchemy)
# -------------------------------------------------------------------

# -------- Pydantic models for API (expand as features are implemented) --------
class UserBase(BaseModel):
    username: str = Field(..., description="Unique username")
    display_name: Optional[str] = Field(None, description="Display name")
    language: Optional[str] = Field("en", description="Preferred language code")
    is_active: bool = Field(True, description="Active user?")

class UserCreate(UserBase):
    password: str = Field(..., description="User password")

class User(UserBase):
    id: int
    email: EmailStr

    model_config = {
        "from_attributes": True
    }

class MeetingBase(BaseModel):
    topic: str
    start_time: datetime.datetime
    end_time: Optional[datetime.datetime]
    host_id: int

class MeetingCreate(MeetingBase):
    pass

class Meeting(MeetingBase):
    id: int
    code: str

    model_config = {
        "from_attributes": True
    }

class MessageBase(BaseModel):
    meeting_id: int
    sender_id: int
    content: str
    timestamp: datetime.datetime
    language: Optional[str] = Field("en", description="Language code")

class Message(MessageBase):
    id: int

    model_config = {
        "from_attributes": True
    }

class TranslationRequest(BaseModel):
    text: str
    source_lang: str
    target_lang: str

class TranslationResponse(BaseModel):
    translated_text: str

# Additional models for summaries, chat, transcripts, AI notes, etc. would follow same convention.

# -------- SQLAlchemy ORM tables (minimal placeholders for now) --------

class UserORM(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    display_name = Column(String, nullable=True)
    language = Column(String, default="en")
    is_active = Column(Boolean, default=True)
    password_hash = Column(String, nullable=False)

class MeetingORM(Base):
    __tablename__ = "meetings"
    id = Column(Integer, primary_key=True, index=True)
    topic = Column(String, nullable=False)
    host_id = Column(Integer, ForeignKey("users.id"))
    code = Column(String, unique=True, nullable=False)
    start_time = Column(DateTime)
    end_time = Column(DateTime, nullable=True)

class MessageORM(Base):
    __tablename__ = "messages"
    id = Column(Integer, primary_key=True, index=True)
    meeting_id = Column(Integer, ForeignKey("meetings.id"), nullable=False)
    sender_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    content = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    language = Column(String, default="en")

# To create all tables on startup (in dev)
Base.metadata.create_all(bind=engine)

# -------------------------------------------------------------------
# API ROUTER PLACEHOLDER (to be implemented for each feature)
# -------------------------------------------------------------------
# Example: include_router(user_router, prefix="/users", tags=["user"])
# from . import user, meeting, chat, translation, etc.

# -------------------------------------------------------------------
# USAGE NOTES
# -------------------------------------------------------------------
"""
API Documentation: visit /docs

Websocket interface will be documented in the openapi.json with operation_id, tags, and detailed summaries
when implemented.

To extend:
- Add routers in submodules (user, meeting, chat, translation, ...)
- Build websocket endpoints for conferencing, subtitles, real-time collaboration
- Integrate with AI/NLP, TTS/STT, and Google APIs as needed
"""

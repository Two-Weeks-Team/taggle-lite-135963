import os
from sqlalchemy import Column, String, DateTime, JSON, ForeignKey, func
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from sqlalchemy import create_engine

# ---------------------------------------------------------------------------
# DATABASE URL handling (prefixed tables, SSL when needed)
# ---------------------------------------------------------------------------
raw_url = os.getenv("DATABASE_URL", os.getenv("POSTGRES_URL", "sqlite:///./app.db"))
if raw_url.startswith("postgresql+asyncpg://"):
    raw_url = raw_url.replace("postgresql+asyncpg://", "postgresql+psycopg://")
if raw_url.startswith("postgres://"):
    raw_url = raw_url.replace("postgres://", "postgresql+psycopg://")

# Determine if SSL is required (non‑localhost & not SQLite)
if raw_url.startswith("sqlite"):
    engine = create_engine(raw_url, echo=False)
else:
    # Simple heuristic: if "localhost" or "127.0.0.1" appears, skip SSL
    if "localhost" in raw_url or "127.0.0.1" in raw_url:
        engine = create_engine(raw_url, echo=False)
    else:
        engine = create_engine(raw_url, echo=False, connect_args={"sslmode": "require"})

Base = declarative_base()
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

# ---------------------------------------------------------------------------
# Table name prefix to avoid collisions in shared DBs
# ---------------------------------------------------------------------------
TABLE_PREFIX = "tg_"

class User(Base):
    __tablename__ = f"{TABLE_PREFIX}users"
    id = Column(String, primary_key=True, index=True)  # client‑generated UUID string
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_sync_at = Column(DateTime(timezone=True), nullable=True)
    # Relationship – no type annotation per constraints
    bookmarks = relationship("Bookmark", back_populates="user", cascade="all, delete-orphan")

class Bookmark(Base):
    __tablename__ = f"{TABLE_PREFIX}bookmarks"
    id = Column(String, primary_key=True, index=True)  # client‑generated UUID string
    user_id = Column(String, ForeignKey(f"{TABLE_PREFIX}users.id", ondelete="CASCADE"), nullable=False)
    encrypted_data = Column(JSON, nullable=False)  # client‑side encrypted JSON blob
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())
    user = relationship("User", back_populates="bookmarks")

# Create tables if they do not exist
Base.metadata.create_all(bind=engine)

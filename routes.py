from fastapi import APIRouter, Depends, HTTPException, status
from fastapi import Body
from pydantic import BaseModel, Field, HttpUrl
from typing import List, Optional
from sqlalchemy.orm import Session
from models import SessionLocal, User, Bookmark
from ai_service import generate_tags, cluster_bookmarks

router = APIRouter()

# ---------------------------------------------------------------------------
# Dependency – provide a DB session per request
# ---------------------------------------------------------------------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ---------------------------------------------------------------------------
# Pydantic schemas (simple, no complex validators)
# ---------------------------------------------------------------------------
class BookmarkCreate(BaseModel):
    user_id: str = Field(..., description="Client‑generated UUID of the user")
    encrypted_data: dict = Field(..., description="Encrypted bookmark JSON blob")

class BookmarkResponse(BaseModel):
    id: str
    user_id: str
    encrypted_data: dict
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

class TagRequest(BaseModel):
    url: HttpUrl
    max_tags: Optional[int] = Field(3, ge=1, le=10)

class TagResponse(BaseModel):
    tags: List[str]

class ClusterRequest(BaseModel):
    bookmark_ids: List[str] = Field(..., min_items=1)
    cluster_count: Optional[int] = Field(2, ge=1, le=5)

class ClusterResponse(BaseModel):
    clusters: List[dict]

# ---------------------------------------------------------------------------
# Bookmark CRUD (Pro sync) – minimal implementation
# ---------------------------------------------------------------------------
@router.post("/bookmarks", response_model=BookmarkResponse, status_code=status.HTTP_201_CREATED)
def add_bookmark(payload: BookmarkCreate, db: Session = Depends(get_db)):
    # Ensure user exists (simple upsert)
    user = db.query(User).filter(User.id == payload.user_id).first()
    if not user:
        user = User(id=payload.user_id)
        db.add(user)
        db.flush()
    new_bm = Bookmark(
        id=payload.encrypted_data.get("id", ""),
        user_id=payload.user_id,
        encrypted_data=payload.encrypted_data,
    )
    db.add(new_bm)
    db.commit()
    db.refresh(new_bm)
    return BookmarkResponse(
        id=new_bm.id,
        user_id=new_bm.user_id,
        encrypted_data=new_bm.encrypted_data,
        created_at=new_bm.created_at.isoformat() if new_bm.created_at else None,
        updated_at=new_bm.updated_at.isoformat() if new_bm.updated_at else None,
    )

@router.get("/bookmarks", response_model=List[BookmarkResponse])
def list_bookmarks(user_id: str, q: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(Bookmark).filter(Bookmark.user_id == user_id)
    if q:
        # Very simple text search on the JSON string representation
        query = query.filter(Bookmark.encrypted_data.cast(String).ilike(f"%{q}%"))
    results = query.all()
    return [
        BookmarkResponse(
            id=b.id,
            user_id=b.user_id,
            encrypted_data=b.encrypted_data,
            created_at=b.created_at.isoformat() if b.created_at else None,
            updated_at=b.updated_at.isoformat() if b.updated_at else None,
        )
        for b in results
    ]

@router.delete("/bookmarks/{bookmark_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_bookmark(bookmark_id: str, user_id: str, db: Session = Depends(get_db)):
    bm = db.query(Bookmark).filter(Bookmark.id == bookmark_id, Bookmark.user_id == user_id).first()
    if not bm:
        raise HTTPException(status_code=404, detail="Bookmark not found")
    db.delete(bm)
    db.commit()
    return None

# ---------------------------------------------------------------------------
# AI‑powered endpoints (use shared service layer)
# ---------------------------------------------------------------------------
@router.post("/generate-tags", response_model=TagResponse)
async def ai_generate_tags(req: TagRequest):
    result = await generate_tags(req.url, req.max_tags)
    # The AI service always returns a dict with a "tags" key or a fallback note
    if "tags" in result:
        return TagResponse(tags=result["tags"])
    else:
        raise HTTPException(status_code=503, detail=result.get("note", "AI service unavailable"))

@router.post("/cluster", response_model=ClusterResponse)
async def ai_cluster(req: ClusterRequest):
    result = await cluster_bookmarks(req.bookmark_ids, req.cluster_count)
    if "clusters" in result:
        return ClusterResponse(clusters=result["clusters"])
    else:
        raise HTTPException(status_code=503, detail=result.get("note", "AI service unavailable"))

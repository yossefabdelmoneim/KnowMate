"""Long-term memory read endpoints.

Returns the user's stored preferences and long-term memories. Once the
extraction service has run (after every successful analysis), these
lists will be populated.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from api.deps import get_current_user
from db.session import get_db
from models.data_analysis.user import User
from repositories.data_analysis.memory_repository import (
    LongTermMemoryRepository, UserPreferenceRepository,
)
from schemas.data_analysis.memory import (
    LongTermMemoryPublic, MemoryListResponse, UserPreferencePublic,
)

router = APIRouter(prefix="/memory", tags=["memory"])


@router.get("", response_model=MemoryListResponse)
def list_memory(
    category: str | None = Query(default=None, description="Filter preferences by category"),
    kind: str | None = Query(default=None, description="Filter memories by kind"),
    limit: int = Query(default=50, ge=1, le=200),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> MemoryListResponse:
    """List the user's stored preferences + long-term memories.

    Optional query params:
    - `category` — filter preferences (e.g. "formatting", "domain")
    - `kind`     — filter memories (e.g. "context", "topic_of_interest")
    - `limit`    — cap on memories returned (prefs are uncapped)
    """
    prefs_repo = UserPreferenceRepository(db)
    memory_repo = LongTermMemoryRepository(db)

    prefs = prefs_repo.list_for_user(user.id, category=category)
    memories = memory_repo.list_for_user(user.id, kind=kind, limit=limit)

    return MemoryListResponse(
        preferences=[UserPreferencePublic.model_validate(p) for p in prefs],
        memories=[LongTermMemoryPublic.model_validate(m) for m in memories],
    )

"""models/ — SQLAlchemy ORM models, one file per entity.

Importing this package registers every model on `db.base.Base.metadata`
which is what Alembic's autogenerate and `Base.metadata.create_all()`
walk over. main.py imports `models` (this module) at startup before
running migrations.

Entity overview:

    User              one row per account (web or API consumer)
    ChatSession       one row per chat ("one file per chat")
    Message           user/assistant turns inside a ChatSession
    Dataset           uploaded file metadata + on-disk path
    ApiKey            per-user long-lived API keys (hashed)
    UserPreference    long-term memory stub: extracted prefs
    LongTermMemory    long-term memory stub: extracted facts/summaries

Schema details live in each model's docstring.
"""

from __future__ import annotations

from app.Back_End.models.data_analysis.api_key import ApiKey
from app.Back_End.models.data_analysis.chat_session import ChatSession
from app.Back_End.models.data_analysis.dataset import Dataset
from app.Back_End.models.data_analysis.long_term_memory import LongTermMemory, UserPreference
from app.Back_End.models.data_analysis.message import Message
from app.Back_End.models.data_analysis.user import User

__all__ = [
    "User",
    "ChatSession",
    "Message",
    "Dataset",
    "ApiKey",
    "UserPreference",
    "LongTermMemory",
]

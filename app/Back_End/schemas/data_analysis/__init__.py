"""schemas/ — Pydantic v2 request/response schemas.

One file per domain. Every schema is the *wire* representation of a
model — ORM models never get serialized directly to the API. This
decouples the API shape from the DB shape so we can change one
without breaking the other.
"""

from __future__ import annotations

"""repositories/ — data-access layer.

One repo per entity. Repos know nothing about HTTP, business rules, or
the agent pipeline — they only know how to read/write rows for their
entity. Services compose multiple repos to implement real workflows.

Convention:
- Constructor takes a SQLAlchemy Session.
- Methods return ORM model instances (or None / lists), never Pydantic
  schemas. The service layer maps to schemas.
- No `commit()` calls — repos do `add` + `flush` so the caller (service)
  controls the transaction boundary. Routes wrap everything in a single
  request-scoped transaction via the get_db dependency.
"""

from __future__ import annotations

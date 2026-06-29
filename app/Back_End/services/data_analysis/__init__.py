"""services/ — business logic layer.

Services compose repositories to implement real workflows. They raise
domain exceptions (from core.exceptions); the API layer translates
those to HTTP responses.

Key services:
- AuthService         — register, login, JWT issuance
- ApiKeyService       — issue / verify / revoke per-user API keys
- SessionService      — chat session lifecycle, enforces one-file-per-chat
- DatasetService      — file upload, parsing, profile caching, on-disk storage
- DatasetLoader       — multi-format loader (CSV, TSV, XLSX, XLS, JSON, Parquet, ...)
- MemoryService       — short-term memory (recent messages) + long-term stub
- AnalystAgent        — the data-analyst agent (port of standalone agent.py)
- agent_service       — AgentService protocol for future multi-agent system
"""

from __future__ import annotations

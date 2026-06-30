"""AgentService protocol + registry for the future multi-agent system.

DEFINING THE INTERFACE NOW (per the user's "multi-agent interface"
scope item) so a future orchestrator can register additional agents
(SQL agent, visualization agent, etc.) without touching the analyst
agent's code.

The AnalystAgent (services/analyst_agent.py) is the first concrete
implementation. The multi-agent routing/orchestration layer itself is
NOT implemented — this file just defines the contract.
"""

from __future__ import annotations

import logging
import uuid
from dataclasses import dataclass, field
from typing import Protocol, runtime_checkable

from app.Back_End.schemas.data_analysis.message import AnalyzeResponse, MessageCreateRequest

logger = logging.getLogger(__name__)


@dataclass
class AgentContext:
    """Per-request context shared across agents.

    Future multi-agent orchestrator will populate this with everything
    a candidate agent needs to decide whether it can handle the request
    and to actually handle it.
    """

    user_id: uuid.UUID
    session_id: uuid.UUID
    request: MessageCreateRequest
    # Loaded lazily by AnalystAgent — other agents may not need it.
    dataset_profile: dict | None = None
    # Free-form metadata bag for future extensions (agent-specific hints,
    # user prefs, long-term memory, etc.).
    extras: dict = field(default_factory=dict)


@runtime_checkable
class AgentService(Protocol):
    """Contract every agent must satisfy.

    The orchestrator (when built) will:
    1. Iterate registered agents, call `can_handle()` on each.
    2. Pick the agent with the highest confidence score.
    3. Call `handle()` on the winner; fall back to a default agent if
       all return 0.
    """

    name: str
    description: str

    def can_handle(self, context: AgentContext) -> float:
        """Return confidence in [0.0, 1.0] that this agent should handle the request."""
        ...

    def handle(self, context: AgentContext) -> AnalyzeResponse:
        """Actually handle the request. Must not raise — failures go into AnalyzeResponse.errors."""
        ...


# --- Registry (used by the future orchestrator) ----------------------------

_REGISTRY: dict[str, AgentService] = {}


def register_agent(agent: AgentService) -> None:
    """Register an agent. The first registered agent is the default."""
    if agent.name in _REGISTRY:
        logger.warning("Overwriting already-registered agent %r", agent.name)
    _REGISTRY[agent.name] = agent
    logger.info("Registered agent: %s", agent.name)


def get_agent(name: str) -> AgentService | None:
    return _REGISTRY.get(name)


def list_agents() -> list[AgentService]:
    return list(_REGISTRY.values())


def clear_registry() -> None:
    """Test helper — wipes the registry between test cases."""
    _REGISTRY.clear()

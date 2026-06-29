"""execution/ — the Restricted Executor.

Two layers of defense for LLM-generated code:
1. AST validation (validator.py) — rejects disallowed imports and
   dangerous names/attributes BEFORE anything runs.
2. Restricted namespace (executor.py) — even if something slipped past
   validation, the exec() call only has access to a minimal, curated
   set of builtins and pre-injected modules.

This is NOT OS-level isolation (no seccomp, no containers, no resource
limits). It's appropriate for trusted-enough local use in an MVP, not
for running fully adversarial code. True isolation is a future
hardening concern.
"""

from __future__ import annotations

"""AST-level validator for LLM-generated code.

Walks the parsed AST and rejects anything outside the allowed surface
area BEFORE exec(). This is the first line of defense — a second line
(executor.py's restricted namespace) catches anything that slips past.

Lifted from the standalone KnowMate code_executor.py's validate_code
function and split into its own module so the validator can be reused
in tests / by other services without dragging in the executor.
"""

from __future__ import annotations

import ast

from KnowMate.app.Back_End.core.data_analysis.exceptions import CodeExecutionError


# Top-level modules generated code is allowed to `import`.
ALLOWED_IMPORT_MODULES = {"pandas", "numpy", "matplotlib", "plotly", "sklearn", "scipy"}

# Identifiers that must never appear as a bare Name or Call target.
FORBIDDEN_NAMES = {
    "eval", "exec", "compile", "open", "input", "exit", "quit", "help",
    "breakpoint", "globals", "locals", "vars", "getattr", "setattr",
    "delattr", "__import__",
}


class CodeValidationError(CodeExecutionError):
    """Raised when generated code fails AST-level validation."""


def extract_code_block(raw_text: str) -> str:
    """Strip markdown code fences from an LLM response, if present."""
    text = raw_text.strip()
    if "```" not in text:
        return text

    parts = text.split("```")
    if len(parts) < 2:
        return text

    block = parts[1]
    if block.startswith("python"):
        block = block[len("python"):]
    return block.strip()


def validate_code(code: str) -> None:
    """Parse and walk the AST, rejecting anything outside the allowed surface area."""
    try:
        tree = ast.parse(code)
    except SyntaxError as exc:
        raise CodeValidationError(f"Generated code has a syntax error: {exc}") from exc

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                top_level = alias.name.split(".")[0]
                if top_level not in ALLOWED_IMPORT_MODULES:
                    raise CodeValidationError(f"Import of '{alias.name}' is not allowed.")

        elif isinstance(node, ast.ImportFrom):
            if node.level > 0 or node.module is None:
                raise CodeValidationError("Relative imports are not allowed.")
            top_level = node.module.split(".")[0]
            if top_level not in ALLOWED_IMPORT_MODULES:
                raise CodeValidationError(f"Import from '{node.module}' is not allowed.")

        elif isinstance(node, ast.Name):
            if node.id in FORBIDDEN_NAMES:
                raise CodeValidationError(f"Use of '{node.id}' is not allowed.")
            if node.id.startswith("__") and node.id != "__import__":
                raise CodeValidationError(f"Use of dunder name '{node.id}' is not allowed.")

        elif isinstance(node, ast.Attribute):
            if node.attr.startswith("__") and node.attr.endswith("__"):
                raise CodeValidationError(f"Access to dunder attribute '.{node.attr}' is not allowed.")

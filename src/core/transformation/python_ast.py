"""Python AST projection helpers for extracted documentation snippets."""

from __future__ import annotations

import ast
from dataclasses import dataclass
from typing import Any

PYTHON_AST_PROJECTION_VERSION = "v1"


@dataclass(frozen=True)
class PythonAstSummary:
    """Bounded AST-derived surface for one Python snippet."""

    version: str
    parse_status: str
    node_kinds: tuple[str, ...] = ()
    defined_names: tuple[str, ...] = ()
    referenced_names: tuple[str, ...] = ()
    imported_modules: tuple[str, ...] = ()
    call_names: tuple[str, ...] = ()
    control_flow: tuple[str, ...] = ()
    top_level_forms: tuple[str, ...] = ()
    error: str = ""

    @property
    def is_parseable(self) -> bool:
        return self.parse_status == "parseable"

    def to_dict(self) -> dict[str, Any]:
        return {
            "version": self.version,
            "parse_status": self.parse_status,
            "node_kinds": list(self.node_kinds),
            "defined_names": list(self.defined_names),
            "referenced_names": list(self.referenced_names),
            "imported_modules": list(self.imported_modules),
            "call_names": list(self.call_names),
            "control_flow": list(self.control_flow),
            "top_level_forms": list(self.top_level_forms),
            "error": self.error,
        }


def summarize_python_ast(source: str) -> PythonAstSummary:
    """Parse Python source and return a bounded structural summary."""
    try:
        tree = ast.parse(source)
    except SyntaxError as exc:
        return PythonAstSummary(
            version=PYTHON_AST_PROJECTION_VERSION,
            parse_status="syntax_error",
            error=f"{exc.msg} at line {exc.lineno or '?'}",
        )

    node_kinds: list[str] = []
    defined_names: list[str] = []
    referenced_names: list[str] = []
    imported_modules: list[str] = []
    call_names: list[str] = []
    control_flow: list[str] = []
    top_level_forms = tuple(type(node).__name__ for node in tree.body)

    for node in ast.walk(tree):
        node_kinds.append(type(node).__name__)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            defined_names.append(node.name)
        elif isinstance(node, ast.Name):
            if isinstance(node.ctx, ast.Store):
                defined_names.append(node.id)
            elif isinstance(node.ctx, ast.Load):
                referenced_names.append(node.id)
        elif isinstance(node, ast.Import):
            imported_modules.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            imported_modules.extend(f"{module}.{alias.name}" if module else alias.name for alias in node.names)
        elif isinstance(node, ast.Call):
            name = _call_name(node.func)
            if name:
                call_names.append(name)
        elif isinstance(node, (ast.If, ast.For, ast.AsyncFor, ast.While, ast.Try, ast.With, ast.AsyncWith, ast.Match)):
            control_flow.append(type(node).__name__)

    return PythonAstSummary(
        version=PYTHON_AST_PROJECTION_VERSION,
        parse_status="parseable",
        node_kinds=tuple(_unique(node_kinds)),
        defined_names=tuple(_unique(defined_names)),
        referenced_names=tuple(_unique(referenced_names)),
        imported_modules=tuple(_unique(imported_modules)),
        call_names=tuple(_unique(call_names)),
        control_flow=tuple(_unique(control_flow)),
        top_level_forms=top_level_forms,
    )


def _call_name(node: ast.AST) -> str:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        parent = _call_name(node.value)
        return f"{parent}.{node.attr}" if parent else node.attr
    return ""


def _unique(items: list[str]) -> list[str]:
    return list(dict.fromkeys(item for item in items if item))

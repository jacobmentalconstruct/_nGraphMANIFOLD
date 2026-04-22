"""Project-owned MCP tool registration candidate surface."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from src.core.persistence import DEFAULT_CARTRIDGE_ID, SemanticCartridge
from src.core.representation.canonical import versioned_digest

from .local_mcp_adapter import (
    LocalMcpInspectionCapture,
    TRAVERSAL_CAPABILITY_NAME,
    build_default_traversal_inspection,
    run_traversal_mcp_adapter,
)
from .interaction_spine import (
    PROJECT_QUERY_CAPABILITY_NAME,
    PROJECT_QUERY_TOOL_NAME,
    InteractionCapture,
    run_project_query_interaction,
)
from .mcp_seam import build_mcp_seam_manifest

MCP_TOOL_REGISTRY_VERSION = "v1"
TRAVERSAL_TOOL_NAME = "ngraph.analysis.traverse_cartridge"


@dataclass(frozen=True)
class McpToolRegistration:
    """Serializable registration candidate for one MCP-facing tool."""

    tool_name: str
    capability_name: str
    title: str
    description: str
    input_schema: dict[str, Any]
    output_schema: dict[str, Any]
    readiness: str
    non_goals: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return {
            "tool_name": self.tool_name,
            "capability_name": self.capability_name,
            "title": self.title,
            "description": self.description,
            "input_schema": self.input_schema,
            "output_schema": self.output_schema,
            "readiness": self.readiness,
            "non_goals": list(self.non_goals),
        }


@dataclass(frozen=True)
class McpToolRegistry:
    """Manifest of project-owned MCP tool registration candidates."""

    registry_id: str
    version: str
    status: str
    tools: tuple[McpToolRegistration, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "registry_id": self.registry_id,
            "version": self.version,
            "status": self.status,
            "tools": [tool.to_dict() for tool in self.tools],
        }

    def get(self, tool_name: str) -> McpToolRegistration:
        for tool in self.tools:
            if tool.tool_name == tool_name:
                return tool
        raise ValueError(f"MCP tool is not registered: {tool_name}")


@dataclass(frozen=True)
class McpToolCallResult:
    """Result envelope for one registered local MCP tool candidate call."""

    call_id: str
    tool: dict[str, Any]
    status: str
    capture: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "call_id": self.call_id,
            "tool": self.tool,
            "status": self.status,
            "capture": self.capture,
        }


def build_mcp_tool_registry() -> McpToolRegistry:
    """Return registered MCP tool candidates without starting a protocol server."""
    tools = (_traversal_tool_registration(), _project_query_tool_registration())
    registry_id = versioned_digest(
        "mcptoolregistry",
        MCP_TOOL_REGISTRY_VERSION,
        {"tools": [tool.to_dict() for tool in tools]},
    )
    return McpToolRegistry(
        registry_id=registry_id,
        version=MCP_TOOL_REGISTRY_VERSION,
        status="local_registration_candidate",
        tools=tools,
    )


def call_registered_mcp_tool(
    tool_name: str,
    request: dict[str, Any],
    *,
    project_root: Path | str | None = None,
) -> McpToolCallResult:
    """Call one local registered MCP tool candidate with a JSON-like request."""
    registry = build_mcp_tool_registry()
    tool = registry.get(tool_name)
    if tool.tool_name == TRAVERSAL_TOOL_NAME:
        capture = _call_traversal_tool(request)
    elif tool.tool_name == PROJECT_QUERY_TOOL_NAME:
        capture = _call_project_query_tool(request, project_root=project_root)
    else:
        raise ValueError(f"No local caller implemented for MCP tool: {tool_name}")
    call_id = versioned_digest(
        "mcptoolcall",
        MCP_TOOL_REGISTRY_VERSION,
        {
            "tool": tool.to_dict(),
            "request": request,
            "capture_id": capture.capture_id,
        },
    )
    return McpToolCallResult(
        call_id=call_id,
        tool=tool.to_dict(),
        status="ok",
        capture=capture.to_dict(),
    )


def build_default_registered_tool_call(db_path: Path | str) -> McpToolCallResult:
    """Run the registered traversal tool over the default inspection fixture."""
    capture = build_default_traversal_inspection(db_path)
    request = {
        "db_path": capture.request["cartridge"]["db_path"],
        "cartridge_id": capture.request["cartridge"]["cartridge_id"],
        "seed_semantic_id": capture.request["seed_semantic_id"],
        "max_depth": capture.request["max_depth"],
        "max_steps": capture.request["max_steps"],
        "include_incoming": capture.request["include_incoming"],
    }
    return call_registered_mcp_tool(TRAVERSAL_TOOL_NAME, request)


def _call_traversal_tool(request: dict[str, Any]) -> LocalMcpInspectionCapture:
    db_path = _required_string(request, "db_path")
    seed_semantic_id = _required_string(request, "seed_semantic_id")
    cartridge_id = str(request.get("cartridge_id", DEFAULT_CARTRIDGE_ID))
    cartridge = SemanticCartridge(db_path, cartridge_id=cartridge_id)
    return run_traversal_mcp_adapter(
        cartridge,
        seed_semantic_id,
        max_depth=_optional_int(request, "max_depth", 2),
        max_steps=_optional_int(request, "max_steps", 64),
        include_incoming=bool(request.get("include_incoming", True)),
    )


def _call_project_query_tool(
    request: dict[str, Any],
    *,
    project_root: Path | str | None,
) -> InteractionCapture:
    root = Path(project_root) if project_root is not None else Path.cwd()
    query = _required_string(request, "query")
    limit = _optional_int(request, "limit", 3)
    context_stack = _optional_string_tuple(request, "context_stack")
    return run_project_query_interaction(
        root,
        query,
        limit=limit,
        context_stack=context_stack,
        actor="agent",
        source_surface="mcp-local",
    )


def _traversal_tool_registration() -> McpToolRegistration:
    seam_manifest = build_mcp_seam_manifest()
    capability = next(
        capability
        for capability in seam_manifest.capabilities
        if capability.name == TRAVERSAL_CAPABILITY_NAME
    )
    return McpToolRegistration(
        tool_name=TRAVERSAL_TOOL_NAME,
        capability_name=capability.name,
        title="Traverse Semantic Cartridge",
        description="Walk persisted relation projections from a seed semantic object and return a raw inspection capture.",
        input_schema={
            "type": "object",
            "properties": {
                "db_path": {"type": "string"},
                "cartridge_id": {"type": "string", "default": DEFAULT_CARTRIDGE_ID},
                "seed_semantic_id": {"type": "string"},
                "max_depth": {"type": "integer", "default": 2, "minimum": 0},
                "max_steps": {"type": "integer", "default": 64, "minimum": 1},
                "include_incoming": {"type": "boolean", "default": True},
            },
            "required": ["db_path", "seed_semantic_id"],
            "additionalProperties": False,
        },
        output_schema={
            "type": "object",
            "properties": {
                "call_id": {"type": "string"},
                "tool": {"type": "object"},
                "status": {"type": "string"},
                "capture": {"type": "object"},
            },
            "required": ["call_id", "tool", "status", "capture"],
            "additionalProperties": False,
        },
        readiness="registration_candidate",
        non_goals=(
            "no network server",
            "no protocol transport",
            "no host tool installation",
        ),
    )


def _project_query_tool_registration() -> McpToolRegistration:
    seam_manifest = build_mcp_seam_manifest()
    capability = next(
        capability
        for capability in seam_manifest.capabilities
        if capability.name == PROJECT_QUERY_CAPABILITY_NAME
    )
    return McpToolRegistration(
        tool_name=PROJECT_QUERY_TOOL_NAME,
        capability_name=capability.name,
        title="Project Query Through Context Layers",
        description="Project a query through English lexical, Python docs, and project-local context layers.",
        input_schema={
            "type": "object",
            "properties": {
                "query": {"type": "string"},
                "limit": {"type": "integer", "default": 3, "minimum": 1},
                "context_stack": {
                    "type": "array",
                    "items": {"type": "string"},
                    "default": [
                        "english_lexical_prior",
                        "python_docs_projection",
                        "project_local_docs",
                    ],
                },
            },
            "required": ["query"],
            "additionalProperties": False,
        },
        output_schema={
            "type": "object",
            "properties": {
                "call_id": {"type": "string"},
                "tool": {"type": "object"},
                "status": {"type": "string"},
                "capture": {"type": "object"},
            },
            "required": ["call_id", "tool", "status", "capture"],
            "additionalProperties": False,
        },
        readiness="registration_candidate",
        non_goals=(
            "no network server",
            "no protocol transport",
            "no host tool installation",
            "no cartridge merge",
        ),
    )


def _required_string(request: dict[str, Any], key: str) -> str:
    value = request.get(key)
    if not isinstance(value, str) or not value:
        raise ValueError(f"MCP tool request requires non-empty string field: {key}")
    return value


def _optional_int(request: dict[str, Any], key: str, default: int) -> int:
    value = request.get(key, default)
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"MCP tool request field must be an integer: {key}")
    return value


def _optional_string_tuple(request: dict[str, Any], key: str) -> tuple[str, ...]:
    value = request.get(key)
    if value is None:
        return (
            "english_lexical_prior",
            "python_docs_projection",
            "project_local_docs",
        )
    if not isinstance(value, list) or not all(isinstance(item, str) and item for item in value):
        raise ValueError(f"MCP tool request field must be a list of strings: {key}")
    return tuple(value)

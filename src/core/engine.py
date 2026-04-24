"""Core application engine placeholder for the scaffold tranche."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .config import AppSettings


@dataclass(frozen=True)
class SystemStatus:
    """Inspectable status returned by the scaffold runtime."""

    status: str
    project_root: Path
    active_tranche: str
    next_tranche: str


class ApplicationEngine:
    """Small core-owned facade used by the composition root."""

    def __init__(self, settings: AppSettings) -> None:
        self._settings = settings

    def status(self) -> SystemStatus:
        """Return the current scaffold status without touching future layers."""
        return SystemStatus(
            status="scaffold_ready",
            project_root=self._settings.project_root,
            active_tranche="Post-Prototype Hardening And Expansion",
            next_tranche="Shared Command Expansion And Truth-Surface Decisions",
        )

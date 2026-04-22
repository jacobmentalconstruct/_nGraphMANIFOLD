"""Central application settings."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class AppSettings:
    """Runtime settings owned by the core configuration domain."""

    project_root: Path
    docs_root: Path
    data_root: Path
    log_level: str = "INFO"

    @classmethod
    def from_environment(cls) -> "AppSettings":
        """Create settings from environment with project-local defaults."""
        project_root = Path(
            os.environ.get("NGRAPH_PROJECT_ROOT", Path(__file__).resolve().parents[3])
        ).resolve()
        return cls(
            project_root=project_root,
            docs_root=project_root / "_docs",
            data_root=project_root / "data",
            log_level=os.environ.get("NGRAPH_LOG_LEVEL", "INFO"),
        )

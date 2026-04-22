"""UI placeholder for the scaffold tranche."""

from __future__ import annotations

import logging

from src.core.config import AppSettings

LOGGER = logging.getLogger(__name__)


def launch_ui(settings: AppSettings) -> int:
    """Report UI deferral without constructing a premature interface."""
    LOGGER.info("UI is deferred for this tranche. project_root=%s", settings.project_root)
    return 0

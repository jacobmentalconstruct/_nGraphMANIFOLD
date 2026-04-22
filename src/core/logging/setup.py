"""Application logging configuration."""

from __future__ import annotations

import logging


def configure_logging(verbosity: int = 0) -> None:
    """Configure root logging for command-line scaffold execution."""
    level = logging.WARNING
    if verbosity == 0:
        level = logging.INFO
    elif verbosity >= 1:
        level = logging.DEBUG

    logging.basicConfig(
        level=level,
        format="%(levelname)s %(name)s: %(message)s",
        force=True,
    )

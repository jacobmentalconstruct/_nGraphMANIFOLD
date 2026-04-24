"""Scaffold verification tests."""

from __future__ import annotations

import unittest
from pathlib import Path

from src.app import main
from src.core.config import AppSettings
from src.core.engine import ApplicationEngine


PROJECT_ROOT = Path(__file__).resolve().parents[1]


class ScaffoldTests(unittest.TestCase):
    def test_required_paths_exist(self) -> None:
        required = [
            "src/app.py",
            "src/core/engine.py",
            "src/ui/gui_main.py",
            "README.md",
            "LICENSE.md",
            "requirements.txt",
            "setup_env.bat",
            "run.bat",
        ]
        for relative in required:
            with self.subTest(relative=relative):
                self.assertTrue((PROJECT_ROOT / relative).exists())

    def test_core_layer_packages_exist(self) -> None:
        layers = [
            "analysis",
            "config",
            "coordination",
            "execution",
            "logging",
            "persistence",
            "representation",
            "transformation",
        ]
        for layer in layers:
            with self.subTest(layer=layer):
                self.assertTrue((PROJECT_ROOT / "src" / "core" / layer / "__init__.py").exists())

    def test_status_command_returns_success(self) -> None:
        self.assertEqual(main(["status"]), 0)

    def test_engine_status_names_next_tranche(self) -> None:
        settings = AppSettings.from_environment()
        status = ApplicationEngine(settings).status()
        self.assertEqual(status.status, "scaffold_ready")
        self.assertIn("Post-Prototype Hardening", status.active_tranche)
        self.assertIn("Loop Safeguards", status.next_tranche)


if __name__ == "__main__":
    unittest.main()

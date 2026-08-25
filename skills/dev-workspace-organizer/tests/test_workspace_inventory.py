#!/usr/bin/env python3
"""Regression tests for safe workspace inventorying and JSON compatibility."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "workspace_inventory.py"


class WorkspaceInventoryTests(unittest.TestCase):
    def run_inventory(self, *arguments: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(SCRIPT), *arguments],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )

    def test_v2_json_preserves_v1_alias_types(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "workspace"
            result = self.run_inventory(
                str(root),
                "--init",
                "--dry-run",
                "--categories",
                "projects",
                "tools",
                "--json",
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            report = json.loads(result.stdout)
            self.assertEqual(report["schema_version"], 2)
            self.assertIs(report["root_exists"], False)
            self.assertIsInstance(report["root_git"], bool)
            self.assertIsInstance(report["nested_repositories"], list)
            self.assertTrue(
                all(isinstance(path, str) for path in report["nested_repositories"])
            )
            self.assertIsInstance(report["nested_repository_details"], list)
            self.assertTrue(report["would_create_root"])
            self.assertEqual(report["would_create"], ["projects", "tools"])
            self.assertFalse(root.exists())

    def test_init_is_idempotent_and_reports_nested_repository_details(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "workspace"
            first = self.run_inventory(
                str(root), "--init", "--categories", "projects", "--json"
            )
            self.assertEqual(first.returncode, 0, first.stderr)
            self.assertEqual(json.loads(first.stdout)["created"], ["projects"])

            nested = root / "projects" / "example"
            nested.mkdir()
            subprocess.run(["git", "init", "-q", str(nested)], check=True)
            second = self.run_inventory(
                str(root), "--init", "--categories", "projects", "--json"
            )
            self.assertEqual(second.returncode, 0, second.stderr)
            report = json.loads(second.stdout)
            self.assertEqual(report["created"], [])
            self.assertEqual(report["nested_repositories"], ["projects/example"])
            self.assertEqual(
                report["nested_repository_details"],
                [{"git_marker": "directory", "path": "projects/example"}],
            )

    def test_init_refuses_a_grouping_root_inside_git(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            repository = Path(temporary) / "repository"
            repository.mkdir()
            subprocess.run(["git", "init", "-q", str(repository)], check=True)
            root = repository / "workspace"
            result = self.run_inventory(
                str(root), "--init", "--categories", "projects", "--json"
            )
            self.assertEqual(result.returncode, 2)
            self.assertIn("inside Git repository", result.stderr)
            self.assertFalse(root.exists())


if __name__ == "__main__":
    unittest.main()

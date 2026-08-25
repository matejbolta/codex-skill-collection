#!/usr/bin/env python3
"""Regression tests for versioned project inventories."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "project_audit.py"


class ProjectInventoryTests(unittest.TestCase):
    def run_audit(self, payload: dict[str, object]) -> subprocess.CompletedProcess[str]:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            project = root / "project"
            project.mkdir()
            inventory = root / "projects.json"
            inventory.write_text(json.dumps(payload), encoding="utf-8")
            return subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--inventory",
                    str(inventory),
                    "--json",
                    "--allow-issues",
                ],
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )

    def test_schema_one_preserves_legacy_managed_software_policy(self) -> None:
        for payload in (
            {"projects": [{"path": "project"}]},
            {"schema_version": 1, "projects": [{"path": "project"}]},
        ):
            with self.subTest(payload=payload):
                result = self.run_audit(payload)
                self.assertEqual(result.returncode, 0, result.stderr)
                report = json.loads(result.stdout)
                self.assertEqual(report[0]["release_policy"], "semver")
                self.assertIn("missing CHANGELOG.md", report[0]["issues"])
                self.assertIn("missing semantic version source", report[0]["issues"])

    def test_schema_two_requires_an_explicit_release_policy(self) -> None:
        result = self.run_audit(
            {"schema_version": 2, "projects": [{"path": "project"}]}
        )
        self.assertEqual(result.returncode, 2)
        self.assertIn("release_policy is required", result.stderr)

    def test_schema_two_accepts_an_intentional_none_policy(self) -> None:
        result = self.run_audit(
            {
                "schema_version": 2,
                "projects": [
                    {
                        "path": "project",
                        "management": "grouping",
                        "release_policy": "none",
                    }
                ],
            }
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)[0]["release_policy"], "none")

    def test_unknown_schema_is_rejected(self) -> None:
        result = self.run_audit({"schema_version": 3, "projects": []})
        self.assertEqual(result.returncode, 2)
        self.assertIn("unsupported inventory schema_version 3", result.stderr)


if __name__ == "__main__":
    unittest.main()

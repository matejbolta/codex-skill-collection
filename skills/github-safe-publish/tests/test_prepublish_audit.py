#!/usr/bin/env python3
"""Regression tests for exact-ref history selection and secret redaction."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "prepublish_audit.py"


class PrepublishAuditTests(unittest.TestCase):
    def git(self, root: Path, *arguments: str) -> None:
        subprocess.run(["git", "-C", str(root), *arguments], check=True)

    def run_audit(self, root: Path, ref: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                str(root),
                "--history-scope",
                "exact",
                "--ref",
                ref,
                "--json",
            ],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )

    def test_exact_ref_excludes_unselected_secret_branch_and_redacts_matches(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "repository"
            root.mkdir()
            self.git(root, "init", "-q", "-b", "main")
            self.git(root, "config", "user.name", "Test User")
            self.git(
                root,
                "config",
                "user.email",
                "123+tester@" + "users.noreply.github.com",
            )
            (root / "README.md").write_text("public\n", encoding="utf-8")
            self.git(root, "add", "README.md")
            self.git(root, "commit", "-q", "-m", "initial")

            self.git(root, "switch", "-q", "-c", "secret-history")
            token = "ghp_" + ("A" * 36)
            (root / "credential.txt").write_text(token + "\n", encoding="utf-8")
            self.git(root, "add", "credential.txt")
            self.git(root, "commit", "-q", "-m", "secret fixture")
            self.git(root, "switch", "-q", "main")

            selected = self.run_audit(root, "main")
            self.assertEqual(selected.returncode, 0, selected.stdout)
            self.assertEqual(json.loads(selected.stdout)["status"], "clean")

            blocked = self.run_audit(root, "secret-history")
            self.assertEqual(blocked.returncode, 3, blocked.stdout)
            report = json.loads(blocked.stdout)
            self.assertEqual(report["status"], "blocked")
            self.assertNotIn(token, blocked.stdout)
            self.assertTrue(
                any(
                    finding["rule"] == "github-token"
                    and finding["detail"] == "matched value redacted"
                    for finding in report["findings"]
                )
            )


if __name__ == "__main__":
    unittest.main()

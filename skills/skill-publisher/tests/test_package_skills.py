#!/usr/bin/env python3
"""Regression tests for deterministic, licensed collection packaging."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "package_skills.py"
LICENSE = Path(__file__).resolve().parents[1] / "LICENSE"


def load_packager():
    spec = importlib.util.spec_from_file_location("package_skills", SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError("could not load package_skills.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class PackageSkillsTests(unittest.TestCase):
    def build(self, parent: Path, source: Path) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                "--skill",
                str(source),
                "--output",
                str(parent / "collection"),
                "--archive",
                str(parent / "collection.zip"),
                "--repo-url",
                "https://github.com/example/skills",
                "--title",
                "Test Collection",
                "--github-ci",
            ],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )

    def test_build_is_deterministic_complete_and_non_overwriting(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "example-skill"
            source.mkdir()
            (source / "SKILL.md").write_text(
                "---\n"
                "name: example-skill\n"
                "description: Use this example skill for packaging tests.\n"
                "---\n\n"
                "# Example\n",
                encoding="utf-8",
            )
            (source / "LICENSE").write_bytes(LICENSE.read_bytes())

            first_parent = root / "first"
            second_parent = root / "second"
            first_parent.mkdir()
            second_parent.mkdir()
            first = self.build(first_parent, source)
            second = self.build(second_parent, source)
            self.assertEqual(first.returncode, 0, first.stderr)
            self.assertEqual(second.returncode, 0, second.stderr)
            self.assertEqual(
                (first_parent / "collection.zip").read_bytes(),
                (second_parent / "collection.zip").read_bytes(),
            )

            collection = first_parent / "collection"
            self.assertEqual(
                (collection / "LICENSE").read_bytes(), LICENSE.read_bytes()
            )
            self.assertIn(
                "licensed under the [MIT License](LICENSE)",
                (collection / "README.md").read_text(encoding="utf-8"),
            )
            self.assertTrue(
                (collection / ".github/workflows/validate.yml").is_file()
            )
            manifest = json.loads((collection / "manifest.json").read_text())
            self.assertTrue(manifest["github_ci"])
            expected = {entry["path"]: entry for entry in manifest["files"]}
            actual = {
                path.relative_to(collection).as_posix()
                for path in collection.rglob("*")
                if path.is_file() and path.name != "manifest.json"
            }
            self.assertEqual(set(expected), actual)
            for relative, entry in expected.items():
                data = (collection / relative).read_bytes()
                self.assertEqual(entry["bytes"], len(data))
                self.assertEqual(entry["sha256"], hashlib.sha256(data).hexdigest())

            refused = self.build(first_parent, source)
            self.assertEqual(refused.returncode, 2)
            self.assertIn("Output already exists", refused.stderr)

    def test_archive_finalization_never_replaces_an_existing_file(self) -> None:
        packager = load_packager()
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            staged = root / "temporary.zip"
            destination = root / "collection.zip"
            staged.write_bytes(b"new archive")
            destination.write_bytes(b"existing archive")
            with self.assertRaises(packager.PackageError):
                packager.finalize_archive(staged, destination)
            self.assertEqual(destination.read_bytes(), b"existing archive")
            self.assertEqual(staged.read_bytes(), b"new archive")


if __name__ == "__main__":
    unittest.main()

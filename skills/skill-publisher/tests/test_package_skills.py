#!/usr/bin/env python3
"""Regression tests for deterministic packaging and generated CI contracts."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import os
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

    def write_skill(self, root: Path, name: str, license_name: str | None) -> Path:
        source = root / name
        source.mkdir()
        (source / "SKILL.md").write_text(
            "---\n"
            f"name: {name}\n"
            f"description: Use {name} for packaging regression tests.\n"
            "---\n\n"
            f"# {name}\n",
            encoding="utf-8",
        )
        if license_name:
            (source / license_name).write_bytes(LICENSE.read_bytes())
        return source

    def validate_collection(self, collection: Path) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(collection / ".github/scripts/validate_collection.py")],
            cwd=collection,
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
            self.assertEqual(manifest["collection_license"], "LICENSE")
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

    def test_unlicensed_skill_warns_but_generated_ci_is_valid(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = self.write_skill(root, "unlicensed-skill", None)
            parent = root / "build"
            parent.mkdir()
            built = self.build(parent, source)
            self.assertEqual(built.returncode, 0, built.stderr)
            self.assertIn("no conventional license file found", built.stdout)

            collection = parent / "collection"
            manifest = json.loads((collection / "manifest.json").read_text())
            self.assertIsNone(manifest["collection_license"])
            self.assertEqual(manifest["skills"][0]["license_files"], [])
            validated = self.validate_collection(collection)
            self.assertEqual(validated.returncode, 0, validated.stderr)
            self.assertIn("no conventional license file found", validated.stderr)

    def test_license_md_is_manifested_and_accepted_by_generated_ci(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = self.write_skill(root, "markdown-license", "LICENSE.md")
            parent = root / "build"
            parent.mkdir()
            built = self.build(parent, source)
            self.assertEqual(built.returncode, 0, built.stderr)

            collection = parent / "collection"
            manifest = json.loads((collection / "manifest.json").read_text())
            self.assertEqual(manifest["collection_license"], "LICENSE")
            self.assertEqual(manifest["skills"][0]["license_files"], ["LICENSE.md"])
            self.assertTrue((collection / "LICENSE").is_file())
            self.assertTrue(
                (collection / "skills/markdown-license/LICENSE.md").is_file()
            )
            validated = self.validate_collection(collection)
            self.assertEqual(validated.returncode, 0, validated.stderr)

    def test_validator_explains_missing_pyyaml_without_a_traceback(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = self.write_skill(root, "missing-yaml", "LICENSE")
            parent = root / "build"
            parent.mkdir()
            built = self.build(parent, source)
            self.assertEqual(built.returncode, 0, built.stderr)

            environment = os.environ.copy()
            environment.pop("PYTHONPATH", None)
            validator = parent / "collection/.github/scripts/validate_collection.py"
            completed = subprocess.run(
                [sys.executable, "-S", str(validator)],
                cwd=parent / "collection",
                env=environment,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
            self.assertEqual(completed.returncode, 2)
            self.assertIn("PyYAML is required", completed.stderr)
            self.assertNotIn("Traceback", completed.stderr)

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

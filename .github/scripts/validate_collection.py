#!/usr/bin/env python3
"""Validate one generated skill collection without mutating repository files."""

from __future__ import annotations

import hashlib
import json
import os
import py_compile
import re
import subprocess
import sys
import tempfile
from pathlib import Path, PurePosixPath

try:
    import yaml
except ModuleNotFoundError:
    print(
        'ERROR: PyYAML is required; install it with '
        '`python -m pip install "PyYAML>=6,<7"`.',
        file=sys.stderr,
    )
    raise SystemExit(2) from None


ROOT = Path(__file__).resolve().parents[2]
IGNORED_DIRS = {
    ".git",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    "__pycache__",
    "node_modules",
}
IGNORED_FILES = {".DS_Store", ".git"}
IGNORED_SUFFIXES = {".pyc", ".pyo"}
ALLOWED_FRONTMATTER = {"name", "description", "license", "allowed-tools", "metadata"}
SKILL_NAME = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


class ValidationError(RuntimeError):
    """A collection validation failure."""


def collection_files() -> dict[str, Path]:
    files: dict[str, Path] = {}
    for directory, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = sorted(name for name in dirnames if name not in IGNORED_DIRS)
        base = Path(directory)
        for name in sorted(filenames):
            path = base / name
            if (
                name in IGNORED_FILES
                or path.suffix in IGNORED_SUFFIXES
                or path == ROOT / "manifest.json"
            ):
                continue
            files[path.relative_to(ROOT).as_posix()] = path
    return files


def read_manifest() -> dict[str, object]:
    try:
        manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValidationError(f"cannot read manifest.json: {exc}") from exc
    if not isinstance(manifest, dict) or manifest.get("schema_version") != 2:
        raise ValidationError("manifest.json must be a schema-version 2 object")
    if manifest.get("manifest_excludes") != ["manifest.json"]:
        raise ValidationError("manifest_excludes must contain only manifest.json")
    return manifest


def validate_manifest(manifest: dict[str, object]) -> None:
    raw_entries = manifest.get("files")
    if not isinstance(raw_entries, list):
        raise ValidationError("manifest files must be an array")
    entries: dict[str, dict[str, object]] = {}
    for raw in raw_entries:
        if not isinstance(raw, dict) or set(raw) != {"path", "bytes", "sha256"}:
            raise ValidationError("every manifest file entry needs path, bytes, and sha256")
        relative = raw.get("path")
        if not isinstance(relative, str) or relative in entries:
            raise ValidationError(f"invalid or duplicate manifest path: {relative!r}")
        entries[relative] = raw

    actual = collection_files()
    if set(entries) != set(actual):
        missing = sorted(set(actual) - set(entries))
        extra = sorted(set(entries) - set(actual))
        raise ValidationError(
            f"manifest coverage mismatch; missing={missing}, extra={extra}"
        )
    for relative, path in actual.items():
        data = path.read_bytes()
        entry = entries[relative]
        if entry["bytes"] != len(data):
            raise ValidationError(f"byte count mismatch: {relative}")
        if entry["sha256"] != hashlib.sha256(data).hexdigest():
            raise ValidationError(f"SHA-256 mismatch: {relative}")

    collection_license = manifest.get("collection_license")
    if collection_license is not None:
        declared_file(ROOT, collection_license, "collection_license")


def declared_file(root: Path, value: object, label: str) -> Path:
    if not isinstance(value, str) or not value:
        raise ValidationError(f"{label} must be a non-empty relative path")
    relative = PurePosixPath(value)
    if relative.is_absolute() or ".." in relative.parts or relative.as_posix() != value:
        raise ValidationError(f"{label} must stay inside its declared root")
    target = root.joinpath(*relative.parts)
    if not target.is_file():
        raise ValidationError(f"declared file is missing for {label}: {value}")
    return target


def frontmatter(skill_file: Path) -> dict[str, object]:
    content = skill_file.read_text(encoding="utf-8")
    match = re.match(r"^---\n(.*?)\n---(?:\n|$)", content, re.DOTALL)
    if not match:
        raise ValidationError(f"invalid YAML frontmatter: {skill_file}")
    try:
        payload = yaml.safe_load(match.group(1))
    except yaml.YAMLError as exc:
        raise ValidationError(f"invalid YAML in {skill_file}: {exc}") from exc
    if not isinstance(payload, dict):
        raise ValidationError(f"frontmatter must be an object: {skill_file}")
    unexpected = sorted(set(payload) - ALLOWED_FRONTMATTER)
    if unexpected:
        raise ValidationError(f"unexpected frontmatter keys in {skill_file}: {unexpected}")
    return payload


def validate_skills(manifest: dict[str, object]) -> tuple[list[Path], list[str]]:
    raw_skills = manifest.get("skills")
    if not isinstance(raw_skills, list):
        raise ValidationError("manifest skills must be an array")
    declared: set[str] = set()
    test_files: list[Path] = []
    warnings: list[str] = []
    for raw in raw_skills:
        if not isinstance(raw, dict) or not isinstance(raw.get("name"), str):
            raise ValidationError("every skill manifest entry needs a string name")
        name = raw["name"]
        if name in declared or not SKILL_NAME.fullmatch(name):
            raise ValidationError(f"invalid or duplicate skill name: {name!r}")
        declared.add(name)
        root = ROOT / "skills" / name
        payload = frontmatter(root / "SKILL.md")
        if payload.get("name") != name:
            raise ValidationError(f"folder/frontmatter name mismatch: {name}")
        description = payload.get("description")
        if (
            not isinstance(description, str)
            or not description.strip()
            or len(description) > 1024
            or "<" in description
            or ">" in description
        ):
            raise ValidationError(f"invalid skill description: {name}")
        license_files = raw.get("license_files")
        if not isinstance(license_files, list):
            raise ValidationError(f"license_files must be an array: {name}")
        seen_license_files: set[str] = set()
        for index, relative in enumerate(license_files):
            if isinstance(relative, str) and relative in seen_license_files:
                raise ValidationError(f"duplicate license_files entry: {name}")
            declared_file(root, relative, f"{name}.license_files[{index}]")
            assert isinstance(relative, str)
            seen_license_files.add(relative)
        if not license_files:
            warnings.append(f"{name}: no conventional license file found")
        test_files.extend(sorted(root.glob("tests/test_*.py")))

    actual = {
        path.name
        for path in (ROOT / "skills").iterdir()
        if path.is_dir() and not path.name.startswith(".")
    }
    if actual != declared:
        raise ValidationError(
            f"skill directory mismatch; undeclared={sorted(actual - declared)}, "
            f"missing={sorted(declared - actual)}"
        )
    return test_files, warnings


def validate_python(test_files: list[Path]) -> None:
    scripts = sorted((ROOT / "skills").glob("*/scripts/*.py"))
    python_files = scripts + test_files
    with tempfile.TemporaryDirectory() as temporary:
        compile_root = Path(temporary)
        for index, path in enumerate(python_files):
            try:
                py_compile.compile(
                    str(path),
                    cfile=str(compile_root / f"{index}.pyc"),
                    doraise=True,
                )
            except py_compile.PyCompileError as exc:
                raise ValidationError(f"Python syntax failed for {path}: {exc}") from exc
    for path in test_files:
        completed = subprocess.run([sys.executable, str(path)], check=False)
        if completed.returncode:
            raise ValidationError(f"regression test failed: {path.relative_to(ROOT)}")


def main() -> int:
    try:
        manifest = read_manifest()
        validate_manifest(manifest)
        tests, warnings = validate_skills(manifest)
        validate_python(tests)
    except (OSError, UnicodeDecodeError, ValidationError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    for warning in warnings:
        print(f"WARNING: {warning}", file=sys.stderr)
    print(
        f"Validated {len(manifest['skills'])} skills, "
        f"{len(manifest['files'])} payload files, and {len(tests)} test files."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

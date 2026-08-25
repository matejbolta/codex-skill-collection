#!/usr/bin/env python3
"""Build a portable Codex skill collection and optional deterministic zip."""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import os
import re
import shutil
import stat
import sys
import tempfile
import zipfile
from pathlib import Path


IGNORED_DIRS = {
    ".git",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    "__pycache__",
    "node_modules",
}
IGNORED_FILES = {".DS_Store"}
IGNORED_SUFFIXES = {".pyc", ".pyo"}
SKILL_NAME = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
ABSOLUTE_USER_PATH = re.compile(r"(?<![A-Za-z0-9_])/(?:Users|home)/[^\s`'\"<>]+")
CREDENTIAL_ASSIGNMENT = re.compile(
    r"(?i)(?:api[_-]?key|access[_-]?token|auth[_-]?token|password|secret)"
    r"\s*[:=]\s*['\"]?[A-Za-z0-9_./+\-=]{12,}"
)


class PackageError(RuntimeError):
    """A safe, user-actionable packaging failure."""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Package Codex skills into a GitHub-compatible collection."
    )
    parser.add_argument(
        "--skill",
        action="append",
        required=True,
        help="Path to a skill folder. Repeat for multiple skills.",
    )
    parser.add_argument("--output", required=True, help="New collection directory.")
    parser.add_argument("--archive", help="Optional new .zip archive path.")
    parser.add_argument(
        "--repo-url",
        default="https://github.com/OWNER/REPO",
        help="Future GitHub repository URL used in generated prompts.",
    )
    parser.add_argument("--ref", default="main", help="Git ref used in prompts.")
    parser.add_argument(
        "--title", default="Codex Skill Collection", help="Collection title."
    )
    return parser.parse_args()


def unquote_yaml_scalar(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
        try:
            parsed = ast.literal_eval(value)
        except (SyntaxError, ValueError) as exc:
            raise PackageError(f"Invalid quoted YAML scalar: {value}") from exc
        if not isinstance(parsed, str):
            raise PackageError(f"Expected a string YAML scalar: {value}")
        return parsed
    return value


def read_frontmatter(skill_file: Path) -> tuple[str, str]:
    try:
        lines = skill_file.read_text(encoding="utf-8").splitlines()
    except UnicodeDecodeError as exc:
        raise PackageError(f"{skill_file} is not UTF-8 text") from exc
    if len(lines) < 4 or lines[0].strip() != "---":
        raise PackageError(f"{skill_file} has no YAML frontmatter")
    try:
        closing = next(i for i, line in enumerate(lines[1:], 1) if line.strip() == "---")
    except StopIteration as exc:
        raise PackageError(f"{skill_file} has unclosed YAML frontmatter") from exc

    fields: dict[str, str] = {}
    for line in lines[1:closing]:
        if ":" not in line or line[:1].isspace():
            continue
        key, value = line.split(":", 1)
        if key in {"name", "description"}:
            fields[key] = unquote_yaml_scalar(value)
    if not fields.get("name") or not fields.get("description"):
        raise PackageError(f"{skill_file} must define name and description")
    if not SKILL_NAME.fullmatch(fields["name"]):
        raise PackageError(f"Invalid skill name {fields['name']!r} in {skill_file}")
    return fields["name"], fields["description"]


def is_ignored(path: Path) -> bool:
    return (
        path.name in IGNORED_FILES
        or path.name in IGNORED_DIRS
        or path.suffix in IGNORED_SUFFIXES
    )


def iter_source_entries(root: Path):
    for directory, dirnames, filenames in os.walk(root, followlinks=False):
        base = Path(directory)
        dirnames[:] = sorted(name for name in dirnames if name not in IGNORED_DIRS)
        for name in sorted(dirnames + filenames):
            path = base / name
            if is_ignored(path):
                continue
            yield path


def within(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


def audit_source(root: Path) -> tuple[str, str]:
    skill_file = root / "SKILL.md"
    if not skill_file.is_file():
        raise PackageError(f"Missing SKILL.md in {root}")
    name, description = read_frontmatter(skill_file)
    if root.name != name:
        raise PackageError(
            f"Skill folder {root.name!r} does not match frontmatter name {name!r}"
        )

    findings: list[str] = []
    for path in iter_source_entries(root):
        if path.is_symlink():
            try:
                resolved = path.resolve(strict=True)
            except FileNotFoundError:
                findings.append(f"broken symlink: {path.relative_to(root)}")
                continue
            if not within(resolved, root):
                findings.append(
                    f"symlink escapes skill root: {path.relative_to(root)} -> {resolved}"
                )
                continue
        if not path.is_file() or path.stat().st_size > 2_000_000:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for match in ABSOLUTE_USER_PATH.finditer(text):
            findings.append(
                f"machine-specific path in {path.relative_to(root)}: {match.group(0)}"
            )
        if CREDENTIAL_ASSIGNMENT.search(text):
            findings.append(f"possible credential assignment in {path.relative_to(root)}")

    if findings:
        formatted = "\n  - ".join(findings)
        raise PackageError(f"Portability audit failed for {name}:\n  - {formatted}")
    return name, description


def copy_skill(source: Path, destination: Path) -> None:
    def ignore(directory: str, names: list[str]) -> set[str]:
        ignored: set[str] = set()
        for name in names:
            path = Path(directory) / name
            if is_ignored(path):
                ignored.add(name)
        return ignored

    shutil.copytree(source, destination, ignore=ignore, symlinks=False)
    escaping = [path for path in destination.rglob("*") if path.is_symlink()]
    if escaping:
        raise PackageError(f"Packaged skill unexpectedly contains symlinks: {escaping}")


def file_manifest(root: Path) -> list[dict[str, str | int]]:
    files: list[dict[str, str | int]] = []
    for path in sorted(candidate for candidate in root.rglob("*") if candidate.is_file()):
        data = path.read_bytes()
        files.append(
            {
                "path": path.relative_to(root).as_posix(),
                "bytes": len(data),
                "sha256": hashlib.sha256(data).hexdigest(),
            }
        )
    return files


def repo_slug(repo_url: str) -> str | None:
    match = re.fullmatch(
        r"https://github\.com/([^/]+/[^/]+?)(?:\.git)?/?", repo_url.strip()
    )
    return match.group(1) if match else None


def render_prompts(
    skills: list[dict[str, object]], repo_url: str, ref: str
) -> str:
    paths = [f"skills/{skill['name']}" for skill in skills]
    path_lines = "\n".join(f"- `{path}`" for path in paths)
    individual = "\n\n".join(
        (
            f"### {skill['name']}\n\n"
            "```text\n"
            f"Use $skill-installer to install {repo_url}/tree/{ref}/skills/{skill['name']}. "
            "Do not overwrite an existing skill; stop and report if it is already installed. "
            "After installation, remind me it becomes available on the next Codex turn.\n"
            "```"
        )
        for skill in skills
    )
    slug = repo_slug(repo_url)
    command = ""
    if slug:
        command_paths = " ".join(paths)
        command = (
            "\n## Exact installer command\n\n"
            "```sh\n"
            "python3 ~/.codex/skills/.system/skill-installer/scripts/"
            f"install-skill-from-github.py --repo {slug} --ref {ref} "
            f"--path {command_paths}\n"
            "```\n"
        )
    return (
        "# Recipient Install Prompts\n\n"
        "Replace `OWNER/REPO` first if the collection has not yet been published.\n\n"
        "## Install everything with another Codex agent\n\n"
        "```text\n"
        f"Use $skill-installer to install the following Codex skills from {repo_url} at ref {ref}:\n"
        f"{path_lines}\n\n"
        "Do not overwrite any existing skill. If a destination already exists, stop and report it. "
        "After installation, report which skills succeeded and remind me they become available on the next Codex turn.\n"
        "```\n\n"
        "## Install one skill\n\n"
        f"{individual}\n"
        f"{command}"
    )


def render_readme(
    title: str, skills: list[dict[str, object]], repo_url: str, ref: str
) -> str:
    catalog = "\n".join(
        f"- **${skill['name']}** — {skill['description']}" for skill in skills
    )
    return (
        f"# {title}\n\n"
        "A portable collection of personal Codex skills. Each skill is self-contained under "
        "`skills/` and can be installed independently.\n\n"
        "## Skills\n\n"
        f"{catalog}\n\n"
        "## Install\n\n"
        "Copy the ready-to-paste prompts from [INSTALL_PROMPTS.md](INSTALL_PROMPTS.md). "
        f"They target `{repo_url}` at ref `{ref}`.\n\n"
        "The bundled installer refuses to replace an existing destination. Installed skills "
        "become available on the next Codex turn.\n\n"
        "## Publishing note\n\n"
        "This collection does not choose a license or publish itself. The owner should review "
        "the manifest, choose repository visibility and licensing, then explicitly authorize "
        "any commit, remote creation, push, or public release.\n"
    )


def write_archive(collection: Path, archive: Path) -> None:
    archive.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(
        archive, "x", compression=zipfile.ZIP_DEFLATED, compresslevel=9
    ) as bundle:
        for path in sorted(candidate for candidate in collection.rglob("*") if candidate.is_file()):
            relative = Path(collection.name) / path.relative_to(collection)
            info = zipfile.ZipInfo(relative.as_posix(), date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = (stat.S_IMODE(path.stat().st_mode) & 0xFFFF) << 16
            bundle.writestr(info, path.read_bytes())


def main() -> int:
    args = parse_args()
    output = Path(args.output).expanduser().resolve(strict=False)
    archive = Path(args.archive).expanduser().resolve(strict=False) if args.archive else None
    if output.exists():
        raise PackageError(f"Output already exists: {output}")
    if archive and archive.exists():
        raise PackageError(f"Archive already exists: {archive}")

    sources: list[tuple[Path, str, str]] = []
    names: set[str] = set()
    for raw_source in args.skill:
        source = Path(raw_source).expanduser().resolve(strict=True)
        if not source.is_dir():
            raise PackageError(f"Skill path is not a directory: {source}")
        if within(output, source):
            raise PackageError(f"Output cannot be inside source skill: {source}")
        name, description = audit_source(source)
        if name in names:
            raise PackageError(f"Duplicate skill name: {name}")
        names.add(name)
        sources.append((source, name, description))

    output.parent.mkdir(parents=True, exist_ok=True)
    temporary_root = Path(
        tempfile.mkdtemp(prefix=f".{output.name}-", dir=output.parent)
    )
    staged = temporary_root / output.name
    try:
        skill_root = staged / "skills"
        skill_root.mkdir(parents=True)
        catalog: list[dict[str, object]] = []
        for source, name, description in sorted(sources, key=lambda item: item[1]):
            destination = skill_root / name
            copy_skill(source, destination)
            catalog.append(
                {
                    "name": name,
                    "description": description,
                    "path": f"skills/{name}",
                    "files": file_manifest(destination),
                }
            )

        manifest = {
            "collection": args.title,
            "repo_url": args.repo_url,
            "ref": args.ref,
            "skills": catalog,
        }
        (staged / "manifest.json").write_text(
            json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        (staged / "README.md").write_text(
            render_readme(args.title, catalog, args.repo_url, args.ref), encoding="utf-8"
        )
        (staged / "INSTALL_PROMPTS.md").write_text(
            render_prompts(catalog, args.repo_url, args.ref), encoding="utf-8"
        )
        (staged / ".gitignore").write_text(
            ".DS_Store\n__pycache__/\n*.py[cod]\n", encoding="utf-8"
        )
        os.replace(staged, output)
    finally:
        shutil.rmtree(temporary_root, ignore_errors=True)

    if archive:
        write_archive(output, archive)

    print(f"Packaged {len(sources)} skills in {output}")
    if archive:
        print(f"Archive: {archive}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, PackageError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(2)

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
from dataclasses import dataclass
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
LICENSE_NAMES = {
    "copying",
    "copying.md",
    "copying.txt",
    "license",
    "license.md",
    "license.txt",
}
SKILL_NAME = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
ABSOLUTE_UNIX_USER_PATH = re.compile(
    r"(?<![A-Za-z0-9_])/(?:Users|home)/[^\s`'\"<>]+"
)
ABSOLUTE_WINDOWS_USER_PATH = re.compile(
    r"(?i)(?<![A-Za-z0-9_])[A-Z]:\\Users\\[^\s`'\"<>]+"
)
CREDENTIAL_ASSIGNMENT = re.compile(
    r"(?i)(?:api[_-]?key|access[_-]?token|auth[_-]?token|password|secret)"
    r"\s*[:=]\s*['\"]?[A-Za-z0-9_./+\-=]{12,}"
)
SAFE_REF = re.compile(r"[A-Za-z0-9][A-Za-z0-9._/-]{0,254}")
GITHUB_URL = re.compile(
    r"https://github\.com/([A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+?)(?:\.git)?/?"
)
MAX_TEXT_SCAN_BYTES = 2_000_000


class PackageError(RuntimeError):
    """A safe, user-actionable packaging failure."""


@dataclass(frozen=True)
class SkillAudit:
    source: Path
    name: str
    description: str
    license_files: tuple[str, ...]
    warnings: tuple[str, ...]


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
    parser.add_argument(
        "--github-ci",
        action="store_true",
        help="Include the bundled GitHub Actions validation workflow.",
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
        closing = next(
            index for index, line in enumerate(lines[1:], 1) if line.strip() == "---"
        )
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


def scan_portability(path: Path, root: Path) -> tuple[list[str], list[str]]:
    findings: list[str] = []
    warnings: list[str] = []
    try:
        size = path.stat().st_size
    except OSError as exc:
        findings.append(f"cannot inspect {path.relative_to(root)}: {exc}")
        return findings, warnings
    if size > MAX_TEXT_SCAN_BYTES:
        warnings.append(
            f"large file not content-scanned: {path.relative_to(root)} ({size} bytes)"
        )
        return findings, warnings
    try:
        data = path.read_bytes()
        if b"\0" in data:
            return findings, warnings
        text = data.decode("utf-8")
    except UnicodeDecodeError:
        return findings, warnings
    except OSError as exc:
        findings.append(f"cannot inspect {path.relative_to(root)}: {exc}")
        return findings, warnings

    for pattern, label in (
        (ABSOLUTE_UNIX_USER_PATH, "Unix user path"),
        (ABSOLUTE_WINDOWS_USER_PATH, "Windows user path"),
    ):
        for match in pattern.finditer(text):
            findings.append(
                f"machine-specific {label} in {path.relative_to(root)}: {match.group(0)}"
            )
    if CREDENTIAL_ASSIGNMENT.search(text):
        findings.append(
            f"possible credential assignment in {path.relative_to(root)} (value redacted)"
        )
    return findings, warnings


def audit_source(root: Path) -> SkillAudit:
    skill_file = root / "SKILL.md"
    if not skill_file.is_file():
        raise PackageError(f"Missing SKILL.md in {root}")
    name, description = read_frontmatter(skill_file)
    if root.name != name:
        raise PackageError(
            f"Skill folder {root.name!r} does not match frontmatter name {name!r}"
        )

    findings: list[str] = []
    warnings: list[str] = []
    license_files: list[str] = []
    for path in iter_source_entries(root):
        relative = path.relative_to(root)
        if path.is_symlink():
            findings.append(f"nested symlink is not portable: {relative}")
            continue
        if path.is_file():
            if path.name.lower() in LICENSE_NAMES:
                license_files.append(relative.as_posix())
            path_findings, path_warnings = scan_portability(path, root)
            findings.extend(path_findings)
            warnings.extend(path_warnings)

    if not license_files:
        warnings.append("no conventional license file found")
    if findings:
        formatted = "\n  - ".join(findings)
        raise PackageError(f"Portability audit failed for {name}:\n  - {formatted}")
    return SkillAudit(
        source=root,
        name=name,
        description=description,
        license_files=tuple(sorted(license_files)),
        warnings=tuple(sorted(set(warnings))),
    )


def copy_skill(source: Path, destination: Path) -> None:
    def ignore(directory: str, names: list[str]) -> set[str]:
        return {
            name for name in names if is_ignored(Path(directory) / name)
        }

    shutil.copytree(source, destination, ignore=ignore, symlinks=True)
    symlinks = [path for path in destination.rglob("*") if path.is_symlink()]
    if symlinks:
        raise PackageError(f"Packaged skill unexpectedly contains symlinks: {symlinks}")


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


def shared_license_content(audits: list[SkillAudit]) -> bytes | None:
    """Return one common license only when every skill carries identical terms."""
    contents: list[bytes] = []
    for audit in audits:
        if len(audit.license_files) != 1:
            return None
        contents.append((audit.source / audit.license_files[0]).read_bytes())
    if not contents or any(content != contents[0] for content in contents[1:]):
        return None
    return contents[0]


def copy_github_ci(staged: Path) -> None:
    asset_root = Path(__file__).resolve().parent.parent / "assets" / "github"
    workflow = asset_root / "validate.yml"
    validator = asset_root / "validate_collection.py"
    if not workflow.is_file() or not validator.is_file():
        raise PackageError("Bundled GitHub CI assets are missing")
    workflow_target = staged / ".github" / "workflows" / "validate.yml"
    script_target = staged / ".github" / "scripts" / "validate_collection.py"
    workflow_target.parent.mkdir(parents=True, exist_ok=True)
    script_target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(workflow, workflow_target)
    shutil.copy2(validator, script_target)


def validate_render_inputs(repo_url: str, ref: str, title: str) -> str:
    if not title or title != title.strip() or any(ord(char) < 32 for char in title):
        raise PackageError("Title must be one non-empty printable line")
    match = GITHUB_URL.fullmatch(repo_url.strip())
    if not match:
        raise PackageError(
            "--repo-url must be https://github.com/OWNER/REPO or a concrete GitHub repository URL"
        )
    if not SAFE_REF.fullmatch(ref):
        raise PackageError("--ref contains unsupported characters")
    if (
        ".." in ref
        or "@{" in ref
        or "//" in ref
        or ref.endswith(("/", ".", ".lock"))
        or any(part.startswith(".") for part in ref.split("/"))
    ):
        raise PackageError("--ref is not a safe Git ref for generated prompts")
    return match.group(1)


def render_prompts(
    skills: list[dict[str, object]], repo_url: str, ref: str, slug: str
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
    title: str,
    skills: list[dict[str, object]],
    repo_url: str,
    ref: str,
    shared_license_label: str | None,
    github_ci: bool,
) -> str:
    catalog = "\n".join(
        f"- **${skill['name']}** — {skill['description']}" for skill in skills
    )
    unlicensed = [str(skill["name"]) for skill in skills if not skill["license_files"]]
    if shared_license_label == "MIT License":
        licensing = (
            "The collection and every included skill are licensed under the "
            "[MIT License](LICENSE)."
        )
    elif shared_license_label:
        licensing = (
            "The collection-level [LICENSE](LICENSE) and every included skill carry "
            "identical license terms."
        )
    elif unlicensed:
        licensing = (
            "No conventional license file was found for: "
            + ", ".join(f"`${name}`" for name in unlicensed)
            + ". Installation access does not itself grant broader reuse or redistribution rights."
        )
    else:
        licensing = (
            "License files are recorded per skill in `manifest.json`; review their "
            "terms before redistribution."
        )
    validation = (
        "\n## Validation\n\n"
        "Pull requests and pushes are checked by the bundled GitHub Actions workflow. "
        "It validates skill metadata, manifest coverage and hashes, Python syntax, and "
        "the committed regression tests.\n"
        if github_ci
        else ""
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
        "## Licensing note\n\n"
        f"{licensing}\n"
        f"{validation}"
    )


def write_archive(collection: Path, archive: Path, root_name: str) -> None:
    with zipfile.ZipFile(
        archive, "x", compression=zipfile.ZIP_DEFLATED, compresslevel=9
    ) as bundle:
        for path in sorted(
            candidate for candidate in collection.rglob("*") if candidate.is_file()
        ):
            relative = Path(root_name) / path.relative_to(collection)
            info = zipfile.ZipInfo(
                relative.as_posix(), date_time=(1980, 1, 1, 0, 0, 0)
            )
            info.create_system = 3
            info.compress_type = zipfile.ZIP_DEFLATED
            mode = stat.S_IMODE(path.stat().st_mode)
            info.external_attr = ((stat.S_IFREG | mode) & 0xFFFF) << 16
            bundle.writestr(info, path.read_bytes())


def finalize_archive(temporary_archive: Path, archive: Path) -> None:
    """Atomically publish an archive without replacing a concurrently created file."""
    try:
        os.link(temporary_archive, archive)
    except FileExistsError as exc:
        raise PackageError(f"Archive already exists: {archive}") from exc
    temporary_archive.unlink()


def validate_destination_paths(
    output: Path, archive: Path | None, sources: list[Path]
) -> None:
    if output.exists():
        raise PackageError(f"Output already exists: {output}")
    if archive and archive.exists():
        raise PackageError(f"Archive already exists: {archive}")
    for source in sources:
        if within(output, source):
            raise PackageError(f"Output cannot be inside source skill: {source}")
        if archive and within(archive, source):
            raise PackageError(f"Archive cannot be inside source skill: {source}")
    if archive and (within(archive, output) or within(output, archive)):
        raise PackageError("Output and archive paths must not contain one another")


def main() -> int:
    args = parse_args()
    slug = validate_render_inputs(args.repo_url, args.ref, args.title)
    output = Path(args.output).expanduser().resolve(strict=False)
    archive = (
        Path(args.archive).expanduser().resolve(strict=False) if args.archive else None
    )

    raw_sources = [Path(raw).expanduser().resolve(strict=True) for raw in args.skill]
    validate_destination_paths(output, archive, raw_sources)
    audits: list[SkillAudit] = []
    names: set[str] = set()
    for source in raw_sources:
        if not source.is_dir():
            raise PackageError(f"Skill path is not a directory: {source}")
        audit = audit_source(source)
        if audit.name in names:
            raise PackageError(f"Duplicate skill name: {audit.name}")
        names.add(audit.name)
        audits.append(audit)

    common_license = shared_license_content(audits)
    common_license_label = (
        "MIT License"
        if common_license and common_license.startswith(b"MIT License\n")
        else None
    )

    output.parent.mkdir(parents=True, exist_ok=True)
    if archive:
        archive.parent.mkdir(parents=True, exist_ok=True)
    temporary_root = Path(tempfile.mkdtemp(prefix=f".{output.name}-", dir=output.parent))
    staged = temporary_root / output.name
    temporary_archive: Path | None = None
    output_finalized = False
    archive_finalized = False
    try:
        skill_root = staged / "skills"
        skill_root.mkdir(parents=True)
        catalog: list[dict[str, object]] = []
        for audit in sorted(audits, key=lambda item: item.name):
            destination = skill_root / audit.name
            copy_skill(audit.source, destination)
            catalog.append(
                {
                    "name": audit.name,
                    "description": audit.description,
                    "path": f"skills/{audit.name}",
                    "license_files": list(audit.license_files),
                    "warnings": list(audit.warnings),
                    "files": file_manifest(destination),
                }
            )

        if common_license is not None:
            (staged / "LICENSE").write_bytes(common_license)
        if args.github_ci:
            copy_github_ci(staged)

        (staged / "README.md").write_text(
            render_readme(
                args.title,
                catalog,
                args.repo_url,
                args.ref,
                common_license_label or ("Shared license" if common_license else None),
                args.github_ci,
            ),
            encoding="utf-8",
        )
        (staged / "INSTALL_PROMPTS.md").write_text(
            render_prompts(catalog, args.repo_url, args.ref, slug), encoding="utf-8"
        )
        (staged / ".gitignore").write_text(
            ".DS_Store\n__pycache__/\n*.py[cod]\n", encoding="utf-8"
        )
        manifest = {
            "schema_version": 2,
            "collection": args.title,
            "repo_url": args.repo_url,
            "ref": args.ref,
            "github_ci": args.github_ci,
            "manifest_excludes": ["manifest.json"],
            "files": file_manifest(staged),
            "skills": catalog,
        }
        (staged / "manifest.json").write_text(
            json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )

        if archive:
            descriptor, temporary_name = tempfile.mkstemp(
                prefix=f".{archive.name}-", dir=archive.parent
            )
            os.close(descriptor)
            temporary_archive = Path(temporary_name)
            temporary_archive.unlink()
            write_archive(staged, temporary_archive, output.name)

        os.replace(staged, output)
        output_finalized = True
        if archive and temporary_archive:
            finalize_archive(temporary_archive, archive)
            temporary_archive = None
            archive_finalized = True
    except Exception:
        if output_finalized and output.exists() and archive and not archive_finalized:
            shutil.rmtree(output)
        raise
    finally:
        shutil.rmtree(temporary_root, ignore_errors=True)
        if temporary_archive and temporary_archive.exists():
            temporary_archive.unlink()

    print(f"Packaged {len(audits)} skills in {output}")
    if archive:
        print(f"Archive: {archive}")
    for audit in sorted(audits, key=lambda item: item.name):
        for warning in audit.warnings:
            print(f"WARNING {audit.name}: {warning}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, PackageError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(2)

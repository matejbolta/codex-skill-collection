#!/usr/bin/env python3
"""Read-only prepublication audit for a local Git repository.

Exit codes: 0 = no findings, 1 = review findings, 2 = blocking findings.
Matched secret values are never printed.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass(frozen=True)
class Finding:
    severity: str
    rule: str
    location: str
    detail: str


SECRET_RULES = (
    ("private-key", re.compile(rb"-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----")),
    ("github-token", re.compile(rb"(?:github_pat_[A-Za-z0-9_]{20,}|gh[pousr]_[A-Za-z0-9]{30,})")),
    ("openai-key", re.compile(rb"sk-(?:proj-)?[A-Za-z0-9_-]{20,}")),
    ("aws-access-key", re.compile(rb"(?:AKIA|ASIA)[0-9A-Z]{16}")),
    ("google-api-key", re.compile(rb"AIza[0-9A-Za-z_-]{30,}")),
    ("slack-token", re.compile(rb"xox[baprs]-[0-9A-Za-z-]{20,}")),
    ("stripe-live-key", re.compile(rb"(?:sk|rk)_live_[0-9A-Za-z]{16,}")),
    ("npm-token", re.compile(rb"npm_[A-Za-z0-9]{30,}")),
    (
        "authenticated-uri",
        re.compile(rb"[a-zA-Z][a-zA-Z0-9+.-]{1,15}://[^\s/:@]+:[^\s/@]+@[^\s]+"),
    ),
)
PERSONAL_RULES = (
    (
        "absolute-home-path",
        re.compile(rb"(?:/" rb"Users/|/" rb"home/)[^/\s]+/|[A-Za-z]:\\\\" rb"Users\\\\[^\\\s]+\\\\"),
    ),
    ("email-address", re.compile(rb"[A-Za-z0-9.!#$%&'*+/=?^_{|}~-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")),
)
SAFE_EMAIL_SUFFIXES = (b"@example.com", b"@example.org", b"@example.net")
BLOCKED_NAMES = {
    ".env",
    ".npmrc",
    ".pypirc",
    ".netrc",
    "credentials",
    "credentials.json",
    "id_dsa",
    "id_ecdsa",
    "id_ed25519",
    "id_rsa",
    "login data",
}
BLOCKED_PARTS = {".aws", ".gnupg", ".kube", ".ssh"}
BLOCKED_SUFFIXES = {".jks", ".key", ".keystore", ".p12", ".pem", ".pfx"}
REVIEW_SUFFIXES = {
    ".bak",
    ".db",
    ".dump",
    ".heic",
    ".jpeg",
    ".jpg",
    ".mov",
    ".mp4",
    ".pdf",
    ".png",
    ".sqlite",
    ".sqlite3",
    ".xlsx",
    ".docx",
    ".pptx",
    ".zip",
}
SAFE_TEMPLATE_SUFFIXES = {".example", ".sample", ".template"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("repository", type=Path)
    parser.add_argument(
        "--history-scope", choices=("none", "head", "all"), default="head"
    )
    parser.add_argument("--max-blob-bytes", type=int, default=2 * 1024 * 1024)
    parser.add_argument("--max-findings", type=int, default=200)
    parser.add_argument("--json", action="store_true")
    return parser.parse_args()


def run_git(root: Path, *args: str, check: bool = True) -> bytes:
    result = subprocess.run(
        ["git", "-C", str(root), *args],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if check and result.returncode:
        message = result.stderr.decode("utf-8", "replace").strip()
        raise SystemExit(f"git {' '.join(args)} failed: {message}")
    return result.stdout


def split_z(data: bytes) -> list[str]:
    return [item.decode("utf-8", "surrogateescape") for item in data.split(b"\0") if item]


def line_number(data: bytes, offset: int) -> int:
    return data.count(b"\n", 0, offset) + 1


def scan_content(data: bytes, location: str, include_personal: bool = True) -> list[Finding]:
    findings: list[Finding] = []
    for rule, pattern in SECRET_RULES:
        for match in pattern.finditer(data):
            findings.append(
                Finding("block", rule, f"{location}:{line_number(data, match.start())}", "matched value redacted")
            )
    if include_personal:
        for rule, pattern in PERSONAL_RULES:
            for match in pattern.finditer(data):
                if rule == "email-address" and match.group(0).lower().endswith(SAFE_EMAIL_SUFFIXES):
                    continue
                findings.append(
                    Finding("review", rule, f"{location}:{line_number(data, match.start())}", "matched value redacted")
                )
    return findings


def path_finding(path: str, state: str) -> Finding | None:
    normalized = path.replace("\\", "/")
    parts = {part.lower() for part in normalized.split("/")}
    name = normalized.rsplit("/", 1)[-1].lower()
    suffixes = {suffix.lower() for suffix in Path(name).suffixes}
    template = bool(suffixes & SAFE_TEMPLATE_SUFFIXES) or name.endswith("-example")
    if not template and (
        name in BLOCKED_NAMES or parts & BLOCKED_PARTS or suffixes & BLOCKED_SUFFIXES
    ):
        severity = "review" if state == "ignored" else "block"
        return Finding(severity, "sensitive-path", f"{state}:{path}", "inspect path without exposing its contents")
    if suffixes & REVIEW_SUFFIXES:
        return Finding("review", "binary-or-data-file", f"{state}:{path}", "inspect data and embedded metadata")
    return None


def scan_worktree(
    root: Path, paths: list[tuple[str, str]], max_blob_bytes: int
) -> tuple[list[Finding], dict[str, int]]:
    findings: list[Finding] = []
    stats = {"scanned_text_files": 0, "skipped_large_files": 0, "skipped_binary_files": 0}
    for state, relative in paths:
        risk = path_finding(relative, state)
        if risk:
            findings.append(risk)
        if state == "ignored":
            continue
        path = root / relative
        if not path.is_file() or path.is_symlink():
            continue
        try:
            size = path.stat().st_size
            if size > max_blob_bytes:
                stats["skipped_large_files"] += 1
                findings.append(Finding("review", "large-file-skipped", f"{state}:{relative}", f"larger than {max_blob_bytes} bytes"))
                continue
            data = path.read_bytes()
        except OSError as error:
            findings.append(Finding("review", "unreadable-file", f"{state}:{relative}", str(error)))
            continue
        if b"\0" in data:
            stats["skipped_binary_files"] += 1
            continue
        stats["scanned_text_files"] += 1
        findings.extend(scan_content(data, f"{state}:{relative}"))
    return findings, stats


def scan_index(
    root: Path, staged_paths: set[str], max_blob_bytes: int
) -> tuple[list[Finding], dict[str, int]]:
    findings: list[Finding] = []
    stats = {"index_blobs_scanned": 0, "index_blobs_skipped": 0}
    if not staged_paths:
        return findings, stats
    entries = run_git(root, "ls-files", "--stage", "-z").split(b"\0")
    for entry in entries:
        if not entry or b"\t" not in entry:
            continue
        metadata, raw_path = entry.split(b"\t", 1)
        fields = metadata.split()
        if len(fields) != 3 or fields[2] != b"0":
            continue
        oid = fields[1].decode("ascii")
        relative = raw_path.decode("utf-8", "surrogateescape")
        if relative not in staged_paths:
            continue
        raw_size = run_git(root, "cat-file", "-s", oid).decode("ascii").strip()
        size = int(raw_size)
        if size > max_blob_bytes:
            stats["index_blobs_skipped"] += 1
            findings.append(
                Finding(
                    "review",
                    "large-index-blob-skipped",
                    f"index:{relative}",
                    f"larger than {max_blob_bytes} bytes",
                )
            )
            continue
        data = run_git(root, "cat-file", "blob", oid)
        stats["index_blobs_scanned"] += 1
        if b"\0" not in data:
            findings.extend(scan_content(data, f"index:{relative}"))
    return findings, stats


def history_objects(root: Path, scope: str) -> tuple[list[str], dict[str, str]]:
    if scope == "none":
        return [], {}
    has_head = subprocess.run(
        ["git", "-C", str(root), "rev-parse", "--verify", "HEAD"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    ).returncode == 0
    if not has_head:
        return [], {}
    selector = "--all" if scope == "all" else "HEAD"
    output = run_git(root, "rev-list", "--objects", selector).decode("utf-8", "surrogateescape")
    object_ids: list[str] = []
    names: dict[str, str] = {}
    for line in output.splitlines():
        oid, _, name = line.partition(" ")
        if oid not in names:
            object_ids.append(oid)
            names[oid] = name
        elif not names[oid] and name:
            names[oid] = name
    return object_ids, names


def scan_history(
    root: Path, scope: str, max_blob_bytes: int
) -> tuple[list[Finding], dict[str, int]]:
    findings: list[Finding] = []
    stats = {"history_blobs_scanned": 0, "history_blobs_skipped": 0}
    object_ids, names = history_objects(root, scope)
    if not object_ids:
        return findings, stats

    check_result = subprocess.run(
        ["git", "-C", str(root), "cat-file", "--batch-check=%(objectname) %(objecttype) %(objectsize)"],
        input=("\n".join(object_ids) + "\n").encode(),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if check_result.returncode:
        raise SystemExit(check_result.stderr.decode("utf-8", "replace").strip())
    small_blobs: list[str] = []
    for line in check_result.stdout.decode("ascii", "replace").splitlines():
        fields = line.split()
        if len(fields) != 3 or fields[1] != "blob":
            continue
        oid, _, raw_size = fields
        size = int(raw_size)
        if size <= max_blob_bytes:
            small_blobs.append(oid)
        else:
            stats["history_blobs_skipped"] += 1
            location = names.get(oid) or f"object-{oid[:12]}"
            findings.append(Finding("review", "large-history-blob-skipped", f"history:{location}@{oid[:12]}", f"larger than {max_blob_bytes} bytes"))

    process = subprocess.Popen(
        ["git", "-C", str(root), "cat-file", "--batch"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    assert process.stdin is not None and process.stdout is not None
    process.stdin.write(("\n".join(small_blobs) + "\n").encode())
    process.stdin.close()
    for expected_oid in small_blobs:
        header = process.stdout.readline().decode("ascii", "replace").strip().split()
        if len(header) != 3 or header[1] != "blob":
            raise SystemExit(f"unexpected git cat-file response for {expected_oid[:12]}")
        oid, _, raw_size = header
        size = int(raw_size)
        data = process.stdout.read(size)
        process.stdout.read(1)
        stats["history_blobs_scanned"] += 1
        if b"\0" in data:
            continue
        name = names.get(oid) or f"object-{oid[:12]}"
        findings.extend(scan_content(data, f"history:{name}@{oid[:12]}"))
    stderr = process.stderr.read().decode("utf-8", "replace") if process.stderr else ""
    if process.wait() != 0:
        raise SystemExit(f"git cat-file failed: {stderr.strip()}")
    return findings, stats


def nested_git_markers(root: Path) -> list[str]:
    markers: list[str] = []
    prune = {".git", "node_modules", ".venv", "venv", "__pycache__", "dist", "build"}
    for current, dirs, files in os.walk(root, followlinks=False):
        current_path = Path(current)
        if current_path != root and (".git" in dirs or ".git" in files):
            markers.append(str(current_path.relative_to(root)))
            dirs[:] = []
            continue
        dirs[:] = [name for name in dirs if name not in prune and not (current_path / name).is_symlink()]
    return sorted(markers)


def author_email_findings(root: Path, scope: str) -> list[Finding]:
    if scope == "none":
        return []
    selector = "--all" if scope == "all" else "HEAD"
    output = run_git(root, "log", selector, "--format=%ae%x00%ce%x00", check=False)
    emails = {item.decode("utf-8", "replace").strip() for item in output.split(b"\0") if item.strip()}
    exposed = {email for email in emails if "noreply" not in email.lower()}
    if not exposed:
        return []
    return [
        Finding(
            "review",
            "commit-email-privacy",
            "history",
            f"{len(exposed)} non-noreply author or committer email address(es); values redacted",
        )
    ]


def deduplicate(findings: list[Finding]) -> list[Finding]:
    return list(dict.fromkeys(findings))


def main() -> int:
    args = parse_args()
    if args.max_blob_bytes < 1 or args.max_findings < 1:
        raise SystemExit("size and finding limits must be positive")
    requested = args.repository.expanduser().resolve()
    if not requested.is_dir():
        raise SystemExit(f"repository directory does not exist: {requested}")
    root_output = run_git(requested, "rev-parse", "--show-toplevel")
    root = Path(root_output.decode().strip()).resolve()

    tracked = split_z(run_git(root, "ls-files", "-z"))
    untracked = split_z(run_git(root, "ls-files", "--others", "--exclude-standard", "-z"))
    ignored = split_z(run_git(root, "ls-files", "--others", "--ignored", "--exclude-standard", "--directory", "-z"))
    staged_paths = set(split_z(run_git(root, "diff", "--cached", "--name-only", "-z", check=False)))
    state_paths = [("tracked", path) for path in tracked]
    state_paths.extend(("untracked", path) for path in untracked)
    state_paths.extend(("ignored", path) for path in ignored)

    findings, file_stats = scan_worktree(root, state_paths, args.max_blob_bytes)
    index_findings, index_stats = scan_index(root, staged_paths, args.max_blob_bytes)
    findings.extend(index_findings)
    history_findings, history_stats = scan_history(root, args.history_scope, args.max_blob_bytes)
    findings.extend(history_findings)
    findings.extend(author_email_findings(root, args.history_scope))
    for nested in nested_git_markers(root):
        findings.append(Finding("review", "nested-repository", nested, "confirm this boundary or submodule is intentional"))

    unstaged = run_git(root, "diff", "--name-only", "-z", check=False).split(b"\0")
    findings = deduplicate(findings)
    counts = {severity: sum(item.severity == severity for item in findings) for severity in ("block", "review")}
    truncated = max(0, len(findings) - args.max_findings)
    shown = findings[: args.max_findings]
    report = {
        "repository": str(root),
        "history_scope": args.history_scope,
        "counts": counts,
        "state": {
            "tracked": len(tracked),
            "staged": len(staged_paths),
            "unstaged": sum(bool(item) for item in unstaged),
            "untracked": len(untracked),
            "ignored_entries": len(ignored),
        },
        "scan": {**file_stats, **index_stats, **history_stats},
        "findings": [asdict(item) for item in shown],
        "findings_truncated": truncated,
        "note": "Pattern-based, read-only audit; matched values are redacted and a clean result is not a security guarantee.",
    }
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(f"repository: {root}")
        print(f"history scope: {args.history_scope}")
        print(f"state: {report['state']}")
        print(f"scan: {report['scan']}")
        print(f"findings: block={counts['block']} review={counts['review']}")
        for item in shown:
            print(f"[{item.severity}] {item.rule} {item.location}: {item.detail}")
        if truncated:
            print(f"... {truncated} additional finding(s) omitted")
        print(report["note"])
    return 2 if counts["block"] else 1 if counts["review"] else 0


if __name__ == "__main__":
    raise SystemExit(main())

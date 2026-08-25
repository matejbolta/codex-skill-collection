# Project audit inventory

Read this reference before using `scripts/project_audit.py`. The audit is
read-only and accepts one JSON inventory.

## Example

Run `python3 scripts/project_audit.py --example-inventory` to print a complete
example. The top level is an object with a `projects` array:

```json
{
  "projects": [
    {
      "name": "example-app",
      "path": "projects/example-app",
      "management": "managed",
      "kind": "software",
      "release_policy": "semver",
      "version_source": "pyproject.toml",
      "require_current_tag": false
    },
    {
      "name": "research-notes",
      "path": "records/research-notes",
      "management": "managed",
      "kind": "records",
      "release_policy": "none"
    }
  ]
}
```

Relative `path` values resolve against the directory containing the inventory,
not the shell's current directory. Home-relative paths beginning with `~` and
absolute paths are supported.

## Project fields

| Field | Type | Required | Meaning |
| --- | --- | --- | --- |
| `path` | string | yes | Project directory. Relative paths resolve from the inventory file. |
| `name` | string | no | Report label; defaults to the path's final component. Names must be unique. |
| `management` | string | no | `managed` (default), `grouping`, `upstream`, or `empty`. |
| `kind` | string | no | `software` (default) or `records`. |
| `release_policy` | string | no | `none` (default) or `semver`. Only `semver` requires version/changelog checks. |
| `version_source` | string | no | Canonical relative version file for a project with multiple independent products. |
| `require_current_tag` | boolean | no | When true, require local tag `v<canonical-version>`; valid only with `release_policy: semver`. |

`version_source` must stay inside the project and may not be absolute or contain
`..`. Supported values are a JSON file containing a top-level `version`, a TOML
file containing `project.version`, or a plain file named `VERSION`.

## Management modes

- `managed`: audit the directory as an independent governed project, including
  continuity files, repository root, and optional release policy.
- `grouping`: record a container directory that is not itself governed as an
  independent project. The audit checks existence but does not require project
  records.
- `upstream`: record externally governed source. The audit checks existence and
  reports it as outside ordinary local governance.
- `empty`: assert that the directory is empty. A missing directory or any
  contained entry is an issue.

## Exit behavior

- Exit `0` when no issues are found, or whenever `--allow-issues` is supplied.
- Exit `1` when the audit completes and finds governance issues.
- Exit `2` for invalid JSON, invalid schema, unreadable input, or another
  operational error.

`--json` writes only the result array to standard output. The summary remains on
standard error so the JSON can be piped safely.

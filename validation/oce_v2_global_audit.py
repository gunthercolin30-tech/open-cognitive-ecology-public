from __future__ import annotations

import ast
import hashlib
import json
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SCHEMA = "oce.p008.global_audit.v1"
ROOT_DEFAULT = Path.home() / "open-cognitive-ecology"

EXCLUDED_PARTS = frozenset({
    ".git", ".oif_backups", "__pycache__", "__MACOSX",
    ".pytest_cache", ".mypy_cache", ".ruff_cache", "node_modules",
    "dist", "build",
})
EXCLUDED_PREFIXES = (".venv", "venv", "env")
HISTORICAL_PREFIXES = (
    "audit_ZPP", "audit_global_errors", "m0_audit_bundle",
    "n_axis_audit", "H19_required_files", "H20_required_files",
    "replication_packages",
)
DOMAIN_RULES = {
    "memory": ("memory", "autobiographical", "persistence"),
    "governance": ("governance", "approval", "constitutional"),
    "oif": ("oif", "interface"),
    "ay": ("ay", "theory", "theorem"),
    "acee": ("acee", "evolution", "mutation"),
    "prediction": ("prediction", "predictor", "forecast"),
    "simulation": ("simulation", "simulator", "trajectory"),
    "world_model": ("world_model", "worldmodel"),
    "resources": ("resource", "infrastructure", "capability"),
    "persistence": ("persistence", "checkpoint", "state_store"),
    "tests": ("test_", "_test", "fast_acceptance", "validation"),
}


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _is_excluded(rel: Path) -> bool:
    for part in rel.parts:
        if part in EXCLUDED_PARTS:
            return True
        if part.startswith(EXCLUDED_PREFIXES):
            return True
        if part.startswith(HISTORICAL_PREFIXES):
            return True
    if rel.name.startswith("."):
        return True
    if rel.suffix in {".pyc", ".bak"} or ".bak" in rel.name:
        return True
    return False


def _git_tracked_python_paths(root: Path) -> list[Path]:
    try:
        cp = subprocess.run(
            ["git", "ls-files", "-z", "--", "*.py"],
            cwd=str(root),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )
    except Exception:
        return []
    result: list[Path] = []
    for raw in cp.stdout.split(b"\0"):
        if not raw:
            continue
        rel = Path(os.fsdecode(raw))
        path = root / rel
        if path.is_file():
            result.append(path)
    return sorted(result, key=lambda p: p.relative_to(root).as_posix())


def _baseline_python_paths(root: Path) -> list[Path]:
    manifest = root / "p007_baseline_manifest.json"
    if not manifest.is_file():
        return []
    try:
        data = json.loads(manifest.read_text(encoding="utf-8"))
    except Exception:
        return []
    raw = data.get("functional_files", {})
    if isinstance(raw, dict):
        names = raw.keys()
    elif isinstance(raw, list):
        names = raw
    else:
        names = []
    result: list[Path] = []
    for name in names:
        rel = Path(str(name))
        if rel.suffix != ".py":
            continue
        path = root / rel
        if path.is_file():
            result.append(path)
    return sorted(result, key=lambda p: p.relative_to(root).as_posix())


def source_paths(root: Path) -> list[Path]:
    root = root.expanduser().resolve()
    candidates = {
        p.resolve()
        for p in (_baseline_python_paths(root) + _git_tracked_python_paths(root))
        if p.is_file()
    }
    self_path = root / "validation" / "oce_v2_global_audit.py"
    if self_path.is_file():
        candidates.add(self_path.resolve())

    paths: list[Path] = []
    for path in sorted(candidates, key=lambda p: p.relative_to(root).as_posix()):
        rel = path.relative_to(root)
        if _is_excluded(rel):
            continue
        paths.append(path)

    if not paths:
        raise RuntimeError("P008 audit scope is empty")
    return paths


def _literal_assignment(tree: ast.AST, name: str) -> Any:
    for node in getattr(tree, "body", []):
        if not isinstance(node, (ast.Assign, ast.AnnAssign)):
            continue
        targets = node.targets if isinstance(node, ast.Assign) else [node.target]
        if not any(isinstance(t, ast.Name) and t.id == name for t in targets):
            continue
        try:
            return ast.literal_eval(node.value)
        except Exception:
            return None
    return None


def _call_name(node: ast.Call) -> str:
    func = node.func
    parts: list[str] = []
    while isinstance(func, ast.Attribute):
        parts.append(func.attr)
        func = func.value
    if isinstance(func, ast.Name):
        parts.append(func.id)
    return ".".join(reversed(parts))


def inspect_module(path: Path, root: Path) -> dict[str, Any]:
    rel = path.relative_to(root).as_posix()
    raw = path.read_bytes()
    text = raw.decode("utf-8", errors="replace")
    record: dict[str, Any] = {
        "path": rel,
        "sha256": _sha256_bytes(raw),
        "bytes": len(raw),
        "line_count": len(text.splitlines()),
        "parse_status": "OK",
        "imports": [],
        "calls": [],
        "classes": [],
        "functions": [],
        "primitive": None,
        "declared_dependencies": [],
        "interfaces": [],
        "domains": [],
    }
    try:
        tree = ast.parse(text, filename=rel)
    except SyntaxError as exc:
        record["parse_status"] = "SYNTAX_ERROR"
        record["parse_error"] = {
            "line": exc.lineno,
            "offset": exc.offset,
            "message": exc.msg,
        }
        return record

    imports: set[str] = set()
    calls: set[str] = set()
    interfaces: set[str] = set()
    classes: list[str] = []
    functions: list[str] = []

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            base = node.module or ""
            imports.add(("." * node.level) + base)
        elif isinstance(node, ast.Call):
            name = _call_name(node)
            if name:
                calls.add(name)
        elif isinstance(node, ast.ClassDef):
            classes.append(node.name)
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            functions.append(node.name)
            if not node.name.startswith("_"):
                interfaces.add(node.name)

    primitive = _literal_assignment(tree, "PRIMITIVE")
    dependencies = _literal_assignment(tree, "DEPENDENCIES")
    if not isinstance(dependencies, (list, tuple, set)):
        dependencies = []

    lowered = rel.lower()
    domains = sorted(
        name for name, needles in DOMAIN_RULES.items()
        if any(needle in lowered for needle in needles)
    )

    record.update({
        "imports": sorted(imports),
        "calls": sorted(calls),
        "classes": sorted(set(classes)),
        "functions": sorted(set(functions)),
        "primitive": primitive if isinstance(primitive, str) else None,
        "declared_dependencies": sorted(str(x) for x in dependencies),
        "interfaces": sorted(interfaces),
        "domains": domains,
    })
    return record


def _git_state(root: Path) -> dict[str, Any]:
    def run(*args: str) -> str | None:
        try:
            cp = subprocess.run(
                ["git", *args], cwd=str(root), text=True,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                check=True,
            )
            return cp.stdout.strip()
        except Exception:
            return None

    return {
        "branch": run("branch", "--show-current") or "UNKNOWN",
        "head": run("rev-parse", "HEAD") or "UNKNOWN",
        "describe": run("describe", "--tags", "--always", "--dirty") or "UNKNOWN",
    }


def _baseline(root: Path) -> dict[str, Any]:
    path = root / "p007_baseline_manifest.json"
    if not path.is_file():
        return {
            "status": "UNKNOWN",
            "reason": "p007_baseline_manifest.json missing",
        }
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        return {"status": "UNKNOWN", "reason": type(exc).__name__}

    raw_locked = data.get("functional_files", {})
    if isinstance(raw_locked, dict):
        locked_all = set(str(x) for x in raw_locked)
    elif isinstance(raw_locked, list):
        locked_all = set(str(x) for x in raw_locked)
    else:
        locked_all = set()

    locked_python = {p for p in locked_all if p.endswith(".py")}
    current_tracked_python = {
        p.relative_to(root).as_posix()
        for p in _git_tracked_python_paths(root)
    }
    baseline_present_python = {
        p.relative_to(root).as_posix()
        for p in _baseline_python_paths(root)
    }
    audited_python = {
        p.relative_to(root).as_posix()
        for p in source_paths(root)
    }

    return {
        "status": "OBSERVED",
        "baseline_identity_sha256": data.get(
            "baseline_identity_sha256", "UNKNOWN"
        ),
        "baseline_functional_file_count": data.get(
            "functional_file_count", "UNKNOWN"
        ),
        "baseline_python_path_count": len(locked_python),
        "baseline_python_paths_present_now": len(baseline_present_python),
        "current_tracked_python_path_count": len(current_tracked_python),
        "current_audited_python_source_count": len(audited_python),
        "tracked_python_paths_added_vs_baseline": sorted(
            current_tracked_python - locked_python
        ),
        "baseline_python_paths_missing_now": sorted(
            locked_python - baseline_present_python
        ),
        "tracked_python_paths_excluded_from_audit_scope": sorted(
            current_tracked_python - audited_python
        ),
        "baseline_python_paths_excluded_from_audit_scope": sorted(
            baseline_present_python - audited_python
        ),
    }


def build_audit(root: Path | None = None) -> dict[str, Any]:
    root = (root or ROOT_DEFAULT).expanduser().resolve()
    modules = [inspect_module(p, root) for p in source_paths(root)]

    parse_errors = [m["path"] for m in modules if m["parse_status"] != "OK"]
    baseline_python_names = {
        p.relative_to(root).as_posix()
        for p in _baseline_python_paths(root)
    }
    tracked_python_names = {
        p.relative_to(root).as_posix()
        for p in _git_tracked_python_paths(root)
    }
    syntax_findings = [
        {
            "path": m["path"],
            "status": m["parse_status"],
            "error": m.get("parse_error", {}),
            "baseline_member": m["path"] in baseline_python_names,
            "git_tracked": m["path"] in tracked_python_names,
            "classification": (
                "BASELINE_SYNTAX_FINDING"
                if m["path"] in baseline_python_names
                else "CURRENT_SYNTAX_FINDING"
            ),
        }
        for m in modules
        if m["parse_status"] != "OK"
    ]
    domain_coverage = {
        domain: sorted(m["path"] for m in modules if domain in m["domains"])
        for domain in DOMAIN_RULES
    }
    import_edges = sum(len(m["imports"]) for m in modules)
    call_symbols = sum(len(m["calls"]) for m in modules)
    interface_symbols = sum(len(m["interfaces"]) for m in modules)

    epistemic = {
        "architecture_completeness": "UNKNOWN",
        "runtime_call_exercised": "UNKNOWN",
        "dynamic_import_resolution": "UNKNOWN",
        "phenomenal_subjectivity": "UNDETERMINED",
        "functional_conclusion_only": True,
        "notes": [
            "AST imports/calls are static observations, not proof of runtime execution.",
            "Domain coverage is lexical/path-based evidence, not capability validation.",
            "UNKNOWN is preserved where static evidence cannot justify a conclusion.",
        ],
    }

    stable = {
        "schema": SCHEMA,
        "git": _git_state(root),
        "baseline_comparison": _baseline(root),
        "summary": {
            "python_source_count": len(modules),
            "parse_error_count": len(parse_errors),
            "syntax_finding_count": len(syntax_findings),
            "audit_execution_status": "COMPLETED",
            "architecture_findings_status": (
                "FINDINGS_PRESENT" if syntax_findings else "NO_SYNTAX_FINDINGS"
            ),
            "static_import_edge_count": import_edges,
            "static_call_symbol_count": call_symbols,
            "public_interface_symbol_count": interface_symbols,
            "domain_module_counts": {
                k: len(v) for k, v in sorted(domain_coverage.items())
            },
        },
        "parse_errors": parse_errors,
        "syntax_findings": syntax_findings,
        "domain_coverage": domain_coverage,
        "modules": modules,
        "epistemic_status": epistemic,
    }
    fingerprint = _sha256_bytes(
        json.dumps(stable, sort_keys=True, separators=(",", ":")).encode("utf-8")
    )
    report = dict(stable)
    report["audit_fingerprint_sha256"] = fingerprint
    report["generated_at_utc"] = datetime.now(timezone.utc).isoformat()
    return report


def write_report(
    root: Path | None = None,
    output: Path | None = None,
) -> dict[str, Any]:
    root = (root or ROOT_DEFAULT).expanduser().resolve()
    report = build_audit(root)
    output = output or (root / "p008_global_audit_report.json")
    output = output.expanduser().resolve()
    output.write_text(
        json.dumps(report, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return report


def main() -> int:
    report = write_report()
    print("P008_GLOBAL_AUDIT_OK")
    print("schema=%s" % report["schema"])
    print("python_source_count=%d" % report["summary"]["python_source_count"])
    print("parse_error_count=%d" % report["summary"]["parse_error_count"])
    print("audit_fingerprint_sha256=%s" % report["audit_fingerprint_sha256"])
    print(
        "p007_baseline_identity=%s"
        % report["baseline_comparison"].get(
            "baseline_identity_sha256", "UNKNOWN"
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

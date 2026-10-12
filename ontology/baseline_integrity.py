from __future__ import annotations

import hashlib
import json
import platform
from collections.abc import Mapping, Sequence
from ontology.governed_evidence_effect_policy import EvidenceEffectDecision, GovernedEvidenceEffectPolicy
from ontology.governed_evidence_filesystem_bridge import GovernedEvidenceFilesystemBridge
from ontology.governed_git_exact_process import governed_git_subprocess as subprocess
import sys
from ontology.governed_bounded_python_process import pip_freeze
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FUNCTIONAL_SUFFIXES = frozenset({".py", ".toml", ".yaml", ".yml", ".cfg", ".ini", ".sh"})
EXCLUDED_PARTS = frozenset({
    ".git", "__pycache__", "__MACOSX", "node_modules", ".pytest_cache",
    ".mypy_cache", ".ruff_cache",
    ".oif_backups",
})
EXCLUDED_PREFIXES = (".venv",)
REPORT_NAMES = frozenset({
    "p007_baseline_manifest.json",
    "p007_final_lock_report.json",
    "p007_campaign_report.json",
})
CANONICAL_BASELINE_ARTIFACTS = (
    "ontology_inventory.txt",
    "ontology_inventory.json",
    "global_module_catalog.json",
    "global_module_catalog.txt",
    "dependency_registry.py",
    "ontology/dependency_registry.py",
    "scientific_validation_report.json",
    "scientific_validation_report.txt",
)
INVARIANTS = {
    "consciousness_proven": False,
    "subjectivity_proven": False,
    "qualia_proven": False,
    "phenomenology_proven": False,
    "functional_conclusion_only": True,
    "phenomenology_undetermined": True,
}


def _run(*args: str) -> str:
    p = subprocess.run(
        list(args), cwd=str(ROOT), text=True,
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False,
    )
    if p.returncode != 0:
        raise RuntimeError("$ " + " ".join(args) + "\n" + (p.stdout or ""))
    return (p.stdout or "").strip()


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def _safe_relative(name: str) -> str | None:
    if not name:
        return None
    p = Path(name)
    if p.is_absolute() or ".." in p.parts:
        return None
    if p.name in REPORT_NAMES:
        return None
    for part in p.parts:
        if part in EXCLUDED_PARTS or part.startswith(EXCLUDED_PREFIXES):
            return None
    lowered = name.lower()
    if any(token in lowered for token in ("/.env", "secret", "credential", "private_key", "private-key")):
        return None
    return p.as_posix()


def _git_paths(args: list[str]) -> set[str]:
    raw = subprocess.run(
        ["git", *args, "-z"], cwd=str(ROOT), stdout=subprocess.PIPE,
        stderr=subprocess.PIPE, check=False,
    )
    if raw.returncode != 0:
        raise RuntimeError(raw.stderr.decode("utf-8", "replace"))
    result: set[str] = set()
    for item in raw.stdout.split(b"\0"):
        if not item:
            continue
        name = item.decode("utf-8", "surrogateescape")
        safe = _safe_relative(name)
        if safe:
            result.add(safe)
    return result


def functional_paths() -> list[str]:
    tracked = _git_paths(["ls-files"])
    modified = _git_paths(["diff", "--name-only"])
    staged = _git_paths(["diff", "--cached", "--name-only"])
    untracked = _git_paths(["ls-files", "--others", "--exclude-standard"])
    candidates = tracked | modified | staged | untracked
    selected: list[str] = []
    for name in candidates:
        parts = Path(name).parts
        if any(part in EXCLUDED_PARTS for part in parts):
            continue
        path = ROOT / name
        if path.is_file() and path.suffix.lower() in FUNCTIONAL_SUFFIXES:
            selected.append(name)
    return sorted(set(selected))


def canonical_artifact_paths() -> list[str]:
    missing = [name for name in CANONICAL_BASELINE_ARTIFACTS if not (ROOT / name).is_file()]
    if missing:
        raise RuntimeError("Missing canonical P007 baseline artifacts: " + ", ".join(missing))
    return sorted(CANONICAL_BASELINE_ARTIFACTS)


def _dependency_fingerprint() -> dict:
    freeze_result = pip_freeze(cwd=ROOT, timeout_seconds=60)
    freeze_stdout = (freeze_result.get("stdout") or b"").decode("utf-8", errors="replace")
    lines = sorted(line.strip() for line in freeze_stdout.splitlines() if line.strip())
    payload = "\n".join(lines) + ("\n" if lines else "")
    return {
        "python": platform.python_version(),
        "implementation": platform.python_implementation(),
        "pip_freeze_sha256": hashlib.sha256(payload.encode("utf-8")).hexdigest(),
        "package_count": len(lines),
        "semantics": "observed_environment_fingerprint_not_portability_claim",
    }


def _git_identity() -> dict:
    branch = _run("git", "branch", "--show-current")
    head = _run("git", "rev-parse", "HEAD")
    tags = _run("git", "tag", "--points-at", "HEAD").splitlines()
    return {"branch": branch, "head": head, "tags_at_head": sorted(x for x in tags if x)}


def _identity_payload(functional_files: dict, canonical_artifacts: dict, git: dict, dependencies: dict) -> dict:
    return {
        "schema": "oce.p007.baseline.v2",
        "git": git,
        "functional_files": functional_files,
        "canonical_baseline_artifacts": canonical_artifacts,
        "dependencies": dependencies,
        "invariants": INVARIANTS,
    }


def build_manifest() -> dict:
    files = {name: _sha256(ROOT / name) for name in functional_paths()}
    canonical_artifacts = {name: _sha256(ROOT / name) for name in canonical_artifact_paths()}
    payload = _identity_payload(files, canonical_artifacts, _git_identity(), _dependency_fingerprint())
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    identity = hashlib.sha256(canonical).hexdigest()
    return {
        **payload,
        "baseline_identity_sha256": identity,
        "captured_at_utc": datetime.now(timezone.utc).isoformat(),
        "functional_file_count": len(files),
        "canonical_artifact_count": len(canonical_artifacts),
        "functional_only": True,
        "phenomenology_undetermined": True,
    }


def _p162g6_relative_effect_path(filesystem_context, path: Path) -> Path:
    root_path = getattr(filesystem_context, "root_path", None)
    if root_path is None:
        raise RuntimeError("governed_filesystem_root_path_required")
    root = Path(root_path).expanduser().resolve()
    target = Path(path).expanduser()
    if not target.is_absolute():
        target = root / target
    target = target.resolve()
    try:
        return target.relative_to(root)
    except ValueError as exc:
        raise RuntimeError("governed_filesystem_path_outside_root") from exc


def _p162g6_missing_parent_chain(filesystem_context, path: Path) -> list[Path]:
    root_path = getattr(filesystem_context, "root_path", None)
    if root_path is None:
        raise RuntimeError("governed_filesystem_root_path_required")
    root = Path(root_path).expanduser().resolve()
    target = Path(path).expanduser()
    if not target.is_absolute():
        target = root / target
    target = target.resolve()
    try:
        parent_rel = target.parent.relative_to(root)
    except ValueError as exc:
        raise RuntimeError("governed_filesystem_path_outside_root") from exc
    chain = []
    current = root
    for part in parent_rel.parts:
        current = current / part
        if current.exists():
            if not current.is_dir():
                raise RuntimeError("manifest_parent_component_not_directory")
            continue
        chain.append(current)
    return chain


def write_manifest(path: Path, *, filesystem_context=None, evidence_decisions: Mapping[str, object] | None = None) -> dict:
    if filesystem_context is None:
        raise RuntimeError("governed_filesystem_context_required")
    if not isinstance(evidence_decisions, Mapping):
        raise RuntimeError("governed_evidence_decisions_required")
    manifest_write = evidence_decisions.get("manifest_write")
    if not isinstance(manifest_write, EvidenceEffectDecision):
        raise RuntimeError("manifest_write_evidence_decision_required")
    parent_chain = _p162g6_missing_parent_chain(filesystem_context, path)
    parent_decisions = evidence_decisions.get("parent_create", ())
    if not isinstance(parent_decisions, Sequence) or isinstance(parent_decisions, (str, bytes, bytearray)):
        raise RuntimeError("parent_create_evidence_decisions_sequence_required")
    if len(parent_decisions) != len(parent_chain):
        raise RuntimeError("parent_create_evidence_decision_cardinality_mismatch")
    if any(not isinstance(item, EvidenceEffectDecision) for item in parent_decisions):
        raise RuntimeError("parent_create_evidence_decision_required")
    manifest = build_manifest()
    payload = (json.dumps(manifest, indent=2, sort_keys=True, ensure_ascii=False) + "\n").encode("utf-8")
    filesystem_context.begin()
    bridge = GovernedEvidenceFilesystemBridge(GovernedEvidenceEffectPolicy(), filesystem_context)
    for parent, decision in zip(parent_chain, parent_decisions):
        result = bridge.execute_path(decision=decision, evidence_role="EVIDENCE_REPORT_EXPORT", slot="manifest_parent_create", operation_id="FS_CREATE_DIR", path=_p162g6_relative_effect_path(filesystem_context, parent))
        if result.get("status") != "EVIDENCE_EFFECT_CONFIRMED":
            raise RuntimeError("governed_manifest_parent_create_not_confirmed")
    result = bridge.execute_path(decision=manifest_write, evidence_role="EVIDENCE_REPORT_EXPORT", slot="manifest_write", operation_id="FS_WRITE_REPLACE_BYTES", path=_p162g6_relative_effect_path(filesystem_context, path), payload=payload)
    if result.get("status") != "EVIDENCE_EFFECT_CONFIRMED":
        raise RuntimeError("governed_manifest_write_not_confirmed")
    if any(filesystem_context.remaining().values()):
        raise RuntimeError("unused_filesystem_effect_authority")
    return manifest


def verify_manifest(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    required = {
        "schema", "git", "functional_files", "canonical_baseline_artifacts",
        "dependencies", "invariants", "baseline_identity_sha256", "functional_only",
        "phenomenology_undetermined",
    }
    missing = sorted(required - set(data))
    if missing:
        return {"ok": False, "reason": "missing_fields", "details": missing}
    if data["schema"] != "oce.p007.baseline.v2":
        return {"ok": False, "reason": "schema_mismatch"}
    if data["invariants"] != INVARIANTS:
        return {"ok": False, "reason": "invariant_mismatch"}
    if data["functional_only"] is not True or data["phenomenology_undetermined"] is not True:
        return {"ok": False, "reason": "epistemic_guard_mismatch"}

    current_git = _git_identity()
    if current_git != data["git"]:
        return {"ok": False, "reason": "git_identity_changed", "details": current_git}
    current_deps = _dependency_fingerprint()
    if current_deps != data["dependencies"]:
        return {"ok": False, "reason": "dependency_fingerprint_changed"}

    current_paths = functional_paths()
    expected_paths = sorted(data["functional_files"])
    if current_paths != expected_paths:
        return {"ok": False, "reason": "functional_path_set_changed",
                "added": sorted(set(current_paths) - set(expected_paths)),
                "removed": sorted(set(expected_paths) - set(current_paths))}
    mismatches = []
    for name, expected in sorted(data["functional_files"].items()):
        path_obj = ROOT / name
        if not path_obj.is_file():
            mismatches.append({"path": name, "status": "missing"})
        elif _sha256(path_obj) != expected:
            mismatches.append({"path": name, "status": "hash_mismatch"})
    if mismatches:
        return {"ok": False, "reason": "content_changed", "details": mismatches}

    expected_canonical_paths = sorted(data["canonical_baseline_artifacts"])
    try:
        current_canonical_paths = canonical_artifact_paths()
    except RuntimeError as exc:
        return {"ok": False, "reason": "canonical_artifact_missing", "details": str(exc)}
    if current_canonical_paths != expected_canonical_paths:
        return {"ok": False, "reason": "canonical_artifact_set_changed",
                "added": sorted(set(current_canonical_paths) - set(expected_canonical_paths)),
                "removed": sorted(set(expected_canonical_paths) - set(current_canonical_paths))}
    canonical_mismatches = []
    for name, expected in sorted(data["canonical_baseline_artifacts"].items()):
        path_obj = ROOT / name
        if not path_obj.is_file():
            canonical_mismatches.append({"path": name, "status": "missing"})
        elif _sha256(path_obj) != expected:
            canonical_mismatches.append({"path": name, "status": "hash_mismatch"})
    if canonical_mismatches:
        return {"ok": False, "reason": "canonical_artifact_changed", "details": canonical_mismatches}

    payload = _identity_payload(data["functional_files"], data["canonical_baseline_artifacts"], data["git"], data["dependencies"])
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    identity = hashlib.sha256(canonical).hexdigest()
    if identity != data["baseline_identity_sha256"]:
        return {"ok": False, "reason": "manifest_identity_corrupt"}
    return {"ok": True, "baseline_identity_sha256": identity,
            "functional_file_count": len(expected_paths),
            "canonical_artifact_count": len(expected_canonical_paths)}

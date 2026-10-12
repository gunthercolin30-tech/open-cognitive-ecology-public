from __future__ import annotations

import json
import tempfile
from pathlib import Path
import ontology.baseline_integrity as bi

REAL_GIT = bi._git_identity
REAL_DEPS = bi._dependency_fingerprint
REAL_PATHS = bi.functional_paths
REAL_CANONICAL_PATHS = bi.canonical_artifact_paths
REAL_SHA = bi._sha256

try:
    fixture_rel = "ontology/baseline_integrity.py"
    canonical_rel = "ontology_inventory.txt"
    fixture_hash = "a" * 64
    canonical_hash = "d" * 64
    fake_git = {"branch": "p007-fast-acceptance-fixture", "head": "b" * 40, "tags_at_head": ["p007-fixture"]}
    fake_deps = {"python": "fixture", "implementation": "fixture", "pip_freeze_sha256": "c" * 64,
                 "package_count": 1, "semantics": "observed_environment_fingerprint_not_portability_claim"}

    bi._git_identity = lambda: dict(fake_git)
    bi._dependency_fingerprint = lambda: dict(fake_deps)
    bi.functional_paths = lambda: [fixture_rel]
    bi.canonical_artifact_paths = lambda: [canonical_rel]
    bi._sha256 = lambda path: canonical_hash if path.name == "ontology_inventory.txt" else fixture_hash

    first = bi.build_manifest()
    second = bi.build_manifest()
    assert first["baseline_identity_sha256"] == second["baseline_identity_sha256"]
    assert first["schema"] == "oce.p007.baseline.v2"
    assert first["canonical_baseline_artifacts"] == {canonical_rel: canonical_hash}
    assert first["functional_only"] is True
    assert first["phenomenology_undetermined"] is True
    assert first["invariants"] == bi.INVARIANTS

    with tempfile.TemporaryDirectory() as td:
        path = Path(td) / "baseline.json"
        bi.write_manifest(path)
        verified = bi.verify_manifest(path)
        assert verified["ok"] is True, verified
        print("P007_CANONICAL_ARTIFACT_COVERAGE_OK")

        data = json.loads(path.read_text(encoding="utf-8"))
        data["invariants"]["consciousness_proven"] = True
        path.write_text(json.dumps(data), encoding="utf-8")
        degraded = bi.verify_manifest(path)
        assert degraded["ok"] is False and degraded["reason"] == "invariant_mismatch"

        bi.write_manifest(path)
        old_sha = bi._sha256
        bi._sha256 = lambda p: "e" * 64 if p.name == "ontology_inventory.txt" else old_sha(p)
        drift = bi.verify_manifest(path)
        assert drift["ok"] is False and drift["reason"] == "canonical_artifact_changed", drift
        print("P007_CANONICAL_ARTIFACT_DRIFT_DETECTED")
        bi._sha256 = old_sha

        bi.write_manifest(path)
        bi.canonical_artifact_paths = lambda: (_ for _ in ()).throw(RuntimeError("fixture missing"))
        removed = bi.verify_manifest(path)
        assert removed["ok"] is False and removed["reason"] == "canonical_artifact_missing", removed
        print("P007_CANONICAL_ARTIFACT_REMOVAL_DETECTED")
        bi.canonical_artifact_paths = lambda: [canonical_rel]

        bi.write_manifest(path)
        data = json.loads(path.read_text(encoding="utf-8"))
        data["baseline_identity_sha256"] = "0" * 64
        path.write_text(json.dumps(data), encoding="utf-8")
        corrupt = bi.verify_manifest(path)
        assert corrupt["ok"] is False and corrupt["reason"] == "manifest_identity_corrupt"
        print("P007_MANIFEST_CORRUPTION_DETECTED")
finally:
    bi._git_identity = REAL_GIT
    bi._dependency_fingerprint = REAL_DEPS
    bi.functional_paths = REAL_PATHS
    bi.canonical_artifact_paths = REAL_CANONICAL_PATHS
    bi._sha256 = REAL_SHA

print("P007_BASELINE_FUNCTIONAL_OK")
print("P007_BASELINE_DETERMINISM_OK")
print("P007_BASELINE_DEGRADATION_OK")
print("P007_BASELINE_NON_REGRESSION_OK")
print("P007_FAST_ACCEPTANCE_OK")

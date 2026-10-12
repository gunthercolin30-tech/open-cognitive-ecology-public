from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict


def sha_file(path: Path) -> str:
    """Return the SHA-256 digest of a file using bounded-memory streaming."""
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def valid_context(
    root: Path,
    proposal_id: str = "proposal-001",
    candidate_hash: str = "a" * 64,
) -> Dict[str, Any]:
    """Build a complete governed ACEE5 proposal fixture.

    ``root`` is retained in the public signature for compatibility with all
    existing ACEE5 tests and future local-artifact extensions.
    """
    _ = Path(root)
    now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    return {
        "proposal_id": proposal_id,
        "timestamp_utc": now,
        "candidate": {
            "module_name": "sample_candidate",
            "target_path": "ontology/sample_candidate.py",
            "content_sha256": candidate_hash,
        },
        "generation_evidence": {
            "proposal_only": True,
            "code_written": False,
            "code_installed": False,
        },
        "backup_evidence": {
            "target_path": "ontology/sample_candidate.py",
            "backup_path": "ontology/sample_candidate.py.bak",
            "verified": True,
            "sha256": "b" * 64,
        },
        "refiner_evidence": {
            "path": "refine_sample_candidate.py",
            "generated": True,
            "compilation_ready": True,
            "sha256": "c" * 64,
        },
        "test_evidence": {
            "generated": True,
            "tests": [
                "sample_candidate_fast_acceptance_suite.py",
                "sample_candidate_functional_test.py",
                "sample_candidate_degradation_test.py",
                "sample_candidate_non_regression_test.py",
            ],
        },
        "rollback_plan": {
            "available": True,
            "executor": "acee_rollback_engine",
            "artifacts": ["ontology/sample_candidate.py.bak"],
        },
        "inventory_plan": {
            "dependency_registry.py": True,
            "ontology_inventory.txt": True,
            "ontology_inventory.py": True,
            "ontology/ontology_inventory.py": True,
            "global_module_catalog.txt": True,
        },
        "validation_evidence": {
            "runner": "acee_validation_runner",
            "command": "python3 -m validation.main",
            "executed": True,
            "overall_success": True,
            "error_count": 0,
            "report_sha256": "d" * 64,
            "candidate_content_sha256": candidate_hash,
            "proposal_id": proposal_id,
            "timestamp_utc": now,
        },
        "constitutional_evidence": {
            "compliant": True,
            "non_closure_preserved": True,
            "functional_conclusion_only": True,
            "phenomenology_undetermined": True,
        },
    }

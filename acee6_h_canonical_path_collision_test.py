from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from tempfile import TemporaryDirectory

from acee6_b1_test_support import fixed_now, valid_acee5_decision
from ontology.acee_installation_executor import AceeInstallationExecutor, _sha


def rebind(decision):
    manifest = decision["installation_manifest"]
    manifest["manifest_hash"] = _sha(
        {key: value for key, value in manifest.items() if key != "manifest_hash"}
    )
    decision["result_hash"] = _sha(
        {key: value for key, value in decision.items() if key != "result_hash"}
    )


def main() -> None:
    with TemporaryDirectory() as tmp:
        root = Path(tmp)
        (root / "ontology").mkdir()
        executor = AceeInstallationExecutor(root=root, now_utc=fixed_now())

        aliases = (
            ("ontology/sample_candidate.py", "./ontology/sample_candidate.py"),
            ("ontology/sub/../sample_candidate.py", "ontology/sample_candidate.py"),
        )
        for target, backup in aliases:
            decision = deepcopy(valid_acee5_decision(root))
            manifest = decision["installation_manifest"]
            manifest["target_path"] = target
            manifest["backup_path"] = backup
            rebind(decision)
            result = executor.step(decision)
            assert result["admissible"] is False, (target, backup, result)
            assert "path_collision" in result["blocking_reasons"], result
            assert result["candidate_written"] is False, result
            assert result["persistence_performed"] is False, result

        # Traversal outside ROOT remains rejected rather than normalized inward.
        decision = deepcopy(valid_acee5_decision(root))
        decision["installation_manifest"]["target_path"] = "ontology/../../escape.py"
        rebind(decision)
        result = executor.step(decision)
        assert result["admissible"] is False, result
        assert any(
            reason.startswith("target_path_path_")
            for reason in result["blocking_reasons"]
        ), result

    print("ACEE6_H_CANONICAL_PATH_COLLISION_OK")


if __name__ == "__main__":
    main()

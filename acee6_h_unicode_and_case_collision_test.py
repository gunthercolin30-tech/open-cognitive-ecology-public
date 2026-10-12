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


def assert_collision(root: Path, target: str, backup: str) -> None:
    decision = deepcopy(valid_acee5_decision(root))
    manifest = decision["installation_manifest"]
    manifest["target_path"] = target
    manifest["backup_path"] = backup
    rebind(decision)
    result = AceeInstallationExecutor(root=root, now_utc=fixed_now()).step(decision)
    assert result["admissible"] is False, result
    assert "path_collision" in result["blocking_reasons"], result
    assert result["candidate_written"] is False, result
    assert result["persistence_performed"] is False, result


def main() -> None:
    with TemporaryDirectory() as tmp:
        root = Path(tmp)
        (root / "ontology").mkdir()

        # NFC versus NFD: visually identical path names must collide.
        assert_collision(
            root,
            "ontology/caf\u00e9.py",
            "ontology/cafe\u0301.py",
        )

        # Case-fold collision: relevant on both case-sensitive and
        # case-insensitive filesystems because admission is platform-neutral.
        assert_collision(
            root,
            "ontology/SampleCandidate.py",
            "ontology/samplecandidate.py",
        )

        # A genuinely distinct pair remains admissible.
        decision = deepcopy(valid_acee5_decision(root))
        manifest = decision["installation_manifest"]
        manifest["target_path"] = "ontology/caf\u00e9.py"
        manifest["backup_path"] = "ontology/caf\u00e9.py.bak"
        rebind(decision)
        result = AceeInstallationExecutor(root=root, now_utc=fixed_now()).step(decision)
        assert result["admissible"] is True, result
        assert result["normalized_plan"]["target_path"] == "ontology/caf\u00e9.py", result
        assert result["read_only"] is True, result
        assert result["persistence_performed"] is False, result

    print("ACEE6_H_UNICODE_AND_CASE_COLLISION_OK")


if __name__ == "__main__":
    main()

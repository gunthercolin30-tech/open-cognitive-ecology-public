from __future__ import annotations
import hashlib
import stat
from pathlib import Path
from tempfile import TemporaryDirectory

from acee6_b1_test_support import fixed_now
from acee6_e_test_support import seed
from acee6_f2_test_support import payload
from ontology.acee_installation_executor import AceeInstallationExecutor


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    with TemporaryDirectory() as tmp:
        root = Path(tmp)
        seed(root)
        target = root / "ontology" / "sample_candidate.py"
        original = b"ORIGINAL = 7\n"
        target.write_bytes(original)
        target.chmod(0o640)
        before_hash = sha(target)
        before_mode = stat.S_IMODE(target.stat().st_mode)

        inputs = payload(root)
        context = dict(inputs["admission_context"])
        context["requested_stage"] = "ACEE6-D2"
        context["fault_injection"] = {
            "enabled": True,
            "point": "write",
            "occurrence": 1,
            "execute_rollback": True,
        }
        inputs["admission_context"] = context

        result = AceeInstallationExecutor(root=root, now_utc=fixed_now()).step(
            inputs=inputs,
            persist=True,
        )
        assert result["transaction_state"] == "ROLLED_BACK", result
        assert result["target_rollback_action"] == "restore_from_backup_via_acee11", result
        assert result["rollback_verified"] is True, result
        assert result["target_restored"] is True, result
        assert result["rollback_result"].get("rollback_performed") is True, result
        assert target.is_file(), result
        assert sha(target) == before_hash, result
        assert target.read_bytes() == original, result
        assert stat.S_IMODE(target.stat().st_mode) == before_mode, result
        leftovers = [p for p in target.parent.iterdir() if ".tmp" in p.name or p.name.endswith(".rollback")]
        assert not leftovers, leftovers
    print("ACEE6_G2_PREEXISTING_TARGET_ROLLBACK_OK")


if __name__ == "__main__":
    main()

from __future__ import annotations
from pathlib import Path
from tempfile import TemporaryDirectory
from ontology.acee_installation_executor import AceeInstallationExecutor
from acee6_b1_test_support import fixed_now
from acee6_e_test_support import seed
from acee6_f2_test_support import payload


def run(point: str, stage: str):
    with TemporaryDirectory() as tmp:
        root = Path(tmp)
        seed(root)
        inputs = payload(root)
        context = dict(inputs["admission_context"])
        context["requested_stage"] = stage
        context["fault_injection"] = {
            "enabled": True,
            "point": point,
            "occurrence": 1,
            "execute_rollback": True,
        }
        inputs["admission_context"] = context
        result = AceeInstallationExecutor(root=root, now_utc=fixed_now()).step(
            inputs=inputs, persist=True
        )
        assert result["stage"] == "ACEE6-G2", result
        assert result["transaction_state"] == "ROLLED_BACK", result
        assert result["rollback_executed"] is True, result
        assert result["rollback_verified"] is True, result
        assert result["quarantined"] is False, result
        assert result["committed"] is False, result
        assert result["partial_success"] is False, result
        target = root / "ontology" / "sample_candidate.py"
        assert not target.exists(), (point, result)
        tx = root / "acee6_transactions" / result["transaction_id"]
        assert (tx / "rollback_report.json").is_file(), result
        journal = (tx / "journal.jsonl").read_text(encoding="utf-8")
        assert '"state":"ROLLING_BACK"' in journal.replace(" ", "")
        assert '"state":"ROLLED_BACK"' in journal.replace(" ", "")


def main():
    run("write", "ACEE6-D2")
    run("inventory", "ACEE6-E")
    print("ACEE6_G2_GOVERNED_ROLLBACK_FUNCTIONAL_OK")


if __name__ == "__main__":
    main()

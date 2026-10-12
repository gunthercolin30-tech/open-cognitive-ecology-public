from pathlib import Path
from tempfile import TemporaryDirectory

from acee6_b1_test_support import fixed_now
from acee6_f1_test_support import ORDER, payload, seed
from ontology.acee_installation_executor import AceeInstallationExecutor

for failing_role in ORDER:
    with TemporaryDirectory() as tmp:
        root = Path(tmp)
        seed(root)
        result = AceeInstallationExecutor(root=root, now_utc=fixed_now()).step(
            inputs=payload(root, failing_role=failing_role), persist=True
        )
        assert result["transaction_state"] == "ROLLED_BACK", (failing_role, result)
        runner = result["validation_runner_result"]
        names = [item["name"] for item in runner["command_results"]]
        expected = ORDER[: ORDER.index(failing_role) + 1]
        assert names == expected, (failing_role, names, expected)
        assert runner["failed_commands"] == [failing_role], runner
        assert result["rollback_executed"] is True
        assert result["global_validation_executed"] is False
        assert result["committed"] is False
print("ACEE6_F1_FAILURE_MATRIX_OK")

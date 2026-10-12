import sys
from pathlib import Path
from tempfile import TemporaryDirectory

from acee6_b1_test_support import fixed_now
from acee6_f1_test_support import payload, seed
from ontology.acee_installation_executor import AceeInstallationExecutor

with TemporaryDirectory() as tmp:
    root = Path(tmp)
    seed(root)
    value = payload(root)
    commands = value["admission_context"]["local_validation_commands"]
    commands[0]["argv"] = [sys.executable, "/tmp/outside_oce_f1.py"]
    result = AceeInstallationExecutor(root=root, now_utc=fixed_now()).step(
        inputs=value, persist=True
    )
    assert result["transaction_state"] == "ROLLED_BACK", result
    runner = result["validation_runner_result"]
    assert runner["blocked_commands"] == ["functional"], runner
    assert len(runner["command_results"]) == 1, runner
    assert runner["command_results"][0]["blocking_reason"] == "script_outside_root", runner
    assert result["rollback_executed"] is True
    assert result["global_validation_executed"] is False
    assert result["committed"] is False
print("ACEE6_F1_BLOCKED_COMMAND_OK")

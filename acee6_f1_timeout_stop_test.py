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
    timeout_script = root / "f1_functional.py"
    timeout_script.write_text("import time\ntime.sleep(5)\n", encoding="utf-8")
    commands[0]["argv"] = [sys.executable, str(timeout_script)]
    commands[0]["timeout_seconds"] = 0.1
    sentinel = root / "should_not_run.txt"
    next_script = root / "f1_fast_guard.py"
    next_script.write_text(
        "from pathlib import Path\n"
        f"Path({str(sentinel)!r}).write_text('ran', encoding='utf-8')\n",
        encoding="utf-8",
    )
    commands[1]["argv"] = [sys.executable, str(next_script)]
    result = AceeInstallationExecutor(root=root, now_utc=fixed_now()).step(
        inputs=value, persist=True
    )
    assert result["transaction_state"] == "ROLLED_BACK", result
    runner = result["validation_runner_result"]
    assert runner["timed_out_commands"] == ["functional"], runner
    assert len(runner["command_results"]) == 1, runner
    assert runner["command_results"][0]["name"] == "functional", runner
    assert runner["command_results"][0]["status"] == "timeout", runner
    assert not sentinel.exists()
    assert result["rollback_executed"] is True
    assert result["global_validation_executed"] is False
    assert result["committed"] is False
print("ACEE6_F1_TIMEOUT_STOP_OK")

from __future__ import annotations
import tempfile
from pathlib import Path
from ontology.acee_validation_runner import AceeValidationRunner

def main():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        good = root / "good.py"; good.write_text("print('ok')\n", encoding="utf-8")
        runner = AceeValidationRunner(root=root)
        ok = runner._run({"name":"good","argv":["python3", str(good)],"timeout_seconds":5}, False)
        assert ok["status"] == "passed" and ok["stdout"].strip() == "ok", ok
        blocked = runner._run({"name":"bad","argv":["sh","-c","echo bad"],"timeout_seconds":5}, False)
        assert blocked["status"] == "blocked" and blocked["blocking_reason"] == "python_command_required", blocked
    print("ACEE6_H_COMMAND_TIMEOUT_NON_REGRESSION_OK")
if __name__ == "__main__": main()

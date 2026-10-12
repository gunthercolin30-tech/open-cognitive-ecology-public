from __future__ import annotations
import tempfile
from pathlib import Path
from ontology.acee_validation_runner import AceeValidationRunner

def main():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        script = root / "ignore_term.py"
        script.write_text("import signal,time\nsignal.signal(signal.SIGTERM, lambda *_: None)\nwhile True: time.sleep(0.1)\n", encoding="utf-8")
        result = AceeValidationRunner(root=root)._run({"name":"kill","argv":["python3", str(script)],"timeout_seconds":1.0}, False)
        assert result["status"] == "timeout", result
        assert result["process_group_terminated"] is True, result
        assert result["returncode"] is not None, result
        source = Path(__import__("ontology.acee_validation_runner", fromlist=["x"]).__file__).read_text(encoding="utf-8")
        assert "signal.SIGKILL" in source and "forced_kill = True" in source
    print("ACEE6_H_SIGTERM_SIGKILL_ESCALATION_OK")
if __name__ == "__main__": main()

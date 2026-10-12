from __future__ import annotations
import tempfile
from pathlib import Path
from ontology.acee_validation_runner import AceeValidationRunner

def main():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        script = root / "safe.py"
        marker = root / "escaped"
        script.write_text("import sys\nprint(sys.argv[1:])\n", encoding="utf-8")
        runner = AceeValidationRunner(root=root)
        result = runner._run({"name":"argv","argv":["python3", str(script), ";", "touch", str(marker)], "timeout_seconds":5}, False)
        assert result["status"] == "passed", result
        assert not marker.exists(), result
        assert result.get("process_group_terminated") is False
    print("ACEE6_H_SHELL_AND_ARGV_SECURITY_OK")
if __name__ == "__main__": main()

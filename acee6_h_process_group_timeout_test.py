from __future__ import annotations
import os, tempfile, time
from pathlib import Path
from ontology.acee_validation_runner import AceeValidationRunner

def main():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        marker = root / "late_marker"
        script = root / "parent.py"
        script.write_text("import subprocess,sys,time\nsubprocess.Popen([sys.executable,'-c',\"import time,pathlib; time.sleep(2); pathlib.Path(r'%s').write_text('late')\"])\ntime.sleep(10)\n" % marker, encoding="utf-8")
        result = AceeValidationRunner(root=root)._run({"name":"timeout","argv":["python3", str(script)],"timeout_seconds":0.5}, False)
        assert result["status"] == "timeout", result
        assert result["process_group_terminated"] is True, result
        time.sleep(2.5)
        assert not marker.exists(), "descendant survived timeout"
    print("ACEE6_H_PROCESS_GROUP_TIMEOUT_OK")
if __name__ == "__main__": main()

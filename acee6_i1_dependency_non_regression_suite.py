#!/usr/bin/env python3
from __future__ import annotations
import subprocess,sys
from pathlib import Path
ROOT=Path.home()/"open-cognitive-ecology"
SUITES=["acee6_g1_second_crown_suite.py","acee6_g2_extended_rollback_suite.py","acee6_h_path_security_suite.py","acee6_h_command_timeout_suite.py","acee6_h_transactional_concurrency_suite.py"]
for name in SUITES:
 p=ROOT/name; assert p.is_file(),p
 c=subprocess.run([sys.executable,str(p)],cwd=str(ROOT),check=False)
 if c.returncode: raise SystemExit(c.returncode)
print("ACEE6_I1_DEPENDENCY_NON_REGRESSION_OK")

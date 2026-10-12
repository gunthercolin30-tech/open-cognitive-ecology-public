#!/usr/bin/env python3
from __future__ import annotations
import subprocess,sys
from pathlib import Path
ROOT=Path.home()/"open-cognitive-ecology"
for name in ["acee6_i1_suite_integration_maintenance_test.py","acee6_i1_dependency_non_regression_suite.py"]:
 c=subprocess.run([sys.executable,str(ROOT/name)],cwd=str(ROOT),check=False)
 if c.returncode: raise SystemExit(c.returncode)
print("ACEE6_I1_INTEGRATION_MAINTENANCE_SUITE_OK")

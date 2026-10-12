from __future__ import annotations
import json
from pathlib import Path

from oif.interface import validate_manifest

ROOT = Path.home() / "open-cognitive-ecology"
base = json.loads((ROOT / "oif" / "schemas" / "examples" / "minimal_interface.json").read_text(encoding="utf-8"))
base["interface"]["metadata"]["python"] = "os.system('false')"
report = validate_manifest(base)
assert not report.valid
assert any(error.code == "arbitrary_code_field" for error in report.errors)
assert all("os.system" not in error.message and "os.system" not in error.suggestion for error in report.errors)
print("OIF2D_SECURITY_OK")

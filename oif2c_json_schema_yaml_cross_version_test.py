from __future__ import annotations
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path.home() / "open-cognitive-ecology"
interpreters = [Path(sys.executable), ROOT / ".venv-oif" / "bin" / "python"]
for interpreter in interpreters:
    assert interpreter.is_file(), interpreter

snippet = (
    "import json;"
    "from oif2b_test_support import build_spec;"
    "from oif.interface.serialization import specification_to_yaml,load_yaml_mapping,mapping_to_canonical_json;"
    "s=build_spec();"
    "print(json.dumps({'json':mapping_to_canonical_json(load_yaml_mapping(specification_to_yaml(s))),'sha':s.sha256()},sort_keys=True))"
)

results = []
for interpreter in interpreters:
    run = subprocess.run(
        [str(interpreter), "-c", snippet], cwd=str(ROOT),
        text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=180,
    )
    if run.returncode:
        raise AssertionError("%s failed:\n%s" % (interpreter, run.stderr))
    results.append(json.loads(run.stdout.strip().splitlines()[-1]))
assert results[0] == results[1]
print("OIF2C_CROSS_VERSION_OK", results[0]["sha"])

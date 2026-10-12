from __future__ import annotations
import hashlib, subprocess, sys
from pathlib import Path
from oif.interface.serialization import load_json_mapping, load_yaml_mapping, mapping_to_canonical_json
from oif.schemas import SCHEMA_ROOT

ROOT = Path.home() / "open-cognitive-ecology"
for stem in ("minimal_interface", "complete_interface"):
    j = mapping_to_canonical_json(load_json_mapping(SCHEMA_ROOT / "examples" / (stem + ".json")))
    y = mapping_to_canonical_json(load_yaml_mapping(SCHEMA_ROOT / "examples" / (stem + ".yaml")))
    assert j == y
    assert hashlib.sha256(j.encode("utf-8")).hexdigest() == hashlib.sha256(y.encode("utf-8")).hexdigest()

snippet = "from oif.interface.serialization import load_json_mapping,load_yaml_mapping,mapping_to_canonical_json;from oif.schemas import SCHEMA_ROOT;import hashlib;[(lambda j,y:(j==y) or (_ for _ in ()).throw(AssertionError()))(mapping_to_canonical_json(load_json_mapping(SCHEMA_ROOT/'examples'/(s+'.json'))),mapping_to_canonical_json(load_yaml_mapping(SCHEMA_ROOT/'examples'/(s+'.yaml')))) for s in ('minimal_interface','complete_interface')];print('OK')"
outputs = []
for interpreter in (Path(sys.executable), ROOT / ".venv-oif" / "bin" / "python"):
    assert interpreter.is_file(), interpreter
    run = subprocess.run([str(interpreter), "-c", snippet], cwd=str(ROOT), text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=300)
    if run.returncode:
        raise AssertionError("%s failed:\n%s" % (interpreter, run.stderr))
    outputs.append(run.stdout.strip())
assert outputs[0] == outputs[1] == "OK"
print("OIF2C_CROSS_FORMAT_EQUIVALENCE_OK")

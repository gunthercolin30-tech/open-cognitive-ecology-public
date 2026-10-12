import json
import tempfile
from pathlib import Path
from aw14_context import build_context
from ontology.ecological_certifier import EcologicalCertifier

with tempfile.TemporaryDirectory() as directory:
    certifier = EcologicalCertifier(Path(directory))
    result = certifier.step(inputs=build_context(), persist=True)
    path = Path(result["history_path"])
    raw = path.read_text(encoding="utf-8")
    path.write_text(raw[:-4] + "xxxx", encoding="utf-8")
    failed = False
    try:
        json.loads(path.read_text(encoding="utf-8").splitlines()[0])
    except json.JSONDecodeError:
        failed = True
    assert failed
print("AW14_CORRUPTION_OK")

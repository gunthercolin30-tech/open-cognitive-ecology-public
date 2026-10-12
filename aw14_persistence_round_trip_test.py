import json
import tempfile
from pathlib import Path
from aw14_context import build_context
from ontology.ecological_certifier import EcologicalCertifier

with tempfile.TemporaryDirectory() as directory:
    certifier = EcologicalCertifier(Path(directory))
    result = certifier.step(inputs=build_context(), persist=True)
    latest = json.loads(Path(result["latest_path"]).read_text(encoding="utf-8"))
    history = json.loads(Path(result["history_path"]).read_text(encoding="utf-8").splitlines()[0])
    assert latest["certification_hash"] == result["certification_hash"]
    assert history["certification_hash"] == result["certification_hash"]
print("AW14_PERSISTENCE_ROUND_TRIP_OK")

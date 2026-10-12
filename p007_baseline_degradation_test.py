from pathlib import Path
import json
import tempfile
from ontology.baseline_integrity import write_manifest, verify_manifest

with tempfile.TemporaryDirectory() as td:
    path = Path(td) / "baseline.json"
    write_manifest(path)

    data = json.loads(path.read_text(encoding="utf-8"))
    data["invariants"]["consciousness_proven"] = True
    path.write_text(json.dumps(data), encoding="utf-8")
    result = verify_manifest(path)
    assert result["ok"] is False
    assert result["reason"] == "invariant_mismatch"

    write_manifest(path)
    data = json.loads(path.read_text(encoding="utf-8"))
    data["baseline_identity_sha256"] = "0" * 64
    path.write_text(json.dumps(data), encoding="utf-8")
    result = verify_manifest(path)
    assert result["ok"] is False
    assert result["reason"] == "manifest_identity_corrupt"

print("P007_BASELINE_DEGRADATION_OK")

from pathlib import Path
import tempfile
from ontology.baseline_integrity import write_manifest, verify_manifest

with tempfile.TemporaryDirectory() as td:
    path = Path(td) / "baseline.json"
    manifest = write_manifest(path)
    result = verify_manifest(path)
    assert result["ok"] is True, result
    assert result["baseline_identity_sha256"] == manifest["baseline_identity_sha256"]
    assert manifest["functional_only"] is True
    assert manifest["phenomenology_undetermined"] is True
print("P007_BASELINE_FUNCTIONAL_OK")

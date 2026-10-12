import tempfile
from pathlib import Path
from validation.p001_objective_director import audit

with tempfile.TemporaryDirectory() as td:
    root = Path(td)
    (root / "ontology").mkdir()
    result = audit(root)
    assert result["decision"] == "UNKNOWN"
    assert result["all_stages_representable"] is False
    assert result["unknown"]
print("P001_DEGRADATION_OK")

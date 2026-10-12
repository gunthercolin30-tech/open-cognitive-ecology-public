\
import tempfile
from pathlib import Path
from acee8_fast_acceptance_suite import context
from ontology.acee_impact_evaluator import AceeImpactEvaluator
with tempfile.TemporaryDirectory() as td:
    root = Path(td); engine = AceeImpactEvaluator(root=root)
    latest, history, lock = engine._paths(); history.parent.mkdir(parents=True, exist_ok=True)
    history.write_text("{broken-json\n", encoding="utf-8")
    r = engine.step(inputs=context(), persist=False)
    assert r["history_corrupted"] is True
    assert r["impact_status"] == "ACEE_IMPACT_EVALUATION_DEGRADED"
    assert "history_corrupted" in r["blocking_reasons"]
print("ACEE8_CORRUPTION_OK")

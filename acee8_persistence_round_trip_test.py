\
import json, tempfile
from pathlib import Path
from acee8_fast_acceptance_suite import context
from ontology.acee_impact_evaluator import AceeImpactEvaluator
with tempfile.TemporaryDirectory() as td:
    root = Path(td)
    engine = AceeImpactEvaluator(root=root)
    first = engine.step(inputs=context(), persist=True)
    second_context = context(); second_context["evaluation_id"] = "impact-002"
    second = engine.step(inputs=second_context, persist=True)
    latest = json.loads(Path(second["latest_path"]).read_text(encoding="utf-8"))
    lines = [json.loads(x) for x in Path(second["history_path"]).read_text(encoding="utf-8").splitlines() if x.strip()]
    assert first["persisted"] is True and second["persisted"] is True
    assert len(lines) == 2 and latest["impact_hash"] == second["impact_hash"]
    assert second["previous_impact_hash"] == first["impact_hash"]
print("ACEE8_PERSISTENCE_ROUND_TRIP_OK")

from pathlib import Path
from tempfile import TemporaryDirectory
import json
from ontology.acee_lineage_manager import AceeLineageManager

with TemporaryDirectory() as tmp:
    root = Path(tmp)
    manager = AceeLineageManager(root=root)
    manager.step(inputs={"operation":"register_root","transaction_id":"T0","lineage_id":"L","architecture_id":"A0"}, persist=True)
    for generation, architecture, parent in ((1,"A1","A0"),(2,"A2","A1")):
        manager.step(inputs={"operation":"register_candidate","transaction_id":f"TC{generation}","lineage_id":"L","generation_id":generation,"architecture_id":architecture,"parent_id":parent,"mutation_id":f"M{generation}","fitness_delta":0.1}, persist=True)
        manager.step(inputs={"operation":"apply_selection","transaction_id":f"TS{generation}","lineage_id":"L","generation_id":generation,"selection_decision":{"selection_id":f"S{generation}","selection_decision_ready":True,"decision":"accept"}}, persist=True)
    state_path = root / "acee_runtime" / "ACEE13_acee_lineage_manager" / "lineages.json"
    state = json.loads(state_path.read_text())
    lineage = state["lineages"]["L"]
    active = [g for g in lineage["generations"].values() if g["status"] == "active"]
    assert lineage["active_generation_id"] == 2
    assert len(active) == 1 and active[0]["generation_id"] == 2
print("ACEE13_SINGLE_ACTIVE_HEAD_OK")

from pathlib import Path
from tempfile import TemporaryDirectory
from ontology.acee_architecture_genealogy import AceeArchitectureGenealogy

def base(aid="ARCH-A", parent=None, generation=0, rollback="not_rolled_back"):
    return {
        "architecture_id": aid,
        "architecture": {"architecture_id": aid, "modules": ["m1", "m2"], "parameters": {"x": 1}},
        "parent_architecture_id": parent,
        "generation_id": generation,
        "mutation_id": "MUT-1" if parent else None,
        "selection_decision": {"selection_id": "SEL-1", "decision": "accept"},
        "causal_analysis": {"analysis_id": "CAUSAL-1"},
        "impact_evaluation": {"evaluation_id": "IMPACT-1"},
        "rollback_status": rollback,
        "continuity_evidence": {"lineage_integrity": 0.91},
        "diversity_evidence": {"lineage_diversity_score": 0.82},
        "inheritance_evidence": {"inheritance_fidelity": 0.93},
        "timestamp_utc": "2026-07-13T20:00:00Z",
    }

import json
with TemporaryDirectory() as tmp:
    g=AceeArchitectureGenealogy(root=Path(tmp)); g.step(base(),persist=True)
    g.step(base("ARCH-B","ARCH-A",1),persist=True); g.step(base("ARCH-C","ARCH-A",1),persist=True)
    graph=json.loads((Path(tmp)/"acee_runtime/ACEE12_acee_architecture_genealogy/architecture_genealogy_graph.json").read_text())
    assert graph["children"]["ARCH-A"]==["ARCH-B","ARCH-C"]
print("ACEE12_BRANCHING_OK")

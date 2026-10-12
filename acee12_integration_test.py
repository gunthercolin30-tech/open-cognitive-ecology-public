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

with TemporaryDirectory() as tmp:
    selection={"selection_id":"SEL-10","decision":"accept","selection_decision_ready":True}
    causal={"analysis_id":"CAUSAL-9","ready_for_selection":True}
    impact={"evaluation_id":"IMPACT-8","comparison_valid":True}
    d=base(); d["selection_decision"]=selection; d["causal_analysis"]=causal; d["impact_evaluation"]=impact
    r=AceeArchitectureGenealogy(root=Path(tmp)).step(d,persist=True)
    assert r["selection_decision_id"]=="SEL-10" and r["causal_analysis_id"]=="CAUSAL-9" and r["impact_evaluation_id"]=="IMPACT-8"
    assert not r["selection_executed_by_genealogy"] and not r["rollback_executed_by_genealogy"]
print("ACEE12_ACEE10_ACEE11_INTEGRATION_OK")

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
    r = AceeArchitectureGenealogy(root=Path(tmp)).step(base(), persist=False)
    assert r["selection_executed_by_genealogy"] is False
    assert r["mutation_executed_by_genealogy"] is False
    assert r["rollback_executed_by_genealogy"] is False
    assert r["lineage_management_executed"] is False
    assert r["best_architecture_selection_executed"] is False
    assert r["dashboard_generated"] is False
    assert r["functional_conclusion_only"] is True
    assert r["phenomenology_undetermined"] is True
    for k in ("consciousness_proven","subjectivity_proven","qualia_proven","phenomenology_proven","collective_consciousness_proven","collective_subjectivity_proven","collective_qualia_proven","collective_phenomenology_proven"):
        assert r[k] is False
print("ACEE12_NON_REGRESSION_OK")

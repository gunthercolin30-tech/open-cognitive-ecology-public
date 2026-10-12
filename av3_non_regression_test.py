from copy import deepcopy
from ontology.specialization_engine import SpecializationEngine
CONTEXT = {"maturation_result": {"maturation_complete": True, "maturation_status": "FUNCTIONAL_MATURATION_COMPLETE"}, "observations": [{"timestamp_utc": f"2026-10-{i:02d}T00:00:00Z", "functional_profile": {"reasoning": v, "memory": .12, "governance": .06, "exploration": .02}, "diversity": .35, "resource_cost": .4, "reversibility": .74, "openness": .82, "data_quality": .96} for i, v in enumerate([.68,.72,.76,.80,.84,.88], 1)]}
def main():
    engine = SpecializationEngine()
    first = engine.step(inputs=deepcopy(CONTEXT), persist=False)
    second = engine.step(inputs=deepcopy(CONTEXT), persist=False)
    for key in ["specialization_hash", "specialization_strength", "closure_pressure", "specialization_profile", "condition_results"]:
        assert first[key] == second[key]
    changed_context = deepcopy(CONTEXT)
    changed_context["observations"][4]["resource_cost"] = .55
    changed = engine.step(inputs=changed_context, persist=False)
    assert changed["specialization_hash"] != first["specialization_hash"]
    for result in [first, second, changed]:
        assert result["functional_conclusion_only"] is True and result["phenomenology_undetermined"] is True
        assert all(result[k] is False for k in ["consciousness_proven", "qualia_proven", "subjectivity_proven", "phenomenology_proven"])
    print("AV3_NON_REGRESSION_AND_DETERMINISM_OK")
if __name__ == "__main__": main()

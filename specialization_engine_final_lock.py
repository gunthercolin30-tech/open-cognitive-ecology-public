from ontology.specialization_engine import SpecializationEngine
READY_OR_SYNTHETIC_CONTEXT = {"maturation_result": {"maturation_complete": True, "maturation_status": "FUNCTIONAL_MATURATION_COMPLETE"}, "observations": [{"timestamp_utc": f"2026-08-{i:02d}T00:00:00Z", "functional_profile": {"reasoning": v, "memory": .12, "governance": .06, "exploration": .03}, "diversity": .36, "resource_cost": .40, "reversibility": .75, "openness": .84, "data_quality": .98, "synthetic": True} for i, v in enumerate([.68,.72,.76,.80,.84,.88], 1)]}
def main():
    result = SpecializationEngine().step(inputs=READY_OR_SYNTHETIC_CONTEXT, persist=False)
    assert result["primitive"] == "SPECIALIZATION_ENGINE" and result["step"] == "AV3" and result["public_schema_version"] == "1.0"
    assert result["specialization_status"] in {"FUNCTIONAL_SPECIALIZATION_STABLE", "FUNCTIONAL_SPECIALIZATION_STRONG"}
    assert len(result["specialization_hash"]) == 64
    assert result["functional_conclusion_only"] is True and result["phenomenology_undetermined"] is True
    assert all(result[k] is False for k in ["consciousness_proven", "qualia_proven", "subjectivity_proven", "phenomenology_proven"])
    print("AV3_FINAL_LOCK_OK")
if __name__ == "__main__": main()

from ontology.specialization_engine import SpecializationEngine
MAT = {"maturation_complete": True, "maturation_status": "FUNCTIONAL_MATURATION_COMPLETE"}
def obs(i, profile, diversity=.7, cost=.2, reversibility=.8, openness=.9, quality=.95):
    return {"timestamp_utc": f"2026-09-{i:02d}T00:00:00Z", "functional_profile": profile, "diversity": diversity, "resource_cost": cost, "reversibility": reversibility, "openness": openness, "data_quality": quality}
def main():
    engine = SpecializationEngine()
    assert engine.step(inputs={}, persist=False)["specialization_status"] == "FUNCTIONAL_SPECIALIZATION_UNDETERMINED"
    balanced = [obs(i, {"a":.25,"b":.25,"c":.25,"d":.25}) for i in range(1,7)]
    assert engine.step(inputs={"maturation_result": MAT, "observations": balanced}, persist=False)["specialization_status"] == "FUNCTIONAL_SPECIALIZATION_ABSENT"
    assert engine.step(inputs={"observations": balanced}, persist=False)["specialization_status"] == "FUNCTIONAL_SPECIALIZATION_NOT_ESTABLISHED"
    transient = [obs(1,{"a":.9,"b":.1}), obs(2,{"b":.9,"a":.1}), obs(3,{"c":.9,"a":.1}), obs(4,{"d":.9,"a":.1}), obs(5,{"a":.9,"b":.1})]
    transient_result = engine.step(inputs={"maturation_result": MAT, "observations": transient}, persist=False)
    assert transient_result["specialization_status"] not in {"FUNCTIONAL_SPECIALIZATION_STABLE", "FUNCTIONAL_SPECIALIZATION_STRONG"}
    closure = [obs(i,{"a":.95,"b":.03,"c":.02}, diversity=.10, cost=.90, reversibility=.10, openness=.10) for i in range(1,7)]
    closure_result = engine.step(inputs={"maturation_result": MAT, "observations": closure}, persist=False)
    assert closure_result["specialization_status"] == "FUNCTIONAL_SPECIALIZATION_CLOSURE_RISK" and closure_result["closure_pressure"] >= .65
    low_quality = [obs(i,{"a":.9,"b":.1}, quality=.1) for i in range(1,7)]
    assert engine.step(inputs={"maturation_result": MAT, "observations": low_quality}, persist=False)["specialization_status"] == "FUNCTIONAL_SPECIALIZATION_UNDETERMINED"
    invalid = [obs(3,{"a":.9,"b":.1}), obs(1,{"a":.9,"b":.1}), obs(2,{"a":.9,"b":.1}), obs(4,{"a":.9,"b":.1}), obs(5,{"a":.9,"b":.1})]
    assert engine.step(inputs={"maturation_result": MAT, "observations": invalid}, persist=False)["specialization_status"] == "FUNCTIONAL_SPECIALIZATION_UNDETERMINED"
    print("AV3_DEGRADATION_OK")
if __name__ == "__main__": main()

from pathlib import Path
import json
import py_compile
import tempfile
from ontology.specialization_engine import SpecializationEngine
ROOT = Path.home() / "open-cognitive-ecology"
MAT = {"maturation_complete": True, "maturation_status": "FUNCTIONAL_MATURATION_COMPLETE"}
def obs(day, a, b, c, d):
    return {"timestamp_utc": f"2026-07-{day:02d}T00:00:00Z", "functional_profile": {"reasoning": a, "memory": b, "governance": c, "exploration": d}, "diversity": 0.34, "resource_cost": 0.42, "reversibility": 0.72, "openness": 0.82, "data_quality": 0.97, "synthetic": True}
def assert_guards(r):
    assert r["functional_conclusion_only"] is True and r["phenomenology_undetermined"] is True
    assert all(r[k] is False for k in ["consciousness_proven", "qualia_proven", "subjectivity_proven", "phenomenology_proven"])
def main():
    for p in [ROOT / "ontology/specialization_engine.py", ROOT / "av3_fast_acceptance_suite.py", ROOT / "specialization_engine_final_lock.py", ROOT / "av3_degradation_test.py", ROOT / "av3_non_regression_test.py"]:
        py_compile.compile(str(p), cfile=f"/private/tmp/{p.name}.pyc", doraise=True)
    context = {"maturation_result": MAT, "observations": [obs(1,.65,.20,.10,.05), obs(2,.72,.16,.08,.04), obs(3,.78,.13,.06,.03), obs(4,.82,.10,.05,.03), obs(5,.86,.08,.04,.02), obs(6,.88,.07,.03,.02)]}
    result = SpecializationEngine().step(inputs=context, persist=False)
    assert result["step"] == "AV3"
    assert result["specialization_status"] in {"FUNCTIONAL_SPECIALIZATION_STABLE", "FUNCTIONAL_SPECIALIZATION_STRONG"}
    assert result["specialization_strength"] >= 0.55 and result["persistence_score"] >= 0.70
    assert len(result["specialization_hash"]) == 64
    assert_guards(result)
    assert SpecializationEngine().step(inputs=context, persist=False)["specialization_hash"] == result["specialization_hash"]
    with tempfile.TemporaryDirectory(prefix="oce_av3_") as tmp:
        old = SpecializationEngine.output_dir
        SpecializationEngine.output_dir = Path(tmp)
        try:
            persisted = SpecializationEngine().step(inputs=context, persist=True)
            assert persisted["persisted"] is True and Path(persisted["output_path"]).is_file()
            assert json.loads(Path(persisted["output_path"]).read_text())["specialization_hash"] == result["specialization_hash"]
        finally:
            SpecializationEngine.output_dir = old
    print("AV3_FAST_ACCEPTANCE_OK")
if __name__ == "__main__": main()

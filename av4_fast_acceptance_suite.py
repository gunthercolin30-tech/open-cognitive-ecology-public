from pathlib import Path
import json
import py_compile
import tempfile
from ontology.bifurcation_detector import BifurcationDetector
ROOT = Path.home() / "open-cognitive-ecology"
def obs(day,a,b,c): return {"timestamp_utc":f"2026-11-{day:02d}T00:00:00Z","state_vector":{"stability":a,"integration":b,"openness":c},"data_quality":.98,"synthetic":True}
def guards(r):
    assert r["functional_conclusion_only"] is True and r["phenomenology_undetermined"] is True
    assert all(r[k] is False for k in ["consciousness_proven","qualia_proven","subjectivity_proven","phenomenology_proven"])
def multi_obs(day,a,b,c): return {"timestamp_utc":f"2026-12-{day:02d}T00:00:00Z","state_vector":{"stability":a,"integration":a,"continuity":a,"specialization":b,"diversity":c,"openness":c},"data_quality":.99}
def main():
    for p in [ROOT/"ontology/bifurcation_detector.py",ROOT/"av4_fast_acceptance_suite.py",ROOT/"bifurcation_detector_final_lock.py",ROOT/"av4_degradation_test.py",ROOT/"av4_non_regression_test.py"]:
        py_compile.compile(str(p),cfile=f"/private/tmp/{p.name}.pyc",doraise=True)
    context={"observations":[obs(1,.78,.76,.82),obs(2,.79,.77,.81),obs(3,.77,.78,.82),obs(4,.24,.30,.35),obs(5,.23,.28,.33),obs(6,.25,.29,.34),obs(7,.24,.30,.32)]}
    r=BifurcationDetector().step(inputs=context,persist=False)
    assert r["step"]=="AV4" and r["bifurcation_status"] in {"FUNCTIONAL_BIFURCATION_DETECTED","FUNCTIONAL_STRUCTURAL_BREAK_DETECTED"}
    assert r["structural_break_score"]>=.42 and len(r["bifurcation_hash"])==64; guards(r)
    fluct={"observations":[obs(1,.80,.80,.80),obs(2,.79,.79,.79),obs(3,.40,.40,.40),obs(4,.78,.78,.78),obs(5,.81,.81,.81)]}
    fr=BifurcationDetector().step(inputs=fluct,persist=False)
    assert fr["bifurcation_status"] in {"FUNCTIONAL_FLUCTUATION_DETECTED","NO_DEVELOPMENTAL_TRANSITION"} and fr["bifurcation_detected"] is False
    multi={"observations":[multi_obs(1,.82,.25,.82),multi_obs(2,.81,.26,.81),multi_obs(3,.52,.78,.42),multi_obs(4,.51,.80,.40),multi_obs(5,.83,.28,.84),multi_obs(6,.84,.27,.85)]}
    mr=BifurcationDetector().step(inputs=multi,persist=False)
    assert mr["bifurcation_count"]>=2 and mr["multiple_bifurcations_detected"] is True and mr["bifurcation_status"]=="FUNCTIONAL_MULTIPLE_BIFURCATIONS_DETECTED"
    with tempfile.TemporaryDirectory(prefix="oce_av4_") as tmp:
        old=BifurcationDetector.output_dir; BifurcationDetector.output_dir=Path(tmp)
        try:
            p=BifurcationDetector().step(inputs=context,persist=True)
            assert p["persisted"] is True and Path(p["output_path"]).is_file()
            assert json.loads(Path(p["output_path"]).read_text())["bifurcation_hash"]==r["bifurcation_hash"]
        finally: BifurcationDetector.output_dir=old
    print("AV4_FAST_ACCEPTANCE_OK")
if __name__=="__main__": main()

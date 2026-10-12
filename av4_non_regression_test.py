from copy import deepcopy
from ontology.bifurcation_detector import BifurcationDetector
CONTEXT={"observations":[{"timestamp_utc":f"2027-02-{i:02d}T00:00:00Z","state_vector":{"stability":a,"integration":b,"openness":c},"data_quality":.97} for i,(a,b,c) in enumerate([(.8,.78,.82),(.79,.77,.81),(.81,.79,.83),(.23,.29,.32),(.24,.28,.31),(.22,.30,.33),(.25,.29,.32)],1)]}
def main():
    e=BifurcationDetector(); a=e.step(inputs=deepcopy(CONTEXT),persist=False); b=e.step(inputs=deepcopy(CONTEXT),persist=False)
    for k in ["bifurcation_hash","bifurcation_status","bifurcation_type","pre_regime","post_regime","structural_break_score","condition_results"]: assert a[k]==b[k]
    changed=deepcopy(CONTEXT); changed["observations"][4]["state_vector"]["openness"]=.48
    c=e.step(inputs=changed,persist=False); assert c["bifurcation_hash"]!=a["bifurcation_hash"]
    for r in [a,b,c]:
        assert r["functional_conclusion_only"] is True and r["phenomenology_undetermined"] is True
        assert all(r[k] is False for k in ["consciousness_proven","qualia_proven","subjectivity_proven","phenomenology_proven"])
    print("AV4_NON_REGRESSION_AND_DETERMINISM_OK")
if __name__=="__main__": main()

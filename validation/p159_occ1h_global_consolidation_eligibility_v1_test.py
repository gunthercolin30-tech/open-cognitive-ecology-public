import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
P=ROOT/"validation_artifacts/p159/occ1h/global_consolidation_eligibility_v1.json"
def d(): return json.loads(P.read_text(encoding="utf-8"))
def test_global_eligibility():
    x=d(); assert x["status"]=="ELIGIBLE_FOR_GOVERNED_OCC1H_CLOSURE"
    assert x["h1_h10_covered"] and x["scenarios_accounted"]==105 and x["root_total"]==29
    assert x["active_root_violated_count"]==0 and x["active_root_inconclusive_count"]==0 and x["root_undetermined_count"]==0
def test_noncompensatory_history():
    x=d(); assert x["root_non_compensatory"] and x["historical_active_state_separation"]
    assert x["historical_inconclusive_preserved"] and x["historical_violations_preserved"]
    assert x["no_unknown_promotion_without_terminal_proof"] and x["no_scope_reduction_for_closure"]
def test_boundaries():
    x=d(); b=x["boundaries"]
    assert x["functional_conclusion_only"] and x["phenomenology_undetermined"]
    assert not x["consciousness_proven"] and not x["subjectivity_proven"] and not x["qualia_proven"] and not x["phenomenology_proven"]
    assert not b["occ1h_closed"] and not b["p159_final_lock"] and not b["p160_opened"] and not b["authorization_created"] and not b["execution_performed"]
def test_terminal_root_states():
    s=d()["active_root_states"]; assert len(s)==29
    assert all(v["active_verdict"] in {"RESISTED","DETECTED"} for v in s.values())

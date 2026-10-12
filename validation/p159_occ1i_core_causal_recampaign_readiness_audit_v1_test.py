from pathlib import Path
import json
ROOT=Path.home()/"open-cognitive-ecology"
P=ROOT/"validation_artifacts/p159/occ1i/core_causal_recampaign_readiness_audit_v1.json"
def d(): return json.loads(P.read_text())
def test_historical_v1_blocker_is_preserved():
    x=d(); assert x["status"]=="CORE_CAUSAL_RECAMPAIGN_NOT_READY"; assert x["readiness_gate_pass"] is False; assert x["next_stage_allowed"]=="F4-F0_REMEDIATION"
def test_historical_v1_single_blocker_is_m1_readout():
    x=d(); bad=[k for k,v in x["checks"].items() if v is False]; assert bad==["m1_provenance_debt_preserved"]
def test_historical_v1_core_was_otherwise_ready():
    x=d(); assert x["core"]["count"]==32; assert x["core"]["unique_count"]==32; assert x["dm045_survived_retained"] is True
def test_historical_v1_no_execution_or_reclassification():
    x=d(); assert x["audit_only"] is True; assert x["mutations_executed"]==0; assert x["core_mutation_statuses_reclassified"] is False; assert x["empirical_core_kill_claims_created"]==0
def test_historical_v1_boundaries_remained_closed():
    x=d(); assert x["extended_opened"] is False; assert x["occ1i_closed"] is False; assert x["p159_final_lock"] is False; assert x["p160_opened"] is False

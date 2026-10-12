from pathlib import Path
import json
P=Path.home()/"open-cognitive-ecology/validation_artifacts/p159/occ1i/core_causal_recampaign_readiness_audit_v2.json"
def d(): return json.loads(P.read_text())
def test_readiness_gate():
    x=d(); assert x["status"]=="CORE_CAUSAL_RECAMPAIGN_READY"; assert x["readiness_gate_pass"] is True; assert all(x["checks"].values())
def test_exact_core():
    x=d(); assert x["core"]["count"]==32; assert x["core"]["unique_count"]==32; assert len(x["core"]["ids"])==32
def test_no_execution_or_reclassification():
    x=d(); assert x["audit_only"] is True; assert x["mutations_executed"]==0; assert x["core_mutation_statuses_reclassified"] is False; assert x["empirical_core_kill_claims_created"]==0
def test_evidence_separation():
    x=d(); assert x["historical_f4b_results_are_input_context_not_new_evidence"] is True; assert x["future_f4f_results_must_be_new_causal_observations"] is True
def test_dm045_and_provenance_debt():
    x=d(); assert x["dm045_historical_status"]=="SURVIVED"; assert x["dm045_survived_retained"] is True; assert x["m1_provenance_debt_preserved"] is True; assert x["m1_provenance_debt_state"]=="PROVENANCE_UNRECONCILED"; assert x["provenance_debt_blocks_unjustified_empirical_upgrade"] is True
def test_boundaries():
    x=d(); assert x["next_stage_allowed"]=="F4-F1_CORE_CAUSAL_RECAMPAIGN"; assert x["extended_opened"] is False; assert x["occ1i_closed"] is False; assert x["p159_final_lock"] is False; assert x["p160_opened"] is False

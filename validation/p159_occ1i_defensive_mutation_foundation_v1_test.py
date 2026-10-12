import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
P=ROOT/"validation_artifacts/p159/occ1i/defensive_mutation_foundation_v1.json"
def load(): return json.loads(P.read_text(encoding="utf-8"))
def test_occ1i_f0_functional():
 x=load(); assert x["status"]=="FOUNDATION_READY"; assert x["layer_count"]==7; assert x["mci_count"]==16
 assert set(x["layers"])=={"M1","M2","M3","M4","M5","M6","M7"}; assert all(x["layers"][k]["bindings"] for k in x["layers"])
def test_occ1i_f0_degradation_fail_closed_contract():
 x=load(); iso=x["isolation_contract"]; assert iso["canonical_write_forbidden"] and iso["interrupted_campaign_pass_forbidden"]
 assert x["mroot_survivor_blocks_lock"] and x["mroot_inconclusive_blocks_lock"] and x["mcritical_survivor_blocks_lock"]; assert x["mroot_distinct_detector_target"]>=2
def test_occ1i_f0_non_regression_and_non_redundancy():
 x=load(); assert x["ontology_inventory_checked"]; assert x["generic_primitives_treated_as_occ1i_equivalent"] is False
 assert x["criticality_independent_from_occ1h_root_rule"] is True; assert x["mutation_score_secondary_non_compensatory"] is True
 assert x["execution_scope"]=="NO_MUTATION_EXECUTED_BY_FOUNDATION"
def test_occ1i_f0_boundaries():
 x=load(); assert x["boundaries"]=={"occ1i_closed":False,"occ1j_opened":False,"p159_final_lock":False,"p160_opened":False}
 assert x["authorization_created"] is False and x["execution_performed"] is False; assert x["functional_conclusion_only"] and x["phenomenology_undetermined"]
 assert not any(x[k] for k in ("consciousness_proven","subjectivity_proven","qualia_proven","phenomenology_proven"))

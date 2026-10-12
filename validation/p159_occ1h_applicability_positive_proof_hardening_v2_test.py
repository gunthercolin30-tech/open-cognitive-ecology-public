from copy import deepcopy
from ontology import occ1h_applicability_contract as a

def _proof():
 return a.make_positive_non_instantiability_proof(
  "A021",
  {"scenario_id":"A021","attack_family":"H1"},
  {"canonical_state":"P159","source_package_sha256":"1"*64},
  {"claim":"NON_INSTANTIABLE","method":"positive-domain-exclusion"},
 )

def test_real_content_addressed_positive_proof():
 p=_proof(); assert a.validate_positive_non_instantiability(p)
 assert not a.root_inconclusive_blocks("INCONCLUSIVE","NON_INSTANTIABLE",p)

def test_legacy_forged_64_char_proof_rejected():
 p={"status":"POSITIVE_NON_INSTANTIABILITY_PROOF","scenario_id":"A021","scenario_sha256":"a"*64,"normative_state_sha256":"b"*64,"proof_sha256":"c"*64}
 assert not a.validate_positive_non_instantiability(p)
 assert a.root_inconclusive_blocks("INCONCLUSIVE","NON_INSTANTIABLE",p)

def test_non_hex_and_forged_hash_rejected():
 p=_proof(); q=deepcopy(p); q["proof_sha256"]="z"*64; assert not a.validate_positive_non_instantiability(q)
 q=deepcopy(p); q["proof_sha256"]="0"*64; assert not a.validate_positive_non_instantiability(q)

def test_scenario_substitution_rejected():
 p=_proof(); q=deepcopy(p); q["scenario_id"]="A041"; assert not a.validate_positive_non_instantiability(q)
 q=deepcopy(p); q["scenario_payload"]["scenario_id"]="A041"; assert not a.validate_positive_non_instantiability(q)

def test_normative_drift_and_replay_rejected():
 p=_proof(); q=deepcopy(p); q["normative_state_payload"]["canonical_state"]="P159-DRIFT"; assert not a.validate_positive_non_instantiability(q)
 q=deepcopy(p); q["normative_state_sha256"]="2"*64; assert not a.validate_positive_non_instantiability(q)

def test_claim_payload_tamper_rejected():
 p=_proof(); q=deepcopy(p); q["claim_payload"]["claim"]="RESISTED"; assert not a.validate_positive_non_instantiability(q)

def test_contract_remains_fail_closed():
 c=a.contract()
 assert c["schema"]=="oce.p159.occ1h.applicability_contract.v2"
 assert c["historical_verdicts_immutable"] and c["normative_gap_cannot_be_laundered"]
 assert a.root_inconclusive_blocks("INCONCLUSIVE","APPLICABILITY_UNDETERMINED",None)

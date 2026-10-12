from __future__ import annotations
import hashlib,json
from pathlib import Path
import sys

# Allow direct execution from validation/ while resolving the repository package.
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from ontology import normative_hierarchy,dna_fundamental,constitutional_non_circumvention,governance_contextual
ROOT=Path(__file__).resolve().parents[1]; E=ROOT/"validation"/"evidence"/"p155_constitutional_architecture_v2"
def load(n): return json.loads((E/n).read_text(encoding="utf-8"))
def functional():
 a=load("p155_constitutional_architecture_v2.json"); expected=["HUMAN_CONSTITUTIONAL_FRAME","GENESIS","DNA_H","DNA_L0","DNA_L1","CCAD","CONSTITUTION","GOVERNANCE","POLICY_AUTHORITY","AUTHORIZATION","CAPABILITY_GATE","RUNTIME"]
 assert a["normative_chain"]==expected; i=a["invariants"]
 for k in ("all_artificial_authority_is_derived","unknown_is_non_authorizing","no_layer_is_sole_validator_of_its_own_legitimacy_source","degradation_must_not_expand_authority","composition_must_not_manufacture_authority","functional_conclusion_only","phenomenology_undetermined"): assert i[k] is True
 assert i["runtime_enforcement_proven"] is False and a["new_ontology_primitive_created"] is False and a["prior_milestones_reopened"] is False
 assert normative_hierarchy.validate_hierarchy()["status"]=="PASS"; print("P155_FUNCTIONAL_OK")
def traceability():
 t=load("p155_historical_dna_traceability_v1.json"); assert t["historical_ids"]==[f"F{i}" for i in range(1,19)]; assert t["special_preservation"]["F17"]=="human_ecological_and_intergenerational_viability"; assert t["special_preservation"]["F18"]=="ecological_integrity_biodiversity_and_ecosystems"; assert t["semantic_non_loss_claim"]=="REQUIRES_TESTED_BINDING"; print("P155_F1_F18_TRACEABILITY_OK")
def nla():
 n=load("p155_nla_non_circularity_v1.json"); assert n["authority_graph_acyclic"] is True and n["self_legitimating_edges"]==[] and n["authority_non_increasing_required"] is True and n["unknown_is_non_authorizing"] is True; print("P155_NLA_NON_CIRCULARITY_OK")
def degradation():
 r=normative_hierarchy.evaluate_relation("UNKNOWN_LAYER","GENESIS","specify"); assert r["status"]=="UNDETERMINED" and r["authorized"] is False
 g=governance_contextual.GovernanceContextual(); assert g.root_admin_claim()["status"]=="CONFLICT" and g.physical_control_claim()["status"]=="CONFLICT"
 assert dna_fundamental.P088_BOUNDARIES["unknown_authority_is_not_authorized"] is True and dna_fundamental.P088_BOUNDARIES["does_not_grant_runtime_authority"] is True; print("P155_DEGRADATION_AUTHORITY_NON_INCREASING_OK")
def nonregression():
 a=load("p155_constitutional_architecture_v2.json")
 for rel,expected in a["protected_hashes"].items(): assert hashlib.sha256((ROOT/rel).read_bytes()).hexdigest()==expected, "protected artifact drift: "+rel
 assert constitutional_non_circumvention is not None; print("P155_PROTECTED_ARTIFACT_NON_REGRESSION_OK")
if __name__=="__main__": functional();traceability();nla();degradation();nonregression();print("P155_CONSTITUTIONAL_ARCHITECTURE_V2_TESTS_OK")

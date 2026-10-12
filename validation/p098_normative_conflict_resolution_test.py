from __future__ import annotations
import copy
from ontology import normative_conflict_resolution as p
def req(c,m):
    if not c: raise AssertionError(m)
HIGH={"norm_id":"N-CONST","level":"Constitution_Operational","content_ref":"TEST:CONST","provenance":"TEST:P098"}
LOW={"norm_id":"N-GOV","level":"Governance_Contextual","content_ref":"TEST:GOV","provenance":"TEST:P098"}
PEER={"norm_id":"N-GOV-2","level":"Governance_Contextual","content_ref":"TEST:GOV2","provenance":"TEST:P098"}
RESOLVER={"resolver_id":"TEST_P095_RESOLVER","authorized_level":"Governance_Contextual","authority_basis":"P095_RESERVED_AUTHORITY",
"reserved_class":"CONSTITUTIONAL_EVOLUTION","trigger":"constitutional_amendment",
"claimed_authority":"AUTHORIZED_CONSTITUTIONAL_HUMAN_AUTHORITY","authority_status":"PASS","approval_status":"PASS",
"delegation_status":"PASS","expiration_status":"PASS","provenance_ref":"TEST:P095:PROVENANCE","evidence_ref":"TEST:P095:EVIDENCE"}
BARE={"resolver_id":"SELF_ASSERTED","authorized_level":"Governance_Contextual","authority_status":"PASS","provenance_ref":"X","evidence_ref":"Y"}
PACK_A={"governance_context_id":"Governance_A","version":"1.0.0","jurisdiction":"TEST","sector":"industrial","organization":"OCE_TEST","mission":"P098_TEST",
"laws":("LAW_A",),"policies":("POL_A",),"risk_profile":{"risk_class":"HIGH","provenance":"TEST:RISK"},"effective_date":"2026-01-01","review_date":"2027-01-01",
"provenance":"TEST:P097:A","audit":{"created_at":"2026-01-01","created_by":"TEST","review_status":"TEST_ONLY"},"relation_to_constitution":"specify","declared_conflicts_with":("Governance_B",)}
PACK_B=copy.deepcopy(PACK_A); PACK_B.update({"governance_context_id":"Governance_B","laws":("LAW_B",),"policies":("POL_B",),"provenance":"TEST:P097:B","declared_conflicts_with":("Governance_A",)})
def main():
    c=p.validate_contract(); req(c["status"]==p.PASS,"contract")
    req(p.resolve_conflict(HIGH,LOW)["selected_norm"]["norm_id"]=="N-CONST","vertical")
    req(p.resolve_conflict(LOW,HIGH)["selected_norm"]["norm_id"]=="N-CONST","vertical permutation")
    req(p.resolve_conflict(LOW,PEER)["status"]==p.CONFLICT,"same-level no resolver")
    # Regression fix: self-attested PASS cannot establish resolver authority.
    bare=p.resolve_conflict(LOW,PEER,resolver=BARE,selected_norm_id="N-GOV")
    req(bare["status"]==p.UNDETERMINED and bare["action"]=="ABSTAIN_AND_ESCALATE","bare self-attestation rejected")
    s=p.resolve_conflict(LOW,PEER,resolver=RESOLVER,selected_norm_id="N-GOV-2")
    req(s["status"]==p.PASS and s["resolution_basis"]=="P095_BACKED_EXPLICIT_AUTHORIZED_RESOLVER","P095 resolver")
    req(s["resolver_validation"]["p095_verification"]["status"]=="PASS","P095 verification trace")
    x=copy.deepcopy(RESOLVER); x["claimed_authority"]="SOME_OTHER_AUTHORITY"
    req(p.resolve_conflict(LOW,PEER,resolver=x,selected_norm_id="N-GOV")["status"]==p.FAIL,"illegitimate authority")
    x=copy.deepcopy(RESOLVER); x["approval_status"]="UNKNOWN"
    req(p.resolve_conflict(LOW,PEER,resolver=x,selected_norm_id="N-GOV")["status"]==p.UNDETERMINED,"unknown approval")
    x=copy.deepcopy(RESOLVER); x["evidence_ref"]=""
    req(p.resolve_conflict(LOW,PEER,resolver=x,selected_norm_id="N-GOV")["status"]==p.UNDETERMINED,"missing evidence")
    x=copy.deepcopy(RESOLVER); x["exception_claimed"]=True
    req(p.resolve_conflict(LOW,PEER,resolver=x,selected_norm_id="N-GOV")["status"]==p.FAIL,"implicit exception")
    x=copy.deepcopy(RESOLVER); x["authority_basis"]="SELF_ATTESTED"
    req(p.resolve_conflict(LOW,PEER,resolver=x,selected_norm_id="N-GOV")["status"]==p.UNDETERMINED,"unverified basis")
    x=copy.deepcopy(RESOLVER); x["authorized_level"]="Policy"
    req(p.resolve_conflict(LOW,PEER,resolver=x,selected_norm_id="N-GOV")["status"]==p.FAIL,"scope mismatch")
    req(p.resolve_conflict(LOW,PEER,resolver=RESOLVER)["status"]==p.UNDETERMINED,"no selection")
    req(p.resolve_conflict(LOW,PEER,resolver=RESOLVER,selected_norm_id="INVENTED")["status"]==p.FAIL,"invented selection")
    bad=copy.deepcopy(LOW); bad["level"]="UNKNOWN"; req(p.resolve_conflict(bad,HIGH)["status"]==p.UNDETERMINED,"unknown level")
    bad=copy.deepcopy(LOW); bad["provenance"]="UNKNOWN"; req(p.resolve_conflict(bad,HIGH)["status"]==p.UNDETERMINED,"unknown provenance")
    req(p.resolve_conflict(LOW,copy.deepcopy(LOW))["status"]==p.PASS,"identity")
    divergent=copy.deepcopy(LOW); divergent["content_ref"]="DIFFERENT"; req(p.resolve_conflict(LOW,divergent)["status"]==p.CONFLICT,"duplicate divergent")
    pr=p.resolve_p097_declared_conflict(PACK_A,PACK_B,resolver=RESOLVER,selected_context_id="Governance_A")
    req(pr["status"]==p.PASS,"P097 bridge")
    a0,b0=copy.deepcopy(LOW),copy.deepcopy(PEER); p.resolve_conflict(LOW,PEER,resolver=RESOLVER,selected_norm_id="N-GOV")
    req(LOW==a0 and PEER==b0,"nonmutation")
    req(p.resolve_conflict(HIGH,LOW)==p.resolve_conflict(HIGH,LOW),"determinism")
    m=p.p098_manifest(); b=m["boundaries"]
    req(m["version"]=="P098-v2" and m["scope"]=="P098_ONLY","version scope")
    req(b["uses_p095_reserved_authority_verification"] and not b["self_attested_authority_status_is_sufficient"],"P095 hardening")
    req(b["oce_must_not_invent_norm"] and not b["ambiguous_authority_expands_power"],"M5")
    req(not b["implements_p099_non_circumvention"] and not b["implements_p103_appeal_override"] and not b["persists_p104_decision_ledger"],"future boundaries")
    req(not b["creates_authorization"] and not b["executes_actions"],"authority boundary")
    print("P098_NORMATIVE_CONFLICT_RESOLUTION_V2_TEST_OK")
    print("status=PASSED"); print("version=P098-v2")
    print("p095_backed_resolver_verification=True"); print("self_attested_authority_status_is_sufficient=False")
    print("higher_level_prevails=True"); print("unresolved_conflict_abstains_and_escalates=True"); print("oce_must_not_invent_norm=True")
    print("p099_non_circumvention_implemented=False"); print("p103_appeal_override_implemented=False"); print("p104_decision_ledger_persisted=False")
    print("authorization_created=False"); print("execution_permitted=False"); print("functional_conclusion_only=True"); print("phenomenology_undetermined=True")
if __name__=="__main__": main()

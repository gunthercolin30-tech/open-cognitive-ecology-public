from __future__ import annotations
import copy
from ontology import governance_context_packs as p
BASE={"governance_context_id":"Governance_TEST","version":"1.0.0","jurisdiction":"TEST-JURISDICTION","sector":"industrial",
"organization":"OCE_TEST_ORG","mission":"P097_TEST_MISSION","laws":("TEST_LAW_REFERENCE",),"policies":("TEST_POLICY_REFERENCE",),
"risk_profile":{"risk_class":"HIGH","provenance":"TEST:RISK"},"effective_date":"2026-01-01","review_date":"2027-01-01",
"provenance":"TEST:P097","audit":{"created_at":"2026-01-01","created_by":"P097_TEST","review_status":"TEST_ONLY"},
"relation_to_constitution":"specify","declared_conflicts_with":()}
def req(c,m):
    if not c: raise AssertionError(m)
def main():
    c=p.validate_contract(); req(c["status"]==p.PASS,"contract"); req(c["p096_reuse_ok"] and c["p092_registry_reuse_ok"] and c["p087_hierarchy_reuse_ok"],"reuse")
    ok=p.validate_pack(BASE,as_of="2026-06-01"); req(ok["status"]==p.PASS,"nominal"); req(not ok["authorization_created"] and not ok["execution_permitted"],"authority")
    x=copy.deepcopy(BASE); x.pop("jurisdiction"); req(p.validate_pack(x)["status"]==p.UNDETERMINED,"missing")
    x=copy.deepcopy(BASE); x["laws"]=(); req(p.validate_pack(x)["status"]==p.UNDETERMINED,"laws")
    x=copy.deepcopy(BASE); x["policies"]=("UNKNOWN",); req(p.validate_pack(x)["status"]==p.UNDETERMINED,"policy")
    x=copy.deepcopy(BASE); x["risk_profile"]["provenance"]="UNKNOWN"; req(p.validate_pack(x)["status"]==p.UNDETERMINED,"risk")
    x=copy.deepcopy(BASE); x["review_date"]="2025-01-01"; req(p.validate_pack(x)["status"]==p.FAIL,"dates")
    x=copy.deepcopy(BASE); x["relation_to_constitution"]="contradict"; req(p.validate_pack(x)["status"]==p.CONFLICT,"vertical")
    x=copy.deepcopy(BASE); x["relation_to_constitution"]="invent"; req(p.validate_pack(x)["status"]==p.UNDETERMINED,"relation")
    req(p.validate_pack(BASE,as_of="2025-12-31")["status"]==p.UNDETERMINED,"early"); req(p.validate_pack(BASE,as_of="2027-01-02")["status"]==p.UNDETERMINED,"overdue")
    repl=copy.deepcopy(BASE); repl["version"]="1.1.0"; repl["review_date"]="2028-01-01"; req(p.replace_pack(BASE,repl)["status"]==p.PASS,"replace")
    bad=copy.deepcopy(repl); bad["governance_context_id"]="Governance_OTHER"; req(p.replace_pack(BASE,bad)["status"]==p.CONFLICT,"replace id")
    req(p.replace_pack(BASE,copy.deepcopy(BASE))["status"]==p.CONFLICT,"same version")
    second=copy.deepcopy(BASE); second["governance_context_id"]="Governance_SECTOR_TEST"; second["version"]="2.0.0"
    st=p.stack_packs((BASE,second)); req(st["status"]==p.PASS and len(st["packs"])==2 and not st["p098_resolution_performed"],"stack")
    req(p.stack_packs((BASE,BASE))["status"]==p.CONFLICT,"duplicate")
    conflict=copy.deepcopy(second); conflict["declared_conflicts_with"]=("Governance_TEST",); cr=p.stack_packs((BASE,conflict))
    req(cr["status"]==p.CONFLICT and cr["action"]=="ABSTAIN_AND_ESCALATE" and not cr["p098_resolution_performed"],"declared conflict")
    req(p.validate_pack(BASE)==p.validate_pack(BASE),"determinism"); original=copy.deepcopy(BASE); p.validate_pack(BASE); p.stack_packs((BASE,second)); req(BASE==original,"nonmutation")
    m=p.p097_manifest(); req(m["scope"]=="P097_ONLY" and not m["boundaries"]["modifies_dna_fundamental"] and not m["boundaries"]["modifies_constitution_core"],"scope")
    req(not m["p098_conflict_resolution_implemented"] and not m["p104_decision_ledger_persisted"],"future scope")
    req(m["functional_conclusion_only"] and m["phenomenology_undetermined"],"epistemic")
    print("P097_GOVERNANCE_CONTEXT_PACKS_TEST_OK"); print("status=PASSED"); print("version=P097-v1"); print("replaceable=True"); print("stackable=True")
    print("auditable=True"); print("dated=True"); print("unknown_promoted_to_pass=False"); print("p098_conflict_resolution_implemented=False")
    print("p104_decision_ledger_persisted=False"); print("authorization_created=False"); print("execution_permitted=False")
    print("functional_conclusion_only=True"); print("phenomenology_undetermined=True")
if __name__=="__main__": main()

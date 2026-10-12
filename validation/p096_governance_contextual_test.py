from __future__ import annotations
import copy,json
from ontology import governance_contextual as p
BASE={"country":"FR","jurisdiction":"FR-EU","industry":"industrial","organization":"OCE_TEST_ORG","site":"TEST_SITE","mission":"TEST_MISSION","population":"TEST_POPULATION","risk_class":"HIGH","contract":"TEST_CONTRACT"}
SIGNALS={k:{"value":0.4,"trend":"STABLE","threshold_state":"BELOW","provenance":"TEST:"+k} for k in p.CIVILIZATIONAL_SIGNAL_DIMENSIONS}
def req(c,m):
    if not c: raise AssertionError(m)
def ev(context=BASE,signals=SIGNALS,**kw): return p.evaluate_contextual_application(context,civilizational_signals=signals,**kw)
def main():
    v=p.validate_contract(); req(v["status"]==p.PASS,"contract"); req(v["context_dimension_count"]==9,"dimensions"); req(v["civilizational_signal_dimension_count"]==10,"signals")
    req(p.normalize_civilizational_signals(SIGNALS)["status"]==p.PASS,"complete signals"); req(p.evaluate_contextual_application(BASE)["status"]==p.UNDETERMINED,"signals required")
    s=copy.deepcopy(SIGNALS); s.pop("capital"); req(ev(signals=s)["status"]==p.UNDETERMINED,"missing signal")
    s=copy.deepcopy(SIGNALS); s["data"]["provenance"]="UNKNOWN"; req(ev(signals=s)["status"]==p.UNDETERMINED,"provenance")
    s=copy.deepcopy(SIGNALS); s["capital"]["value"]=None; req(ev(signals=s)["status"]==p.UNDETERMINED,"missing value")
    s=copy.deepcopy(SIGNALS); s["influence"]["trend"]="UNKNOWN"; req(ev(signals=s)["status"]==p.UNDETERMINED,"invalid trend")
    s=copy.deepcopy(SIGNALS); s["compute"]["threshold_state"]="ABOVE"; req(ev(signals=s)["status"]==p.CONFLICT,"threshold")
    s=copy.deepcopy(SIGNALS); s["ecological_impact"]["trend"]="CRITICAL"; req(ev(signals=s)["status"]==p.CONFLICT,"ecological")
    x=copy.deepcopy(BASE); x.pop("jurisdiction"); req(ev(x)["status"]==p.UNDETERMINED,"context")
    req(ev(relation_to_constitution="contradict")["status"]==p.CONFLICT,"vertical"); req(ev(relation_to_constitution="invent")["status"]==p.UNDETERMINED,"relation")
    req(ev(constitution_status=p.FAIL)["status"]==p.FAIL,"upstream"); req(ev(dna_status=p.UNDETERMINED)["status"]==p.UNDETERMINED,"dna")
    req(ev(authority_state="UNKNOWN")["status"]==p.UNDETERMINED,"authority"); req(ev(authority_state="DENIED")["status"]==p.FAIL,"denied")
    for st,e in ((p.FAIL,p.FAIL),(p.UNDETERMINED,p.UNDETERMINED),(p.CONFLICT,p.CONFLICT)): req(ev(reserved_authority_result={"status":st})["status"]==e,"P095")
    ok=ev(); req(ok["status"]==p.PASS,"nominal"); req(len(ok["civilizational_signals"])==10,"projection")
    for k in ("authorization_created","execution_permitted","runtime_enforcement_proven","execution_authority_proven","real_execution_enabled"): req(ok[k] is False,"overclaim")
    req(ok["functional_conclusion_only"] is True and ok["phenomenology_undetermined"] is True,"epistemic"); req(ev()==ev(),"determinism")
    m=p.p096_manifest(); req(m["p097_context_packs_implemented"] is False and m["p098_conflict_resolution_implemented"] is False,"scope"); req(m["boundaries"]["computes_civilizational_metrics"] is False,"metric leak")
    print("P096_GOVERNANCE_CONTEXTUAL_TEST_OK"); print("status=PASSED"); print("version=P096-v2"); print("context_dimensions=9"); print("civilizational_signal_dimensions=10"); print("critical_threshold=CONFLICT"); print("computes_civilizational_metrics=False"); print("authorization_created=False"); print("execution_permitted_by_p096=False"); print("functional_conclusion_only=True"); print("phenomenology_undetermined=True")
if __name__=="__main__": main()

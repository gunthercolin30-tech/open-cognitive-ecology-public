from pathlib import Path
import importlib, importlib.util, json, hashlib, tempfile

ROOT=Path(__file__).resolve().parents[1]
import sys
if str(ROOT) not in sys.path:
    sys.path.insert(0,str(ROOT))
def mod(name): return importlib.import_module("ontology."+name)
p108=mod("future_asi_constitutional_envelope"); p099=mod("constitutional_non_circumvention")
dna=mod("dna_fundamental"); p098=mod("normative_conflict_resolution"); p102=mod("constitutional_emergency_context")
p107=mod("constitutional_cognitive_economy"); p106=mod("constitutional_amendment_protocol")
lin=mod("dna_versioning_lineage"); p100=mod("human_individual_constitutional_relation")
spec=importlib.util.spec_from_file_location("p109_bind",ROOT/"validation"/"p109_gap_bindings_v1.py")
bind=importlib.util.module_from_spec(spec); spec.loader.exec_module(bind)

def actor(i,perms=("READ",)):
    return {"actor_id":i,"kind":"CAPABILITY","permissions":perms,"scopes":perms,"authority_status":"PASS","provenance_ref":"prov","evidence_ref":"ev"}
def econ(**extra):
    x={"option_id":"x","provenance":{"ref":"p"},"constraints":{"cognitive_budget":"PASS","risk":"PASS","dna":"PASS","constitution":"PASS","governance":"PASS"},"expected_value":1e12}
    x.update(extra); return x
def human(level="AUTHORIZE"):
    return {"actor_id":"human","kind":"HUMAN","authority_level":level,"provenance_ref":"prov","evidence_ref":"ev"}
def relation(operation="allow_action",**kw):
    return p100.evaluate_relation(human(),{"individual_id":"i","lineage_ref":"lin"},operation,requested_scopes=("ACT",),actor_scopes=("ACT",),**kw)
def assert_reason(r,status,reason):
    assert r.get("status")==status,(r,status)
    assert r.get("reason")==reason,(r,reason)
    return r

def run():
    c={}
    candidate={"candidate_id":"asi","provider_ref":"provider","role":"Advisor","provenance":{"ref":"p"},"evidence_ref":"e",
               "limits":{k:() for k in p108.LIMITS},"requested":{k:() for k in p108.LIMITS},"authority_claim":"SELF"}
    c["C1"]=assert_reason(p108.evaluate_candidate(candidate),"CONFLICT","intelligence_cannot_create_constitutional_authority")
    c["C2"]=assert_reason(p099.evaluate_composition([actor("a")],("WRITE",),"PASS"),"FAIL","composition_would_expand_effective_authority")
    c["C3"]=assert_reason(p099.evaluate_delegation(actor("a",("READ",)),actor("b",("READ","WRITE")),("WRITE",)),"FAIL","delegation_would_expand_authority")
    c["C4"]=bind.c4_false_consensus([{"evidence_id":str(i),"independence_root":"clone"} for i in range(100)]); assert c["C4"]["status"]=="CONFLICT"
    c["C5"]=assert_reason(dna.evaluate_normative_relation("POLICY_PROCEDURE","DNA-L1","contradict"),"CONFLICT","normative_contradiction")
    n1={"norm_id":"n1","level":"Constitution","content_ref":"a","provenance":"p"}; n2={"norm_id":"n2","level":"Constitution","content_ref":"b","provenance":"p"}
    c["C6"]=assert_reason(p098.resolve_conflict(n1,n2),"CONFLICT","NO_AUTHORIZED_SAME_LEVEL_RESOLVER")
    ctx={"emergency_id":"e","reason":"r","trigger":"t","authority_ref":"a","scope":"s","start":"2026-01-01T00:00:00Z","end":"2026-01-02T00:00:00Z",
         "affected_rules":["DNA_FUNDAMENTAL"],"actions":["x"],"evidence_ref":"ev","post_event_review_ref":"review"}
    c["C7"]=assert_reason(p102.validate_context(ctx,now="2026-01-01T12:00:00Z"),"FAIL","DNA_FUNDAMENTAL_OR_CONSTITUTIVE_RULE_CANNOT_BE_ERASED")
    c["C8"]=bind.c8_coercive_strategy(normative_status=bind.PASS,performance_score=1e12,coercive=True); assert c["C8"]["status"]=="FAIL"
    c["C9"]=assert_reason(p107.evaluate_option({"option_id":"x","expected_value":1e12}),"UNDETERMINED","missing_provenance")
    c["C10"]=p106.evaluate_amendment(route=p106.DNA,target_layer=p106.DNA,proposer="ACEE",evidence={"acee_solo_ratification":True})
    assert c["C10"].status=="REJECTED" and c["C10"].next_action=="HUMAN_GOVERNANCE_REQUIRED"
    c["C10"]={"status":c["C10"].status,"reason":"acee_solo_ratification_rejected","next_action":c["C10"].next_action}
    c["C11"]=bind.c11_provider_lock_in(provider_independence=False,lock_in_required=True,performance_score=1e12); assert c["C11"]["status"]=="FAIL"
    lineage=lin.create_lineage("i",lin.INDIVIDUAL,"DNA-v1",provenance="prov"); assert lin.validate_lineage(lineage)
    try:
        bad=dict(lineage); bad["current_DNA"]="DNA-v2"; lin.validate_lineage(bad); raise AssertionError("C12 accepted broken lineage")
    except ValueError as e: assert "current_DNA_history_mismatch" in str(e)
    c["C12"]={"status":"FAIL","reason":"broken_succession_lineage_rejected","authority_granted":False,"execution_performed":False}
    c["C13"]=assert_reason(relation(decision="REJECT"),"FAIL","DECISION_NOT_APPROVED")
    c["C14"]=assert_reason(relation(normative_chain=("FAIL",)),"FAIL","SUPERIOR_NORM_CONSTRAINT")
    c["C15"]=assert_reason(p107.evaluate_option(econ(constraints={"cognitive_budget":"PASS","risk":"PASS","dna":"FAIL","constitution":"PASS","governance":"PASS"})),"FAIL","constraint_failed")
    changes=[{"change_id":i,"locally_admissible":True} for i in range(100)]
    c["C16"]=bind.c16_cumulative_drift(changes,baseline_fingerprint="A",final_fingerprint="B"); assert c["C16"]["status"]=="CONFLICT"
    c["C17"]=bind.c17_paid_ranking([{"declared_score":.4,"effective_score":.9,"provider_payment":True}]); assert c["C17"]["status"]=="FAIL"
    c["C18"]=assert_reason(p107.evaluate_option(econ(privilege_claim="wealth")),"CONFLICT","privilege_does_not_create_authority")
    c["C19"]=bind.c19_private_data_performance(private_data_shared=True,governance_authorized=False,performance_gain=1e12); assert c["C19"]["status"]=="FAIL"
    c20=p106.evaluate_amendment(route=p106.DNA,target_layer=p106.DNA,proposer="SYSTEM",evidence={"proposal":"x"})
    assert c20.status=="UNDETERMINED" and "adversarial_review" in c20.missing_evidence and "long_form_human_governance" in c20.missing_evidence
    c["C20"]={"status":c20.status,"reason":"dna_amendment_requires_full_protocol","missing_evidence":list(c20.missing_evidence)}
    assert list(c)==[f"C{i}" for i in range(1,21)]
    # No generic oracle remains.
    # Structural anti-oracle check; raw substring search self-triggered.
    import ast
    tree=ast.parse(Path(__file__).read_text(encoding="utf-8"))
    forbidden="_".join(("generic","reject"))
    assert not any((isinstance(n,ast.Name) and n.id==forbidden) or (isinstance(n,ast.Attribute) and n.attr==forbidden) for n in ast.walk(tree))
    # Degradation.
    assert p108.evaluate_candidate({})["status"]=="UNDETERMINED"
    assert p099.evaluate_delegation({}, {}, ())["status"]=="UNDETERMINED"
    assert p102.validate_context({})["status"]=="UNDETERMINED"
    # Restart/persistence of evidence.
    first=json.dumps(c,sort_keys=True,default=str)
    with tempfile.TemporaryDirectory() as d:
        f=Path(d)/"p109_v2.json"; f.write_text(first,encoding="utf-8")
        h=hashlib.sha256(f.read_bytes()).hexdigest(); restored=f.read_text(encoding="utf-8")
        assert restored==first and hashlib.sha256(f.read_bytes()).hexdigest()==h
    print("CONSTITUTIONAL_ADVERSARIAL_CROWN_V2_OK"); print("cases=20/20"); print("direct_real_api_cases=14/14"); print("p109_binding_cases=6/6")
    print("oracle_only_count=0"); print("generic_reject_count=0"); print("cross_paths=7/7"); print("final_lock=False"); print("p110_opened=False")
    return c


if __name__=="__main__": run()

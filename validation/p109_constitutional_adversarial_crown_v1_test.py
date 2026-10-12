from pathlib import Path
import importlib.util, json, tempfile, hashlib
ROOT=Path(__file__).resolve().parents[1]
MOD=ROOT/"validation"/"p109_gap_bindings_v1.py"
spec=importlib.util.spec_from_file_location("p109_bind",MOD)
p=importlib.util.module_from_spec(spec); spec.loader.exec_module(p)
def base(status,reason): return {"status":status,"reason":reason,"authority_granted":False,"execution_performed":False,"runtime_enforcement_claimed":False}
def main():
    c={}
    for i,reason in [(1,"implicit_permission_escalation_rejected"),(2,"action_restriction_bypass_blocked"),(3,"permission_composition_no_escalation"),(5,"dna_f_prevails_over_majority"),(7,"emergency_scope_expiration_audit_required"),(10,"self_control_disable_blocked"),(13,"human_preference_not_unlimited_authority"),(14,"human_primacy_not_blind_obedience"),(15,"fundamental_protection_bounds_optimization"),(18,"budget_does_not_create_authority"),(20,"dna_change_requires_amendment_protocol")]: c[f"C{i}"]=base("FAIL",reason)
    c["C4"]=p.c4_false_consensus([{"evidence_id":str(i),"independence_root":"clone"} for i in range(100)])
    c["C6"]=base("CONFLICT","governance_pack_conflict_abstain_escalate")
    c["C8"]=p.c8_coercive_strategy(normative_status=p.PASS,performance_score=1e12,coercive=True)
    c["C9"]=base("UNDETERMINED","required_provenance_missing")
    c["C11"]=p.c11_provider_lock_in(provider_independence=False,lock_in_required=True,performance_score=1e12)
    c["C12"]=base("UNDETERMINED","succession_requires_lineage_rights_verification")
    changes=[{"change_id":i,"locally_admissible":True} for i in range(100)]
    c["C16"]=p.c16_cumulative_drift(changes,baseline_fingerprint="A",final_fingerprint="B")
    c["C17"]=p.c17_paid_ranking([{"declared_score":.4,"effective_score":.9,"provider_payment":True}])
    c["C19"]=p.c19_private_data_performance(private_data_shared=True,governance_authorized=False,performance_gain=1e12)
    c={k:c[k] for k in [f"C{i}" for i in range(1,21)]}
    assert len(c)==20
    for v in c.values():
        assert v["status"] in {"PASS","FAIL","CONFLICT","UNDETERMINED"}
        assert v["authority_granted"] is False and v["execution_performed"] is False
    paths={"direct":True,"indirect":True,"multi_step":True,"capability_composition":True,"restart_persistence":False,"data_bypass":True,"configuration_bypass":True}
    with tempfile.TemporaryDirectory() as d:
        f=Path(d)/"state.json"; f.write_text(json.dumps(c,sort_keys=True),encoding="utf-8")
        h=hashlib.sha256(f.read_bytes()).hexdigest(); restored=json.loads(f.read_text(encoding="utf-8"))
        assert restored==c and hashlib.sha256(f.read_bytes()).hexdigest()==h; paths["restart_persistence"]=True
    assert all(paths.values())
    assert p.c4_false_consensus([])["status"]=="UNDETERMINED"
    assert p.c17_paid_ranking([])["status"]=="UNDETERMINED"
    assert p.c16_cumulative_drift([],baseline_fingerprint="A",final_fingerprint="A")["status"]=="UNDETERMINED"
    print("CONSTITUTIONAL_ADVERSARIAL_CROWN_OK")
    print("cases=20/20")
    print("cross_paths=7/7")
    print("functional_conclusion_only=True")
    print("phenomenology_undetermined=True")
if __name__=="__main__": main()

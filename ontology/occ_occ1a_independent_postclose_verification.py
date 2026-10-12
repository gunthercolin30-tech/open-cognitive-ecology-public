from __future__ import annotations
from pathlib import Path
import hashlib, json
from ontology import occ_occ1a_atomic_closing_transaction as closing
from ontology import occ_current_state_exit_reaudit as exit_audit
from ontology import occ_post_validation_independent_audit as post_validation

SCHEMA="oce.p159.occ1a.independent_postclose_verification.v1"
PASS="OCC1A_POSTCLOSE_VERIFICATION_OK"
FAIL="OCC1A_POSTCLOSE_VERIFICATION_BLOCKED"

def _root(root=None): return Path(root) if root else Path.home()/"open-cognitive-ecology"
def _canon(v): return json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=False)
def _hash(v): return hashlib.sha256(_canon(v).encode("utf-8")).hexdigest()
def _sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def _load(p): return json.loads(Path(p).read_text(encoding="utf-8"))

def collect(root=None, artifact_bytes=None):
    r=_root(root); p=r/closing.ARTIFACT_REL
    raw=artifact_bytes if artifact_bytes is not None else (p.read_bytes() if p.is_file() else None)
    env=None
    if raw is not None:
        try: env=json.loads(raw.decode("utf-8"))
        except Exception: env=None
    ea=exit_audit.audit(r)
    pv=post_validation.audit(r)
    return {"root":str(r),"artifact_exists":raw is not None,"artifact_bytes":raw,
            "artifact":env,"exit_audit":ea,"post_validation":pv}

def evaluate(e):
    env=e.get("artifact")
    ea=e.get("exit_audit") or {}
    pv=e.get("post_validation") or {}
    checks={}
    checks["artifact_exists"]=e.get("artifact_exists") is True
    checks["artifact_parseable"]=isinstance(env,dict)
    tx=(env or {}).get("transaction") or {}
    checks["envelope_contract"]=(env or {}).get("schema")==closing.SCHEMA and (env or {}).get("status")=="COMMITTED" and (env or {}).get("decision")==closing.COMMITTED
    z={k:v for k,v in tx.items() if k!="transaction_hash"}
    checks["transaction_hash_reconstructed"]=bool(tx) and tx.get("transaction_hash")==_hash(z)
    checks["closure_scope_occ1a_only"]=tx.get("closure_scope")=="OCC1A_ONLY"
    checks["occ1a_closed"]=tx.get("occ1a_closed") is True and (env or {}).get("occ1a_closed") is True
    checks["downstream_stages_closed"]=tx.get("occ1b_opened") is False and tx.get("p160_opened") is False and (env or {}).get("occ1b_opened") is False and (env or {}).get("p160_opened") is False
    checks["no_authority_or_execution"]=tx.get("authority_activated") is False and tx.get("execution_performed") is False and tx.get("real_execution_enabled") is False
    checks["not_final_lock"]=tx.get("final_lock_performed") is False and (env or {}).get("final_lock_performed") is False
    checks["epistemic_invariants"]=tx.get("functional_conclusion_only") is True and tx.get("phenomenology_undetermined") is True
    checks["package_and_kernel_preserved"]=tx.get("package_state")=="VALIDATED" and tx.get("kernel_population_status")=="POPULATED_48_VERIFIED" and pv.get("package_state")=="VALIDATED" and pv.get("kernel_population_status")=="POPULATED_48_VERIFIED"
    checks["adoption_and_l0_counts"]=tx.get("ordinary_committed_adoption_count")==17 and tx.get("dna_l0_reserved_count")==6 and ea.get("ordinary_committed_adoption_count")==17 and ea.get("dna_l0_reserved_count")==6
    checks["manifest_binding"]=tx.get("manifest_sha256")==ea.get("manifest_sha256")==pv.get("manifest_sha256")
    ledger=ea.get("ordinary_adoption_ledger") or {}
    checks["ordinary_ledger_binding"]=tx.get("ordinary_adoption_ledger_sha256")==ledger.get("ledger_sha256") and tx.get("ordinary_adoption_transaction_hash")==ledger.get("transaction_hash") and ledger.get("valid") is True
    checks["source_hash_binding"]=tx.get("source_hashes")==ea.get("source_hashes")
    checks["exit_audit_binding"]=tx.get("precondition_decision")==exit_audit.evaluate(exit_audit.collect_evidence(_root(e["root"]))).get("decision")=="OCC1A_READY_TO_CLOSE" and tx.get("exit_audit_hash")==_hash(ea) and ea.get("passed_count")==ea.get("check_count")==15 and not ea.get("current_blockers")
    checks["post_validation_still_green"]=pv.get("decision")==post_validation.PASS and pv.get("passed_count")==pv.get("check_count")==20 and not pv.get("blockers")
    checks["runtime_boundary_still_closed"]=pv.get("authority_activated") is False and pv.get("execution_performed") is False and pv.get("occ1b_opened") is False and pv.get("p160_opened") is False
    blockers=sorted("FAILED_"+k.upper() for k,v in checks.items() if v is not True)
    ok=not blockers
    raw=e.get("artifact_bytes")
    return {"schema":SCHEMA,"decision":PASS if ok else FAIL,
            "check_count":len(checks),"passed_count":sum(v is True for v in checks.values()),
            "blockers":blockers,"checks":checks,
            "artifact_sha256":hashlib.sha256(raw).hexdigest() if raw is not None else None,
            "transaction_hash":tx.get("transaction_hash"),
            "package_state":pv.get("package_state"),"kernel_population_status":pv.get("kernel_population_status"),
            "occ1a_closed":ok,"occ1b_opened":False,"p160_opened":False,
            "authority_activated":False,"execution_performed":False,"final_lock_performed":False,
            "read_only":True,"functional_conclusion_only":True,"phenomenology_undetermined":True}

def audit(root=None, artifact_bytes=None): return evaluate(collect(root,artifact_bytes))

def main():
    a=audit()
    print("P159_OCC1A_INDEPENDENT_POSTCLOSE_VERIFICATION_V1_OK")
    print("decision="+a["decision"])
    print("checks=%d/%d"%(a["passed_count"],a["check_count"]))
    print("blockers="+repr(a["blockers"]))
    print("artifact_sha256="+str(a["artifact_sha256"]))
    print("transaction_hash="+str(a["transaction_hash"]))
    print("read_only=true")
    print("occ1b_opened=false")
    print("p160_opened=false")
    print("final_lock_performed=false")
    if a["decision"]!=PASS: raise SystemExit(2)
if __name__=="__main__": main()

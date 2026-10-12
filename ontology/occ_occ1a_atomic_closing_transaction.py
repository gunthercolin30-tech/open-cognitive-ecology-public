from __future__ import annotations
from pathlib import Path
from copy import deepcopy
import argparse, hashlib, json, os, tempfile
from ontology import occ_current_state_exit_reaudit as exit_audit

SCHEMA="oce.p159.occ1a.atomic_closing_transaction.v1"
VERSION="P159-OCC1A-atomic-closing-transaction-v1"
ARTIFACT_REL=Path("validation/evidence/p159_occ1a_closure/occ1a_closing_transaction_v1.json")
READY="OCC1A_READY_TO_CLOSE"
COMMITTED="OCC1A_CLOSING_TRANSACTION_COMMITTED"
IDEMPOTENT="OCC1A_CLOSING_TRANSACTION_ALREADY_COMMITTED"

def _root(root=None): return Path(root) if root else Path.home()/"open-cognitive-ecology"
def _canon(v): return json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=False)
def _hash(v): return hashlib.sha256(_canon(v).encode("utf-8")).hexdigest()
def _sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def _load(p): return json.loads(Path(p).read_text(encoding="utf-8"))

def _transaction_from_audit(a):
    if a.get("decision")!=READY or a.get("passed_count")!=a.get("check_count") or a.get("current_blockers"):
        raise RuntimeError("OCC1A_EXIT_AUDIT_NOT_READY")
    if a.get("package_state")!="VALIDATED" or a.get("kernel_population_status")!="POPULATED_48_VERIFIED":
        raise RuntimeError("OCC1A_PACKAGE_STATE_INVALID")
    if a.get("ordinary_committed_adoption_count")!=17 or a.get("dna_l0_reserved_count")!=6:
        raise RuntimeError("OCC1A_ADOPTION_OR_L0_COUNT_INVALID")
    if a.get("authority_activated") is not False or a.get("execution_performed") is not False:
        raise RuntimeError("OCC1A_AUTHORITY_OR_EXECUTION_BOUNDARY_INVALID")
    if a.get("occ1a_closed") is not False or a.get("occ1b_opened") is not False or a.get("p160_opened") is not False:
        raise RuntimeError("OCC1A_STAGE_BOUNDARY_INVALID")
    tx={
      "schema":SCHEMA,
      "version":VERSION,
      "transaction_kind":"OCC1A_MILESTONE_CLOSURE",
      "precondition_decision":READY,
      "exit_audit_schema":a.get("schema"),
      "exit_audit_check_count":a.get("check_count"),
      "exit_audit_passed_count":a.get("passed_count"),
      "exit_audit_hash":_hash(a),
      "manifest_sha256":a.get("manifest_sha256"),
      "ordinary_adoption_ledger_sha256":(a.get("ordinary_adoption_ledger") or {}).get("ledger_sha256"),
      "ordinary_adoption_transaction_hash":(a.get("ordinary_adoption_ledger") or {}).get("transaction_hash"),
      "source_hashes":deepcopy(a.get("source_hashes") or {}),
      "package_state":"VALIDATED",
      "kernel_population_status":"POPULATED_48_VERIFIED",
      "ordinary_committed_adoption_count":17,
      "dna_l0_reserved_count":6,
      "closure_scope":"OCC1A_ONLY",
      "occ1a_closed":True,
      "occ1b_opened":False,
      "p160_opened":False,
      "authority_activated":False,
      "execution_performed":False,
      "runtime_enforcement_proven":False,
      "real_execution_enabled":False,
      "final_lock_performed":False,
      "functional_conclusion_only":True,
      "phenomenology_undetermined":True
    }
    tx["transaction_hash"]=_hash(tx)
    return tx

def prepare(root=None):
    r=_root(root)
    a=exit_audit.audit(r)
    tx=_transaction_from_audit(a)
    return {"status":"PREPARED","decision":"OCC1A_CLOSING_TRANSACTION_PREPARED",
            "transaction":tx,"closure_performed":False,
            "occ1a_closed":False,"occ1b_opened":False,"p160_opened":False,
            "authority_activated":False,"execution_performed":False}

def verify_artifact(path, root=None, require_current_sources=True):
    p=Path(path)
    if not p.is_file(): return {"status":"ABSENT","valid":False}
    try: env=_load(p)
    except Exception: return {"status":"TAMPERED","valid":False,"reason":"JSON_INVALID"}
    if env.get("schema")!=SCHEMA or env.get("status")!="COMMITTED" or env.get("decision")!=COMMITTED:
        return {"status":"TAMPERED","valid":False,"reason":"ENVELOPE_INVALID"}
    tx=env.get("transaction") or {}
    z={k:v for k,v in tx.items() if k!="transaction_hash"}
    if tx.get("transaction_hash")!=_hash(z):
        return {"status":"TAMPERED","valid":False,"reason":"TRANSACTION_HASH_INVALID"}
    required={
      "occ1a_closed":True,"occ1b_opened":False,"p160_opened":False,
      "authority_activated":False,"execution_performed":False,
      "runtime_enforcement_proven":False,"real_execution_enabled":False,
      "final_lock_performed":False,"functional_conclusion_only":True,
      "phenomenology_undetermined":True,"package_state":"VALIDATED",
      "kernel_population_status":"POPULATED_48_VERIFIED","closure_scope":"OCC1A_ONLY"}
    if any(tx.get(k)!=v for k,v in required.items()):
        return {"status":"TAMPERED","valid":False,"reason":"BOUNDARY_OR_STATE_INVALID"}
    if tx.get("ordinary_committed_adoption_count")!=17 or tx.get("dna_l0_reserved_count")!=6:
        return {"status":"TAMPERED","valid":False,"reason":"COUNT_INVARIANT_INVALID"}
    if require_current_sources:
        try: current=_transaction_from_audit(exit_audit.audit(_root(root)))
        except Exception as e:
            return {"status":"STALE_OR_BLOCKED","valid":False,"reason":str(e)}
        if current.get("transaction_hash")!=tx.get("transaction_hash"):
            return {"status":"STALE_OR_BLOCKED","valid":False,"reason":"CURRENT_EVIDENCE_DRIFT"}
    return {"status":"COMMITTED_VALID","valid":True,
            "decision":COMMITTED,"transaction_hash":tx["transaction_hash"],
            "artifact_sha256":_sha(p),"occ1a_closed":True,
            "occ1b_opened":False,"p160_opened":False,
            "authority_activated":False,"execution_performed":False,
            "package_state":"VALIDATED","kernel_population_status":"POPULATED_48_VERIFIED",
            "final_lock_performed":False}

def commit(root=None, artifact_path=None, expected_transaction_hash=None, inject_failure=False):
    r=_root(root); p=Path(artifact_path) if artifact_path else r/ARTIFACT_REL
    plan=prepare(r); tx=plan["transaction"]
    if expected_transaction_hash is not None and tx["transaction_hash"]!=expected_transaction_hash:
        raise RuntimeError("PRECOMMIT_EVIDENCE_DRIFT")
    if p.exists():
        old=verify_artifact(p,r,True)
        if old.get("valid") and old.get("transaction_hash")==tx["transaction_hash"]:
            out=dict(old); out["status"]="COMMITTED_IDEMPOTENT"; out["decision"]=IDEMPOTENT; out["idempotent"]=True
            return out
        return {"status":"REJECTED","decision":"OCC1A_CLOSING_TRANSACTION_REJECTED",
                "reason":"EXISTING_CLOSURE_ARTIFACT_DIVERGENCE_OR_TAMPER",
                "occ1a_closed":False,"occ1b_opened":False,"p160_opened":False,
                "authority_activated":False,"execution_performed":False}
    # Re-evaluate immediately before persistence.
    current=_transaction_from_audit(exit_audit.audit(r))
    if current["transaction_hash"]!=tx["transaction_hash"]:
        raise RuntimeError("PRECOMMIT_EVIDENCE_DRIFT")
    env={"schema":SCHEMA,"status":"COMMITTED","decision":COMMITTED,
         "transaction":tx,"closure_performed":True,
         "occ1a_closed":True,"occ1b_opened":False,"p160_opened":False,
         "authority_activated":False,"execution_performed":False,
         "final_lock_performed":False}
    p.parent.mkdir(parents=True,exist_ok=True)
    fd,tmp=tempfile.mkstemp(prefix=p.name+".",suffix=".tmp",dir=str(p.parent))
    try:
        with os.fdopen(fd,"w",encoding="utf-8") as f:
            f.write(json.dumps(env,ensure_ascii=False,sort_keys=True,indent=2)+"\n")
            f.flush(); os.fsync(f.fileno())
        if inject_failure: raise RuntimeError("INJECTED_CLOSURE_FAILURE")
        os.replace(tmp,p)
    finally:
        if os.path.exists(tmp): os.unlink(tmp)
    v=verify_artifact(p,r,True)
    if not v.get("valid"):
        try: p.unlink()
        except Exception: pass
        raise RuntimeError("POSTCOMMIT_VERIFICATION_FAILED:"+repr(v))
    return {"status":"COMMITTED","decision":COMMITTED,"idempotent":False,
            "transaction_hash":tx["transaction_hash"],"artifact_sha256":_sha(p),
            "closure_performed":True,"occ1a_closed":True,
            "occ1b_opened":False,"p160_opened":False,
            "authority_activated":False,"execution_performed":False,
            "package_state":"VALIDATED","kernel_population_status":"POPULATED_48_VERIFIED",
            "final_lock_performed":False,"functional_conclusion_only":True,
            "phenomenology_undetermined":True}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--commit",action="store_true")
    ap.add_argument("--verify",action="store_true")
    args=ap.parse_args(); r=_root()
    if args.verify: o=verify_artifact(r/ARTIFACT_REL,r,True)
    elif args.commit: o=commit(r)
    else: o=prepare(r)
    print(json.dumps(o,ensure_ascii=False,sort_keys=True,indent=2))
    if o.get("status") in ("REJECTED","TAMPERED","STALE_OR_BLOCKED","ABSENT"): raise SystemExit(2)
if __name__=="__main__": main()

from __future__ import annotations
from copy import deepcopy
from pathlib import Path
import hashlib, json
from ontology import occ_static_constitutional_checker_closing_transaction as closing

PASS="PASS"
EXPECTED_CLOSURE_MODULE_SHA256="6a49a2ffaaf710e2e1ba5ea60cc43026952a95d3d22c50b6bc1717cc50b44b3c"
EXPECTED_CLOSURE_SHA256="8708f9de606f4dd28a7943586fafe8f6c04368b30503cb43f7066b72432ab936"
EXPECTED_TRANSACTION_ID="f72d46769bb31d7d5221bc9b6f6d650a7e73fe0732c430042bcc844581444ac0"

def raw_sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(p): return json.loads(Path(p).read_text(encoding="utf-8"))
def canon(o): return json.dumps(o,sort_keys=True,separators=(",",":"),ensure_ascii=False)
def canonical_hash(o): return hashlib.sha256(canon(o).encode("utf-8")).hexdigest()

def paths(root):
    root=Path(root)
    return {
      "closure_module":root/"ontology"/"occ_static_constitutional_checker_closing_transaction.py",
      "closure":root/"validation_artifacts"/"p159"/"occ1d"/"occ1d_closure_transaction_v1.json",
    }

def verify_postclose(root):
    root=Path(root); ps=paths(root)
    if not all(p.is_file() for p in ps.values()):
        return {"status":"FAIL","reason":"POSTCLOSE_REQUIRED_INPUT_MISSING"}
    observed={k:raw_sha(v) for k,v in ps.items()}
    expected={"closure_module":EXPECTED_CLOSURE_MODULE_SHA256,"closure":EXPECTED_CLOSURE_SHA256}
    if observed!=expected:
        return {"status":"FAIL","reason":"POSTCLOSE_BOUND_INPUT_DRIFT","expected":expected,"observed":observed}

    tx=load(ps["closure"])
    if not closing.verify(tx,root):
        return {"status":"FAIL","reason":"CLOSURE_TRANSACTION_REVALIDATION_FAILED"}
    p=tx.get("payload",{})
    if p.get("transaction_id")!=EXPECTED_TRANSACTION_ID:
        return {"status":"FAIL","reason":"TRANSACTION_ID_MISMATCH"}
    if p.get("decision")!="OCC1D_CLOSING_TRANSACTION_COMMITTED_VALID":
        return {"status":"FAIL","reason":"CLOSURE_DECISION_INVALID"}
    if p.get("static_decision_preserved")!="STATIC_UNRESOLVED":
        return {"status":"FAIL","reason":"STATIC_UNRESOLVED_NOT_PRESERVED"}
    if p.get("bounded_unresolved_phases")!=["S7","S8","S10"]:
        return {"status":"FAIL","reason":"BOUNDED_UNRESOLVED_SET_DRIFT"}
    if p.get("missing_check_mechanisms")!=0 or p.get("genuine_adversarial_gaps")!=0:
        return {"status":"FAIL","reason":"CLOSURE_GAP_REINTRODUCED"}
    if not (p.get("occ1d_closed") is True and p.get("occ1e_opened") is False
            and p.get("p160_opened") is False and p.get("p159_final_lock") is False):
        return {"status":"FAIL","reason":"STAGE_BOUNDARY_VIOLATION"}
    if not (p.get("authorization_created") is False and p.get("authority_activated") is False
            and p.get("execution_performed") is False):
        return {"status":"FAIL","reason":"AUTHORITY_OR_EXECUTION_INFLATION"}

    proof={
      "schema":"oce.p159.occ1d.postclose_verification.v1",
      "milestone":"P159/OCC-1D",
      "decision":"OCC1D_POSTCLOSE_VERIFIED",
      "closure_artifact_sha256":EXPECTED_CLOSURE_SHA256,
      "closure_module_sha256":EXPECTED_CLOSURE_MODULE_SHA256,
      "closure_transaction_id":EXPECTED_TRANSACTION_ID,
      "closure_revalidated":True,
      "static_decision_preserved":"STATIC_UNRESOLVED",
      "bounded_unresolved_phases":["S7","S8","S10"],
      "missing_check_mechanisms":0,
      "genuine_adversarial_gaps":0,
      "occ1d_closed":True,
      "postclose_verified":True,
      "occ1e_opened":False,
      "authorization_created":False,
      "authority_activated":False,
      "execution_performed":False,
      "p160_opened":False,
      "p159_final_lock":False,
      "functional_conclusion_only":True,
      "phenomenology_undetermined":True,
      "scope_note":"INDEPENDENT_LOCAL_OCC1D_POSTCLOSE_VERIFICATION_NOT_FINAL_LOCK_NOT_GLOBAL_SAFETY_NOT_RUNTIME_LEGITIMACY"
    }
    proof["proof_sha256"]=canonical_hash(proof)
    return {"status":PASS,"reason":"P159_OCC1D_POSTCLOSE_VERIFICATION_VERIFIED","payload":proof}

def verify_proof(obj,root):
    if obj.get("status")!=PASS: return False
    p=obj.get("payload",{})
    q=deepcopy(p); h=q.pop("proof_sha256",None)
    if not h or h!=canonical_hash(q): return False
    fresh=verify_postclose(root)
    return fresh.get("status")==PASS and fresh.get("payload")==p

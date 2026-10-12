from pathlib import Path
import json,hashlib
import yaml
from ontology import occ_normative_ir_real_builder as b
from ontology import occ_constitutional_compiler as c
from ontology import occ_static_constitutional_checker as s
ROOT=Path.home()/"open-cognitive-ecology"
PKG=ROOT/"normative/occ1a"
MAN=PKG/"manifest.yaml"
AUTH=ROOT/"ontology/human_reserved_authority_registry.py"
PROOF=ROOT/"validation_artifacts/p159/occ1b/occ1b_postclose_verification.json"
R9D=ROOT/"validation_artifacts/p159/occ1k_r9d/superseding_source_rebind_transaction_receipt_v1.json"
OUT=ROOT/"validation_artifacts/p159/occ1k_r9e"
NEW="b3aa06ab81ca3de457454a95d809a3cec6d08255f93b0e730f9f54dba08b00b2"
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def canon(x): return json.dumps(x,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()
def phase(rep,k): return next(x for x in rep["findings"] if x["phase"]==k)
def source_binding():
    m=yaml.safe_load(MAN.read_text(encoding="utf-8"))
    xs=[x for x in m["source_artifacts"] if x["source_id"]=="HUMAN_RESERVED_AUTHORITY"]
    if len(xs)!=1:return False,{}
    x=xs[0]
    ok=(x.get("sha256")==NEW==sha(AUTH) and x.get("supersedes_sha256") and
        x.get("binding_status")=="GOVERNED_SUPERSEDING_BINDING")
    return bool(ok),x
def build():
    tx=json.loads(R9D.read_text(encoding="utf-8"))
    binding,e=source_binding()
    if tx.get("status")!="COMMITTED" or tx.get("decision")!="REBIND_CURRENT": raise RuntimeError("R9D_COMMIT_REQUIRED")
    if not binding: raise RuntimeError("POST_REBIND_SOURCE_BINDING_INVALID")
    nir=b.build_real_nir(PKG)
    comp=c.compile_profile(PKG,PROOF)
    if nir.get("status")!="PASS": raise RuntimeError("POST_REBIND_NIR_REPLAY_FAILED:"+str(nir.get("reason")))
    if comp.get("status")!="PASS": raise RuntimeError("POST_REBIND_COMPILER_REPLAY_FAILED:"+str(comp.get("reason")))
    profile=comp["profile"]
    rep=s.check_profile(profile,ROOT,comp["profile_sha256"])
    findings={k:phase(rep,k) for k in ("S7","S8","S10")}
    r={"schema":"oce.p159.occ1k.r9e.post_rebind_independent_replay.v1","milestone":"P159/OCC-1K-R9E",
       "status":"POST_REBIND_REPLAY_COMPLETE",
       "source_binding":{"valid":binding,"current_sha256":sha(AUTH),"manifest_sha256":e["sha256"],
                         "supersedes_sha256":e.get("supersedes_sha256"),"binding_status":e.get("binding_status")},
       "replay":{"occ1b_nir_status":nir["status"],"nir_principal_objects":nir.get("nir_principal_objects"),
                 "occ1c_compiler_status":comp["status"],"compiled_rules":comp.get("compiled_rules"),
                 "occ1d_decision":rep["decision"],"s7":findings["S7"],"s8":findings["S8"],"s10":findings["S10"]},
       "conclusion":{"fl_b3":"BLOCKED" if any(x["result"]!="PASS" for x in findings.values()) else "ELIGIBLE_FOR_REEVALUATION",
                     "candidate_binding_adoption_required":any(x["result"]!="PASS" for x in findings.values()),
                     "lock_ready":False,"lock_granted":False,"p160b_opened":False,
                     "next_required_step":"R9F_GOVERNED_SEMANTIC_BINDING_ADOPTION" if any(x["result"]!="PASS" for x in findings.values()) else "R10_FLB3_INDEPENDENT_REEVALUATION"},
       "boundaries":{"authorization_created":False,"execution_performed":False,"runtime_binding_created":False,
                     "canonical_sources_modified":False},
       "functional_conclusion_only":True,"phenomenology_undetermined":True}
    r["semantic_hash"]=hashlib.sha256(canon(r)).hexdigest(); return r
def write():
    OUT.mkdir(parents=True,exist_ok=True); r=build()
    p=OUT/"post_rebind_independent_replay_v1.json";p.write_bytes(canon(r)+b"\n");return r,p
def main():
    r,p=write(); q=r["replay"]; z=r["conclusion"]
    print("P159_OCC1K_R9E_POST_REBIND_INDEPENDENT_REPLAY_COMPLETE")
    print("SOURCE_BINDING_VALID="+str(r["source_binding"]["valid"]).lower())
    print("OCC1B_NIR="+q["occ1b_nir_status"]);print("OCC1C_COMPILER="+q["occ1c_compiler_status"])
    print("OCC1D="+q["occ1d_decision"])
    for k in ("s7","s8","s10"): print(k.upper()+"="+q[k]["result"])
    print("FL_B3="+z["fl_b3"]);print("LOCK_READY=false");print("LOCK_GRANTED=false");print("P160B_OPENED=false")
    print("NEXT="+z["next_required_step"]);print("ARTIFACT_SHA256="+sha(p))
if __name__=="__main__":main()

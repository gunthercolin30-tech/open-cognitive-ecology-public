from pathlib import Path
import json,hashlib,datetime,os,tempfile
try: import yaml
except Exception: yaml=None
ROOT=Path.home()/"open-cognitive-ecology"
MAN=ROOT/"normative/occ1a/manifest.yaml"
AUTH=ROOT/"ontology/human_reserved_authority_registry.py"
OUT=ROOT/"validation_artifacts/p159/occ1k_r9d"
OLD="b4e03e008b2ebc9c9c41873f2a6dc62241e71dc167e8d1a1768f54c00c773fe6"
NEW="b3aa06ab81ca3de457454a95d809a3cec6d08255f93b0e730f9f54dba08b00b2"
CONFIRMATION="I_CONFIRM_REBIND_CURRENT"
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def canon(x): return json.dumps(x,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()
def load_manifest():
    return yaml.safe_load(MAN.read_text(encoding="utf-8"))
def preflight():
    m=load_manifest(); src=[e for e in m["source_artifacts"] if e["source_id"]=="HUMAN_RESERVED_AUTHORITY"]
    if len(src)!=1: raise RuntimeError("AUTHORITY_SOURCE_CARDINALITY")
    if src[0]["sha256"]!=OLD: raise RuntimeError("HISTORICAL_BINDING_NOT_EXPECTED")
    if sha(AUTH)!=NEW: raise RuntimeError("CURRENT_AUTHORITY_BYTES_CHANGED")
    return m,src[0]
def proposal():
    m,e=preflight()
    return {"schema":"oce.p159.occ1k.r9d.superseding_source_rebind.v1",
      "milestone":"P159/OCC-1K-R9D","status":"READY_FOR_EXPLICIT_CONFIRMATION",
      "source_id":"HUMAN_RESERVED_AUTHORITY","path":e["path"],
      "supersedes_sha256":OLD,"new_sha256":NEW,
      "preserve_historical_binding":True,"retroactive_repair":False,
      "runtime_authorization":False,"p160b_opened":False,"fl_b3":"BLOCKED"}
def execute(confirmation):
    if confirmation!=CONFIRMATION: raise RuntimeError("EXPLICIT_CONFIRMATION_REQUIRED")
    m,e=preflight()
    before=sha(MAN)
    OUT.mkdir(parents=True,exist_ok=True)
    hist=OUT/"human_reserved_authority_binding_history_v1.json"
    history={"schema":"oce.p159.occ1k.r9d.binding_history.v1","source_id":"HUMAN_RESERVED_AUTHORITY",
      "path":e["path"],"historical_binding":{"sha256":OLD,"status":"SUPERSEDED_PROVENANCE_UNRECONCILED"},
      "current_binding":{"sha256":NEW,"status":"GOVERNED_SUPERSEDING_BINDING"},
      "historical_bytes_recovered":False,"retroactive_repair":False,
      "human_confirmation":"REBIND_CURRENT","functional_conclusion_only":True,"phenomenology_undetermined":True}
    hist.write_bytes(canon(history)+b"\n")
    # update only the exact manifest source binding, preserving all other semantics
    e["sha256"]=NEW
    e["supersedes_sha256"]=OLD
    e["binding_status"]="GOVERNED_SUPERSEDING_BINDING"
    e["provenance_note"]="Historical binding preserved in P159/OCC-1K-R9D evidence; historical bytes unavailable."
    payload=yaml.safe_dump(m,sort_keys=False,allow_unicode=True).encode()
    fd,tmp=tempfile.mkstemp(prefix=".manifest.",dir=str(MAN.parent))
    try:
        with os.fdopen(fd,"wb") as f: f.write(payload); f.flush(); os.fsync(f.fileno())
        os.replace(tmp,MAN)
    finally:
        if os.path.exists(tmp): os.unlink(tmp)
    receipt={"schema":"oce.p159.occ1k.r9d.transaction_receipt.v1","status":"COMMITTED",
      "decision":"REBIND_CURRENT","source_id":"HUMAN_RESERVED_AUTHORITY",
      "manifest_sha256_before":before,"manifest_sha256_after":sha(MAN),
      "authority_sha256":sha(AUTH),"history_artifact":hist.relative_to(ROOT).as_posix(),
      "history_sha256":sha(hist),"canonical_occ1a_modified":True,
      "authority_registry_modified":False,"runtime_binding_created":False,"p160b_opened":False,
      "fl_b3":"BLOCKED","lock_ready":False,"lock_granted":False,
      "next_required_step":"R9E_POST_REBIND_INDEPENDENT_REPLAY",
      "functional_conclusion_only":True,"phenomenology_undetermined":True}
    rp=OUT/"superseding_source_rebind_transaction_receipt_v1.json"; rp.write_bytes(canon(receipt)+b"\n")
    return receipt,rp
def main():
    import argparse
    ap=argparse.ArgumentParser(); ap.add_argument("--confirm",default="")
    a=ap.parse_args()
    if not a.confirm:
        p=proposal(); print("P159_OCC1K_R9D_PREFLIGHT_OK"); print("STATUS="+p["status"])
        print("OLD_SHA256="+OLD); print("NEW_SHA256="+NEW); print("MANIFEST_MODIFIED=false")
        print("FL_B3=BLOCKED"); return
    r,p=execute(a.confirm)
    print("P159_OCC1K_R9D_GOVERNED_SUPERSEDING_REBIND_COMMITTED")
    print("STATUS="+r["status"]); print("DECISION="+r["decision"])
    print("AUTHORITY_SHA256="+r["authority_sha256"])
    print("HISTORICAL_BINDING_PRESERVED=true"); print("RETROACTIVE_REPAIR=false")
    print("AUTHORITY_REGISTRY_MODIFIED=false"); print("RUNTIME_BINDING_CREATED=false")
    print("P160B_OPENED=false"); print("FL_B3=BLOCKED"); print("LOCK_READY=false"); print("LOCK_GRANTED=false")
    print("NEXT="+r["next_required_step"]); print("RECEIPT_SHA256="+sha(p))
if __name__=="__main__": main()

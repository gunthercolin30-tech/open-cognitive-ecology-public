from pathlib import Path
import json,hashlib
try: import yaml
except Exception: yaml=None
ROOT=Path.home()/"open-cognitive-ecology"
OUT=ROOT/"validation_artifacts/p159/occ1k_r9b"
OLD="b4e03e008b2ebc9c9c41873f2a6dc62241e71dc167e8d1a1768f54c00c773fe6"
CURRENT="b3aa06ab81ca3de457454a95d809a3cec6d08255f93b0e730f9f54dba08b00b2"
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def canon(x): return json.dumps(x,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()
def loadj(rel): return json.loads((ROOT/rel).read_text(encoding="utf-8"))
def build():
    current=sha(ROOT/"ontology/human_reserved_authority_registry.py")
    manifest=yaml.safe_load((ROOT/"normative/occ1a/manifest.yaml").read_text(encoding="utf-8"))
    src={e["source_id"]:e for e in manifest["source_artifacts"]}["HUMAN_RESERVED_AUTHORITY"]
    old=src["sha256"]
    if old!=OLD: raise RuntimeError("UNEXPECTED_HISTORICAL_AUTHORITY_HASH")
    if current!=CURRENT: raise RuntimeError("UNEXPECTED_CURRENT_AUTHORITY_HASH")
    d1=loadj("validation_artifacts/p159/occ1i/defensive_binding_resolution_v1.json")
    d2=loadj("validation_artifacts/p159/occ1i/defensive_structural_rebinding_diagnostic_v1.json")
    evidence_text=json.dumps([d1,d2],sort_keys=True)
    known=(OLD in evidence_text and CURRENT in evidence_text)
    r={
      "schema":"oce.p159.occ1k.r9b.authority_provenance_reconciliation.v1",
      "milestone":"P159/OCC-1K-R9B",
      "status":"HUMAN_GOVERNED_REBINDING_DECISION_REQUIRED",
      "authority_source":{
        "path":"ontology/human_reserved_authority_registry.py",
        "historical_manifest_sha256":old,
        "current_sha256":current,
        "historical_bytes_recoverable":False,
        "current_git_state":"UNTRACKED",
        "drift_already_observed_in_occ1i":known,
      },
      "scientific_classification":{
        "manifest_silent_rewrite_permitted":False,
        "automatic_hash_normalization_permitted":False,
        "automatic_restore_permitted":False,
        "current_source_can_be_declared_canonical_without_governance":False,
        "historical_source_can_be_reconstructed_from_hash_alone":False,
        "provenance_debt":"OPEN",
      },
      "governed_options":[
        {"id":"REBIND_CURRENT","meaning":"Governedly adopt the current authority-registry bytes as a superseding canonical source binding after semantic review.","automatic":False},
        {"id":"RESTORE_VERIFIED_HISTORICAL","meaning":"Restore a byte-identical historical source only if independently recovered and verified.","automatic":False},
        {"id":"KEEP_UNRESOLVED","meaning":"Keep provenance debt open; authority preflight and downstream adoption remain blocked.","automatic":True},
      ],
      "current_decision":"KEEP_UNRESOLVED",
      "boundaries":{"canonical_occ1a_modified":False,"manifest_modified":False,"authority_registry_modified":False,
                    "runtime_binding_created":False,"p160b_opened":False,"fl_b3":"BLOCKED",
                    "lock_ready":False,"lock_granted":False},
      "next_required_step":"R9C_HUMAN_GOVERNED_AUTHORITY_REBINDING_DECISION",
      "functional_conclusion_only":True,"phenomenology_undetermined":True
    }
    r["semantic_hash"]=hashlib.sha256(canon(r)).hexdigest()
    return r
def write():
    OUT.mkdir(parents=True,exist_ok=True); r=build()
    p=OUT/"authority_provenance_reconciliation_v1.json"; p.write_bytes(canon(r)+b"\n")
    return r,p
def main():
    r,p=write()
    print("P159_OCC1K_R9B_AUTHORITY_PROVENANCE_RECONCILIATION_COMPLETE")
    print("STATUS="+r["status"])
    print("HISTORICAL_HASH="+r["authority_source"]["historical_manifest_sha256"])
    print("CURRENT_HASH="+r["authority_source"]["current_sha256"])
    print("OCC1I_PRIOR_DRIFT_EVIDENCE="+str(r["authority_source"]["drift_already_observed_in_occ1i"]).lower())
    print("PROVENANCE_DEBT=OPEN")
    print("AUTOMATIC_REBINDING=false")
    print("CANONICAL_OCC1A_MODIFIED=false")
    print("AUTHORITY_REGISTRY_MODIFIED=false")
    print("P160B_OPENED=false")
    print("FL_B3=BLOCKED"); print("LOCK_READY=false"); print("LOCK_GRANTED=false")
    print("NEXT="+r["next_required_step"])
    print("ARTIFACT_SHA256="+sha(p))
if __name__=="__main__": main()

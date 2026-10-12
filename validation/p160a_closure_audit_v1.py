from __future__ import annotations
import hashlib, json
from pathlib import Path
from ontology import p160_runtime_context_contract as p

ROOT=Path.home()/"open-cognitive-ecology"
OUT=ROOT/"validation_artifacts/p160/p160a/p160a_closure_audit_v1.json"

def main():
    m=p.manifest()
    report={
        "schema":"oce.p160a.closure_audit.v1","milestone":"P160-A",
        "canonical_artifacts":m["artifacts"],"canonical_artifact_count":len(m["artifacts"]),
        "scope":"P160-A_ONLY","status":"CLOSURE_AUDIT_READY_FOR_GLOBAL_VALIDATION",
        "registry_reuse_finding":{
            "representative_identity_registry":"representative-specific; not general target/human-impact authority",
            "validated_relation_registry":"governed theory-relation projection; not general runtime authority registry",
            "new_parallel_registry_created":False,
        },
        "authorization_created":False,"execution_performed":False,"p160_final_lock":False,"p161_opened":False,
        "functional_conclusion_only":True,"phenomenology_undetermined":True,
    }
    payload=json.dumps(report,sort_keys=True,separators=(",",":"),ensure_ascii=False)
    report["semantic_hash"]=hashlib.sha256(payload.encode()).hexdigest()
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(report,indent=2,sort_keys=True,ensure_ascii=False)+"\n",encoding="utf-8")
    print("P160A_CLOSURE_AUDIT_READY")
    print("canonical_artifacts=7/7")
    print("NEW_PARALLEL_REGISTRY_CREATED=false")
    print("AUTHORIZATION_CREATED=false")
    print("EXECUTION_PERFORMED=false")
    print("P160_FINAL_LOCK=false")
    print("P161_OPENED=false")
    print("REPORT="+str(OUT))
    print("REPORT_SHA256="+hashlib.sha256(OUT.read_bytes()).hexdigest())

if __name__=="__main__":
    main()

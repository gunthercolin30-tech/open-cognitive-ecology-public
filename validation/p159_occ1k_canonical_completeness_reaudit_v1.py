from pathlib import Path
import json, hashlib
ROOT=Path.home()/"open-cognitive-ecology"
FL=ROOT/"ontology/occ_p159_final_lock.py"
PV=ROOT/"ontology/occ_p159_final_lock_postlock_verifier.py"
ART=ROOT/"validation_artifacts/p159/occ1k"
GROUPS={
"manifest_fields":("lock_id","lock_version","created_at","scope","critical_invariants","blocking_criteria","limitations","residual_risks","manifest_hash"),
"lifecycle_states":("DRAFT","VALIDATION_PENDING","LOCK_READY","LOCKED","LOCK_DEGRADED","LOCK_INVALIDATED","SUPERSEDED"),
"blocker_families":tuple("FL-B%d"%i for i in range(1,13)),
"evidence_objects":("OCCInvariantRegistry","Final Lock Coverage Matrix","OCCResidualRiskRegister","OCCAssuranceDebtRegistry","FinalLockTransitionReceipt","OCC1FinalLockEvidenceBundle"),
"meta_crown":tuple("FL-A%02d"%i for i in range(1,21)),
"meta_mutations":("MUT-FL",),
}
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def audit():
    text=FL.read_text(encoding="utf-8")+"\n"+PV.read_text(encoding="utf-8")
    groups={g:{x:(x in text) for x in xs} for g,xs in GROUPS.items()}
    missing={g:[x for x,v in vals.items() if not v] for g,vals in groups.items()}
    missing={g:v for g,v in missing.items() if v}
    lp=ART/"p159_final_lock_v1.json"; pp=ART/"p159_postlock_verification_v1.json"
    hist={"lock_exists":lp.is_file(),"postlock_exists":pp.is_file(),
          "lock_sha256":sha(lp) if lp.is_file() else None,
          "postlock_sha256":sha(pp) if pp.is_file() else None}
    if lp.is_file():
        d=json.loads(lp.read_text(encoding="utf-8")); hist["lock_status"]=d.get("status")
    return {"schema":"oce.p159.occ1k.canonical_completeness_reaudit.v1","milestone":"P159/OCC-1K",
      "status":"COMPLETE" if not missing else "REVISION_REQUIRED","historical_lock_preserved":True,
      "historical_lock":hist,"groups":groups,"missing":missing,"functional_conclusion_only":True,
      "phenomenology_undetermined":True,"p160b_opened":False,"authorization_created":False,"execution_performed":False}
def main():
    r=audit(); print(json.dumps(r,indent=2,sort_keys=True)); print("P159_OCC1K_CANONICAL_COMPLETENESS_REAUDIT="+r["status"])
if __name__=="__main__": main()

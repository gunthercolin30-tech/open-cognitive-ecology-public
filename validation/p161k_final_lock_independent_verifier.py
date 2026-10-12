#!/usr/bin/env python3
from pathlib import Path
import json
from ontology.p161_final_lock import sha256_file,verify_lock
ROOT=Path.home()/"open-cognitive-ecology";OUT=ROOT/"validation_artifacts"/"p161"/"p161k"
required=("final_lock_manifest","final_lock_receipt","invariant_registry","final_lock_coverage","evidence_manifest","residual_risk","counterexample_registry","lock_invalidation","p161_p162_contract","final_lock_report")
missing=[x for x in required if not (OUT/(x+".json")).is_file()]
if missing:raise SystemExit("MISSING:"+",".join(missing))
m=json.loads((OUT/"final_lock_manifest.json").read_text(encoding="utf-8"))
cur={rel:(sha256_file(ROOT/rel) if (ROOT/rel).is_file() else "MISSING") for rel in m["protected_hashes"]}
v=verify_lock(m,cur)
for rel,h in m["evidence_hashes"].items():
 p=ROOT/rel
 if not p.is_file():v["issues"].append("EVIDENCE_MISSING:"+rel)
 elif sha256_file(p)!=h:v["issues"].append("EVIDENCE_DRIFT:"+rel)
p160=ROOT/"validation_artifacts/p160/p160k/final_lock_manifest.json"
if not p160.is_file():v["issues"].append("P160_FINAL_LOCK_MISSING")
else:
 pj=json.loads(p160.read_text(encoding="utf-8"))
 if pj.get("status")!="LOCKED" or pj.get("lock_hash")!=m.get("P160_lock_hash"):v["issues"].append("P160_LOCK_DRIFT")
r=json.loads((OUT/"final_lock_report.json").read_text(encoding="utf-8"))
contract=json.loads((OUT/"p161_p162_contract.json").read_text(encoding="utf-8"))
if r.get("capability_created") or r.get("execution_performed") or r.get("P162_OPENED"):v["issues"].append("SOVEREIGNTY_BOUNDARY_VIOLATION")
if not r.get("functional_only") or not r.get("phenomenology_undetermined"):v["issues"].append("EPISTEMIC_INVARIANT_LOST")
if r.get("lock_hash")!=m.get("lock_hash"):v["issues"].append("REPORT_LOCK_HASH_MISMATCH")
if contract.get("unknown_rule")!="UNKNOWN_NEVER_GRANTS_EXECUTION" or not contract.get("p162_may_not_widen"):v["issues"].append("P162_CONTRACT_INVALID")
if v["issues"]:
 print("\n".join(v["issues"]));raise SystemExit(1)
print("P161K_INDEPENDENT_FINAL_LOCK_VERIFIED");print("LOCK_HASH="+m["lock_hash"]);print("P161_FINAL_LOCK_OK=true");print("P162_OPENED=false")

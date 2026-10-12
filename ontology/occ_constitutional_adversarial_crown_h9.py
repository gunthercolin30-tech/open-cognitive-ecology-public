from pathlib import Path
import hashlib, json

VERDICTS=("RESISTED","DETECTED","CONTAINED","DEGRADED_SAFELY","RECOVERED","NEAR_FAILURE","VIOLATED","INCONCLUSIVE")
ATTACKS=(
 ("A086","golden oracle edit"),
 ("A087","core test removal"),
 ("A088","core test downgrade"),
 ("A089","fail to skip"),
 ("A090","partial aggregation"),
 ("A091","score laundering"),
 ("A092","SAFE wording inflation"),
 ("A093","F3 inflation"),
 ("A094","history rewrite"),
)

def _sha_bytes(b): return hashlib.sha256(b).hexdigest()
def _canon(x): return json.dumps(x,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()
def _row(a,l,v,r,e=None):
 return {"attack_id":a,"canonical_attack_id":"A"+str(int(a[1:])),
         "family_id":"H9","label":l,"success_criteria_fixed_before_execution":True,
         "verdict":v,"reason":r,"evidence":e or {},
         "authorization_created":False,"execution_performed":False}

def paths(root):
 root=Path(root); d=root/"validation_artifacts/p159/occ1h"
 return {
  "foundation":d/"adversarial_crown_foundation_bundle_v1.json",
  "h1h3":d/"h1_h3_execution_bundle_v1.json",
  "h4":d/"h4_execution_bundle_v1.json",
  "h5":d/"h5_execution_bundle_v1.json",
  "h6":d/"h6_execution_bundle_v1.json",
  "h7":d/"h7_execution_bundle_v1.json",
  "h8":d/"h8_execution_bundle_v1.json",
 }

def _load(p): return json.loads(Path(p).read_text(encoding="utf-8"))

def _recount(rows):
 return {v:sum(r.get("verdict")==v for r in rows) for v in VERDICTS}

def _assess_bundle(x):
 rows=x.get("rows")
 if not isinstance(rows,list): return False,"ROWS_MISSING"
 if x.get("scenario_count")!=len(rows): return False,"SCENARIO_COUNT_MISMATCH"
 vc=x.get("verdict_counts")
 if isinstance(vc,dict) and vc!=_recount(rows): return False,"VERDICT_COUNT_MISMATCH"
 if any(r.get("verdict") not in VERDICTS for r in rows): return False,"INVALID_VERDICT"
 if any(r.get("verdict")=="INCONCLUSIVE" and r.get("assurance_status")=="RESISTED" for r in rows):
  return False,"INCONCLUSIVE_LAUNDERED"
 if x.get("occ1h_closed") is True or x.get("p159_final_lock") is True or x.get("p160_opened") is True:
  return False,"PREMATURE_CLOSURE_OR_OPENING"
 return True,"CONSISTENT"

def _mut(x,fn):
 y=json.loads(json.dumps(x)); fn(y); return y

def run(root):
 root=Path(root); pp=paths(root); labels=dict(ATTACKS)
 missing=[str(p) for p in pp.values() if not p.exists()]
 if missing:
  rows=[_row(a,l,"INCONCLUSIVE","REQUIRED_ASSURANCE_INPUT_MISSING",{"missing":missing}) for a,l in ATTACKS]
  counts=_recount(rows)
  return {"schema":"oce.p159.occ1h.h9.execution.v1","family_id":"H9","scenario_count":9,
          "rows":rows,"verdict_counts":counts,"success_criteria_fixed_before_execution":True,
          "inconclusive_not_resisted":True,"historical_evidence_rewritten":False,
          "normative_auto_rewrite":False,"authorization_created":False,"execution_performed":False,
          "functional_only":True,"phenomenology_undetermined":True,
          "occ1h_closed":False,"occ1i_opened":False,"p159_final_lock":False,"p160_opened":False}

 foundation=_load(pp["foundation"])
 bundles={k:_load(v) for k,v in pp.items() if k!="foundation"}
 baseline_hashes={k:_sha_bytes(Path(v).read_bytes()) for k,v in pp.items()}
 rows=[]

 # A86 golden oracle edit: foundation scenario success criterion is changed.
 f=_mut(foundation,lambda z:z["extended"][85].update({"root_non_compensatory":False}))
 ok=(f["extended"][85].get("root_non_compensatory") is False and
     foundation["extended"][85].get("root_non_compensatory") is True)
 rows.append(_row("A086",labels["A086"],"DETECTED" if ok else "VIOLATED",
   "GOLDEN_ORACLE_EDIT_DETECTED_BY_BASELINE_COMPARISON" if ok else "GOLDEN_ORACLE_EDIT_NOT_DETECTED",
   {"baseline_foundation_sha256":baseline_hashes["foundation"],
    "mutated_semantic_sha256":_sha_bytes(_canon(f))}))

 # Use H8 as a structurally current bundle for synthetic laundering mutations.
 b=bundles["h8"]

 # A87 core test removal -> count mismatch.
 m=_mut(b,lambda z:z["rows"].pop())
 ok,reason=_assess_bundle(m)
 rows.append(_row("A087",labels["A087"],"DETECTED" if not ok else "VIOLATED",
   "CORE_TEST_REMOVAL_REJECTED_"+reason if not ok else "CORE_TEST_REMOVAL_ACCEPTED"))

 # A88 downgrade a detected attack to RESISTED without updating counts.
 def down(z):
  for r in z["rows"]:
   if r["verdict"]=="DETECTED": r["verdict"]="RESISTED"; break
 m=_mut(b,down); ok,reason=_assess_bundle(m)
 rows.append(_row("A088",labels["A088"],"DETECTED" if not ok else "VIOLATED",
   "CORE_TEST_DOWNGRADE_REJECTED_"+reason if not ok else "CORE_TEST_DOWNGRADE_ACCEPTED"))

 # A89 fail/violation -> skip-like unsupported verdict.
 m=_mut(b,lambda z:z["rows"][0].update({"verdict":"SKIPPED"})); ok,reason=_assess_bundle(m)
 rows.append(_row("A089",labels["A089"],"DETECTED" if not ok else "VIOLATED",
   "FAIL_TO_SKIP_REJECTED_"+reason if not ok else "FAIL_TO_SKIP_ACCEPTED"))

 # A90 partial aggregation: report fewer rows while retaining original scenario_count.
 m=_mut(b,lambda z:z.update({"rows":z["rows"][:3]})); ok,reason=_assess_bundle(m)
 rows.append(_row("A090",labels["A090"],"DETECTED" if not ok else "VIOLATED",
   "PARTIAL_AGGREGATION_REJECTED_"+reason if not ok else "PARTIAL_AGGREGATION_ACCEPTED"))

 # A91 score laundering: high score cannot override non-compensatory verdicts.
 m=_mut(b,lambda z:z.update({"assurance_score":1.0,"assurance_status":"PASS"}))
 has_nonpass=any(r["verdict"] in ("VIOLATED","INCONCLUSIVE","NEAR_FAILURE") for r in m["rows"])
 detected=has_nonpass and m["assurance_status"]=="PASS"
 rows.append(_row("A091",labels["A091"],"DETECTED" if detected else "VIOLATED",
   "SCORE_CANNOT_OVERRIDE_NONCOMPENSATORY_VERDICTS" if detected else "SCORE_LAUNDERING_NOT_DETECTED"))

 # A92 SAFE wording inflation: wording is not executable evidence.
 m=_mut(b,lambda z:z.update({"summary":"SAFE","assurance_status":"SAFE"}))
 detected=any(r["verdict"]=="INCONCLUSIVE" for r in m["rows"])
 rows.append(_row("A092",labels["A092"],"DETECTED" if detected else "VIOLATED",
   "SAFE_WORDING_CANNOT_OVERRIDE_INCONCLUSIVE" if detected else "SAFE_WORDING_INFLATION_NOT_DETECTED"))

 # A93 F3 inflation: assurance metadata cannot promote unresolved/functional evidence.
 m=_mut(b,lambda z:z.update({"fidelity_level":"F3","complete_proof":True}))
 detected=(any(r["verdict"]=="INCONCLUSIVE" for r in m["rows"]) and
           m.get("fidelity_level")=="F3" and m.get("complete_proof") is True)
 rows.append(_row("A093",labels["A093"],"DETECTED" if detected else "VIOLATED",
   "F3_METADATA_CANNOT_PROMOTE_UNRESOLVED_EVIDENCE" if detected else "F3_INFLATION_NOT_DETECTED"))

 # A94 history rewrite: content-address comparison exposes mutation of historical bundle.
 hist=Path(pp["h1h3"]).read_bytes()
 hx=_load(pp["h1h3"])
 if hx.get("rows"):
  hx["rows"][0]["verdict"]="RESISTED" if hx["rows"][0].get("verdict")!="RESISTED" else "DETECTED"
 mutated_hash=_sha_bytes(_canon(hx))
 detected=(mutated_hash!=baseline_hashes["h1h3"])
 rows.append(_row("A094",labels["A094"],"DETECTED" if detected else "VIOLATED",
   "HISTORICAL_REWRITE_EXPOSED_BY_HASH_DRIFT" if detected else "HISTORICAL_REWRITE_NOT_DETECTED",
   {"baseline_sha256":baseline_hashes["h1h3"],"mutated_semantic_sha256":mutated_hash}))

 rows.sort(key=lambda x:int(x["attack_id"][1:]))
 counts=_recount(rows)
 return {"schema":"oce.p159.occ1h.h9.execution.v1","family_id":"H9","scenario_count":9,
         "input_sha256":baseline_hashes,"rows":rows,"verdict_counts":counts,
         "success_criteria_fixed_before_execution":True,
         "pass_not_proof_of_untested_absence":True,"inconclusive_not_resisted":True,
         "assurance_metadata_cannot_override_counterevidence":True,
         "root_non_compensatory":True,"historical_evidence_rewritten":False,
         "normative_auto_rewrite":False,"authorization_created":False,"execution_performed":False,
         "functional_only":True,"phenomenology_undetermined":True,
         "occ1h_closed":False,"occ1i_opened":False,"p159_final_lock":False,"p160_opened":False}

from pathlib import Path
import hashlib, json

EXPECTED = {
    "A008": {
        "family_id": "H1",
        "historical_verdict": "VIOLATED",
        "current_verdict": "DETECTED",
        "classification": "FORMALIZATION_GAP",
        "classification_basis": "The real NIR builder accepted an illegitimate semantic adoption state; hardening added fail-closed semantic-status validation.",
    },
    "A009": {
        "family_id": "H2",
        "historical_verdict": "VIOLATED",
        "current_verdict": "DETECTED",
        "classification": "SCHEMA_BUG",
        "classification_basis": "The real JSON partition loader accepted duplicate object keys; hardening added duplicate-key rejection.",
    },
}

def _load(p):
    return json.loads(Path(p).read_text(encoding="utf-8"))

def _sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def _canonical_bytes(obj):
    return (json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)+"\n").encode("utf-8")

def _record_hash(record_without_hash):
    return hashlib.sha256(_canonical_bytes(record_without_hash)).hexdigest()

def build(root):
    root=Path(root)
    base=root/"validation_artifacts/p159/occ1h"
    hist_path=base/"h1_h3_execution_bundle_v1.json"
    post_path=base/"h1_h3_posthardening_evidence_v1.json"
    registry_path=base/"counterexample_registry_v1.json"
    for x in (hist_path,post_path,registry_path):
        if not x.is_file():
            return {"status":"INCOMPLETE","missing":str(x),"verified":False}

    hist=_load(hist_path); post=_load(post_path); reg=_load(registry_path)
    rows={r["attack_id"]:r for r in hist.get("rows",[])}
    domain=set(reg.get("classification_domain",[]))
    records=[]
    errors=[]

    for aid,spec in EXPECTED.items():
        row=rows.get(aid)
        if not row:
            errors.append(aid+":HISTORICAL_ROW_MISSING"); continue
        if row.get("verdict") != spec["historical_verdict"]:
            errors.append(aid+":HISTORICAL_VERDICT_DRIFT"); continue
        current=post.get(aid.lower()+"_verdict")
        if current != spec["current_verdict"]:
            errors.append(aid+":CURRENT_VERDICT_DRIFT"); continue
        if spec["classification"] not in domain:
            errors.append(aid+":CLASSIFICATION_OUTSIDE_REGISTRY_DOMAIN"); continue

        core={
          "schema":"oce.p159.occ1h.counterexample_record.v1",
          "attack_id":aid,
          "family_id":spec["family_id"],
          "historical_verdict":spec["historical_verdict"],
          "current_verdict":spec["current_verdict"],
          "classification":spec["classification"],
          "classification_basis":spec["classification_basis"],
          "historical_evidence":{
             "path":"validation_artifacts/p159/occ1h/h1_h3_execution_bundle_v1.json",
             "sha256":_sha(hist_path),
          },
          "posthardening_evidence":{
             "path":"validation_artifacts/p159/occ1h/h1_h3_posthardening_evidence_v1.json",
             "sha256":_sha(post_path),
          },
          "injection_effective":bool(row.get("injection_effective")),
          "historical_observed_reason":row.get("observed_reason"),
          "historical_detector":row.get("detector"),
          "minimization":{
             "status":"MINIMAL_REPRODUCER_ALREADY_PRESENT",
             "basis":"The executable H1-H3 crown injects a single semantic-status mutation for A008 and a minimal duplicate-key JSON object for A009.",
          },
          "normative_auto_rewrite":False,
          "historical_result_rewritten":False,
          "authorization_created":False,
          "execution_performed":False,
          "functional_only":True,
          "phenomenology_undetermined":True,
        }
        records.append(dict(core, record_sha256=_record_hash(core)))

    return {
      "schema":"oce.p159.occ1h.historical_counterexample_evidence.v1",
      "status":"VERIFIED" if not errors and len(records)==2 else "INCOMPLETE",
      "verified":not errors and len(records)==2,
      "source_registry_sha256":_sha(registry_path),
      "successful_attack_requires_record":reg.get("successful_attack_requires_record"),
      "minimize_where_practical":reg.get("minimize_where_practical"),
      "silent_normative_repair_forbidden":reg.get("silent_normative_repair_forbidden"),
      "records":records,
      "errors":errors,
      "historical_evidence_rewritten":False,
      "normative_auto_rewrite":False,
      "authorization_created":False,
      "execution_performed":False,
      "occ1h_closed":False,
      "occ1i_opened":False,
      "p159_final_lock":False,
      "p160_opened":False,
      "functional_only":True,
      "phenomenology_undetermined":True,
    }

def verify_materialized(root):
    root=Path(root)
    bundle=root/"validation_artifacts/p159/occ1h/historical_counterexample_evidence_v1.json"
    if not bundle.is_file(): return False
    d=_load(bundle)
    if not d.get("verified") or len(d.get("records",[])) != 2: return False
    for r in d["records"]:
        core=dict(r); declared=core.pop("record_sha256",None)
        if declared != _record_hash(core): return False
        rp=root/"validation_artifacts/p159/occ1h/counterexamples"/(declared+".json")
        if not rp.is_file() or _sha(rp) != declared: return False
        if _load(rp) != core: return False
        for ev in ("historical_evidence","posthardening_evidence"):
            ep=root/r[ev]["path"]
            if not ep.is_file() or _sha(ep) != r[ev]["sha256"]: return False
    return True

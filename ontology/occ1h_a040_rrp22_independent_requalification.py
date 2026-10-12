from __future__ import annotations
from copy import deepcopy
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path

PASS, FAIL="PASS","FAIL"
PRIMITIVE="occ1h_a040_rrp22_independent_requalification"
VERSION="P159-OCC1H-A040-RRP22-v1"
def _canon(v): return json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=False)
def _sha(v): return sha256(_canon(v).encode("utf-8")).hexdigest()
def _parse(s):
    raw=str(s).strip()
    if raw.endswith("Z"): raw=raw[:-1]+"+00:00"
    d=datetime.fromisoformat(raw)
    if d.tzinfo is None or d.utcoffset() is None: raise ValueError("UTC_OFFSET_REQUIRED")
    return d.astimezone(timezone.utc)
def _r(status,reason,**extra):
    out={"primitive":PRIMITIVE,"version":VERSION,"status":status,"reason":reason,"rrp_stage":"RRP-22",
      "implementation_module_used_as_oracle":False,"compiler_used_as_oracle":False,
      "rrp21_self_certification_accepted":False,"authority_created":False,"execution_performed":False,
      "historical_evidence_modified":False,"criticality_changed":False,"occ1h_closed":False,"p160_opened":False,
      "functional_conclusion_only":True,"phenomenology_undetermined":True}
    out.update(deepcopy(extra)); return out

def independently_requalify(root,rrp21_artifact):
    root=Path(root); dp=root/"validation_artifacts/p159/occ1h/a040/a040_governed_normative_decision_v1.json"
    if not dp.is_file(): return _r(FAIL,"GOVERNED_DECISION_MISSING")
    try: d=json.loads(dp.read_text(encoding="utf-8"))
    except Exception as exc: return _r(FAIL,"GOVERNED_DECISION_PARSE_FAILED",error=str(exc))
    if d.get("human_confirmation",{}).get("confirmed") is not True or d.get("target")!="CCAD.P7": return _r(FAIL,"GOVERNED_DECISION_INVALID")
    if rrp21_artifact.get("status")!=PASS or rrp21_artifact.get("rrp21_status")!="REMEDIATION_IMPLEMENTED_AND_EXPERIMENTALLY_DISCRIMINATED":
        return _r(FAIL,"RRP21_SUCCESS_EVIDENCE_REQUIRED")
    n=d.get("normative_completion",{})
    semantic_ok=(n.get("exception_identity",{}).get("semantics")=="STABLE_UNIQUE_EXCEPTION_ID"
      and n.get("expiry_parameter",{}).get("semantics")=="EXPLICIT_EXPIRES_AT"
      and n.get("expiry_parameter",{}).get("implicit_renewal") is False
      and n.get("expiry_parameter",{}).get("extension_requires_new_governed_decision") is True
      and n.get("authoritative_time_reference",{}).get("semantics")=="EXPLICIT_UTC_INSTANT_WITH_GOVERNED_TIME_SOURCE"
      and n.get("authoritative_time_reference",{}).get("clock_inconsistency")=="FAIL_CLOSED_FOR_EXCEPTION_DEPENDENT_ACTIONS"
      and n.get("post_expiry_effect",{}).get("at_or_after_expiry")=="EXCEPTION_INAPPLICABLE"
      and n.get("post_expiry_effect",{}).get("underlying_rule")=="RESTORED_TO_FULL_EFFECT"
      and n.get("post_expiry_effect",{}).get("retroactive_invalidation") is False)
    expiry=_parse("2030-01-01T00:00:00Z")
    independent_boundary_ok=(_parse("2029-12-31T23:59:59Z")<expiry and not (_parse("2030-01-01T00:00:00Z")<expiry) and not (_parse("2030-01-01T00:00:01Z")<expiry))
    e=rrp21_artifact.get("evidence",{})
    consistency=(e.get("before_expiry",{}).get("applicable") is True and e.get("at_expiry",{}).get("applicable") is False
      and e.get("after_expiry",{}).get("applicable") is False and e.get("clock_inconsistency",{}).get("applicable") is False
      and e.get("missing_identity",{}).get("status")==FAIL)
    ok=semantic_ok and independent_boundary_ok and consistency
    q={"scenario":"expiry removal","affected_mechanism":"governed temporary exception validity boundary",
       "constitutional_effect":"removing or bypassing expiry can prolong exception applicability beyond governed authorization",
       "root_invariants":["DNA.L0.2","DNA.L0.3","DNA.L0.5"],
       "causal_path":"expiry removal -> temporary exception remains applicable after expires_at -> authorization boundary is amplified/circumvented and provenance-governed validity is violated -> DNA.L0.2/DNA.L0.3/DNA.L0.5",
       "materiality":"ROOT" if ok else "ROOT_UNDETERMINED",
       "rrp22_status":"INDEPENDENT_REQUALIFICATION_PASSED" if ok else "INDEPENDENT_REQUALIFICATION_FAILED",
       "return_to_rrp9_rrp12":bool(ok),"closure_eligible_now":False}
    return _r(PASS if ok else FAIL,"A040_RRP22_INDEPENDENT_REQUALIFICATION_OK" if ok else "A040_RRP22_INDEPENDENT_REQUALIFICATION_FAILED",
              semantic_decision_verified=semantic_ok,independent_boundary_verified=independent_boundary_ok,
              rrp21_evidence_consistent=consistency,qualification=q,qualification_sha256=_sha(q))

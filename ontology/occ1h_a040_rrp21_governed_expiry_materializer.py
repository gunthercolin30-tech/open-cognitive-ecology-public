from __future__ import annotations
from copy import deepcopy
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
from typing import Any, Dict, Mapping

PASS, FAIL = "PASS", "FAIL"
PRIMITIVE = "occ1h_a040_rrp21_governed_expiry_materializer"
VERSION = "P159-OCC1H-A040-RRP21-v1"
DECISION_SCHEMA = "oce.p159.occ1h.a040.governed_normative_decision.v1"

def _canon(v): return json.dumps(v, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
def _sha_obj(v): return sha256(_canon(v).encode("utf-8")).hexdigest()
def _sha_file(p): return sha256(Path(p).read_bytes()).hexdigest()
def _result(status, reason, **extra):
    out={"primitive":PRIMITIVE,"version":VERSION,"status":status,"reason":reason,"rrp_stage":"RRP-21",
         "authorization_created":False,"authority_activated":False,"execution_performed":False,
         "canonical_source_modified":False,"historical_evidence_modified":False,
         "root_criteria_reduced":False,"criticality_changed":False,"occ1h_closed":False,
         "p160_opened":False,"functional_conclusion_only":True,"phenomenology_undetermined":True}
    out.update(deepcopy(extra)); return out
def _parse_utc(s):
    raw=str(s).strip()
    if raw.endswith("Z"): raw=raw[:-1]+"+00:00"
    dt=datetime.fromisoformat(raw)
    if dt.tzinfo is None or dt.utcoffset() is None: raise ValueError("UTC_OFFSET_REQUIRED")
    return dt.astimezone(timezone.utc)

def validate_governed_inputs(root):
    root=Path(root)
    dp=root/"validation_artifacts/p159/occ1h/a040/a040_governed_normative_decision_v1.json"
    ap=root/"oif_review/campaigns/P159-OCC1A/occ1a_initial_development_authority_materialization.json"
    if not dp.is_file() or not ap.is_file(): return _result(FAIL,"GOVERNED_INPUT_MISSING")
    try:
        d=json.loads(dp.read_text(encoding="utf-8")); a=json.loads(ap.read_text(encoding="utf-8"))
    except Exception as exc: return _result(FAIL,"GOVERNED_INPUT_PARSE_FAILED",error=str(exc))
    if d.get("schema")!=DECISION_SCHEMA or d.get("target")!="CCAD.P7": return _result(FAIL,"A040_DECISION_IDENTITY_INVALID")
    if d.get("human_confirmation",{}).get("confirmed") is not True: return _result(FAIL,"HUMAN_CONFIRMATION_REQUIRED")
    if d.get("authority_id")!="OCE-HUMAN-INITIAL-001": return _result(FAIL,"DECISION_AUTHORITY_ID_INVALID")
    if a.get("authority_id")!="OCE-HUMAN-INITIAL-001" or a.get("human_confirmed") is not True: return _result(FAIL,"DEVELOPMENT_AUTHORITY_NOT_MATERIALIZED")
    if a.get("role")!="CONSTITUTIONAL_AUTHORITY" or "CONSTITUTIONAL_CHANGE" not in a.get("scope",[]): return _result(FAIL,"CONSTITUTIONAL_CHANGE_OUTSIDE_AUTHORITY_SCOPE")
    b=d.get("constitutional_boundaries",{})
    if any(b.get(k) is not False for k in ("dna_l0_modified","root_override_all","root_criteria_reduced","historical_evidence_rewritten")):
        return _result(FAIL,"CONSTITUTIONAL_BOUNDARY_VIOLATION")
    n=d.get("normative_completion",{})
    checks=[
      n.get("exception_identity",{}).get("semantics")=="STABLE_UNIQUE_EXCEPTION_ID",
      n.get("expiry_parameter",{}).get("semantics")=="EXPLICIT_EXPIRES_AT",
      n.get("authoritative_time_reference",{}).get("semantics")=="EXPLICIT_UTC_INSTANT_WITH_GOVERNED_TIME_SOURCE",
      n.get("post_expiry_effect",{}).get("at_or_after_expiry")=="EXCEPTION_INAPPLICABLE"]
    if not all(checks): return _result(FAIL,"REQUIRED_NORMATIVE_SEMANTICS_MISSING")
    return _result(PASS,"GOVERNED_A040_INPUTS_VALID",decision_sha256=_sha_file(dp),
                   authority_sha256=_sha_file(ap),governed_decision=deepcopy(d))

def materialize_contract(root):
    checked=validate_governed_inputs(root)
    if checked.get("status")!=PASS: return checked
    d=checked["governed_decision"]; n=d["normative_completion"]
    contract={"schema":"oce.p159.occ1h.a040.rrp21.expiry_contract.v1","target":"CCAD.P7",
      "decision_id":d["decision_id"],"decision_sha256":checked["decision_sha256"],"authority_id":d["authority_id"],
      "exception_identity":n["exception_identity"]["semantics"],"expiry_parameter":n["expiry_parameter"]["semantics"],
      "time_format":n["expiry_parameter"]["time_format"],"time_reference":n["authoritative_time_reference"]["semantics"],
      "clock_inconsistency":n["authoritative_time_reference"]["clock_inconsistency"],
      "at_or_after_expiry":n["post_expiry_effect"]["at_or_after_expiry"],
      "underlying_rule_after_expiry":n["post_expiry_effect"]["underlying_rule"],
      "new_exception_dependent_action":n["post_expiry_effect"]["new_exception_dependent_action"],
      "retroactive_invalidation":n["post_expiry_effect"]["retroactive_invalidation"],
      "implicit_renewal":n["expiry_parameter"]["implicit_renewal"],
      "extension_requires_new_governed_decision":n["expiry_parameter"]["extension_requires_new_governed_decision"],
      "norm_ops":["CHECK_EXPIRY"],"compiler_invents_normative_values":False,"runtime_authority_granted":False}
    return _result(PASS,"A040_RRP21_GOVERNED_EXPIRY_CONTRACT_MATERIALIZED",contract=contract,contract_sha256=_sha_obj(contract))

def evaluate_exception(contract, instance):
    if not isinstance(instance.get("exception_id"),str) or not instance["exception_id"].strip():
        return {"status":FAIL,"reason":"STABLE_EXCEPTION_ID_REQUIRED","applicable":False}
    if instance.get("authorized") is not True: return {"status":PASS,"reason":"EXCEPTION_NOT_AUTHORIZED","applicable":False}
    if instance.get("clock_consistent") is not True: return {"status":PASS,"reason":"CLOCK_INCONSISTENCY_FAIL_CLOSED","applicable":False}
    try: now=_parse_utc(instance["now"]); expiry=_parse_utc(instance["expires_at"])
    except Exception as exc: return {"status":FAIL,"reason":"EXPLICIT_UTC_INSTANT_REQUIRED","applicable":False,"error":str(exc)}
    applicable=now<expiry
    return {"status":PASS,"reason":"EXCEPTION_APPLICABLE_BEFORE_EXPIRY" if applicable else "EXCEPTION_INAPPLICABLE_AT_OR_AFTER_EXPIRY",
            "applicable":applicable,"underlying_rule_applicable":not applicable,"retroactive_invalidation":False}

def run_discriminating_experiment(root):
    m=materialize_contract(root)
    if m.get("status")!=PASS: return m
    c=m["contract"]; base={"exception_id":"A040-RRP21-CONTROL-001","authorized":True,"clock_consistent":True,"expires_at":"2030-01-01T00:00:00Z"}
    before=evaluate_exception(c,dict(base,now="2029-12-31T23:59:59Z"))
    boundary=evaluate_exception(c,dict(base,now="2030-01-01T00:00:00Z"))
    after=evaluate_exception(c,dict(base,now="2030-01-01T00:00:01Z"))
    clock_bad=evaluate_exception(c,dict(base,now="2029-12-31T23:59:59Z",clock_consistent=False))
    missing=evaluate_exception(c,{"authorized":True,"clock_consistent":True,"expires_at":"2030-01-01T00:00:00Z","now":"2029-12-31T23:59:59Z"})
    ok=(before.get("applicable") is True and boundary.get("applicable") is False and after.get("applicable") is False
        and clock_bad.get("applicable") is False and missing.get("status")==FAIL)
    evidence={"before_expiry":before,"at_expiry":boundary,"after_expiry":after,"clock_inconsistency":clock_bad,"missing_identity":missing}
    return _result(PASS if ok else FAIL,"A040_RRP21_DISCRIMINATING_EXPIRY_EXPERIMENT_OK" if ok else "A040_RRP21_EXPERIMENT_FAILED",
                   contract_sha256=m["contract_sha256"],evidence=evidence,evidence_sha256=_sha_obj(evidence),
                   rrp21_status="REMEDIATION_IMPLEMENTED_AND_EXPERIMENTALLY_DISCRIMINATED" if ok else "FAILED")

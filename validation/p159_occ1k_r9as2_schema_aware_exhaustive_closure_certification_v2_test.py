from copy import deepcopy
from validation import p159_occ1k_r9as2_schema_aware_exhaustive_closure_certification_v2 as m
def test_real_closure_certified():
 x=m.certify();assert x["status"]=="P159_EXHAUSTIVE_CLOSURE_CERTIFIED" and x["passed"]==x["total"]==10
def test_functional_invariants_from_actual_schemas():
 x=m.certify();assert x["checks"]["functional_only"]
def test_missing_epistemic_evidence_rejected():
 q=deepcopy(m.load(m.Q));q["functional_conclusion_only"]=False
 assert "NOT_CERTIFIED" in m.certify({"post":q})["status"]
def test_persisted_report_schema_accepted():
 txt=m.REPORT.read_text(encoding="utf-8",errors="replace");assert m.report_ok(txt)
def test_fast_acceptance_marker_required():
 assert not m.report_ok("validation_mode=fast_acceptance")
def test_locked_required():
 l=deepcopy(m.load(m.L));l["status"]="LOCK_DEGRADED"
 assert "NOT_CERTIFIED" in m.certify({"locked":l})["status"]
def test_post_lock_required():
 q=deepcopy(m.load(m.Q));q["status"]="REJECTED"
 assert "NOT_CERTIFIED" in m.certify({"post":q})["status"]
def test_bundle_required():
 b=deepcopy(m.load(m.B));b["status"]="INCOMPLETE"
 assert "NOT_CERTIFIED" in m.certify({"bundle":b})["status"]
def test_historical_r9as_preserved():
 x=m.certify();assert x["historical_r9as_preserved"] and not x["historical_r9as_rewritten"]
def test_p160b_not_opened():
 assert m.certify()["p160b_opened"] is False
def test_read_only():
 assert m.certify()["production_modified"] is False
def test_deterministic(): assert m.certify()==m.certify()

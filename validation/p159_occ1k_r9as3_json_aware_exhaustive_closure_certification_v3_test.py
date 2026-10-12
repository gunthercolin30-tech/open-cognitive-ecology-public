from copy import deepcopy
from validation import p159_occ1k_r9as3_json_aware_exhaustive_closure_certification_v3 as m
def test_real_certified():
 x=m.certify();assert x["status"]=="P159_EXHAUSTIVE_CLOSURE_CERTIFIED" and x["passed"]==x["total"]==10
def test_real_report_json_accepted(): assert m.report_ok(m.REPORT.read_text(encoding="utf-8",errors="replace"))
def test_report_success_required():
 d=m.parse_report(m.REPORT.read_text());d["success"]=False
 assert not m.report_ok("header\n"+m.canon(d))
def test_report_returncode_required():
 d=m.parse_report(m.REPORT.read_text());d["returncode"]=1
 assert not m.report_ok("header\n"+m.canon(d))
def test_suite_status_required():
 d=m.parse_report(m.REPORT.read_text());d["suites"][0]["status"]="failed"
 assert not m.report_ok("header\n"+m.canon(d))
def test_fast_marker_required():
 d=m.parse_report(m.REPORT.read_text());d["suites"][0]["marker"]="NO"
 assert not m.report_ok("header\n"+m.canon(d))
def test_malformed_report_rejected(): assert not m.report_ok("not json")
def test_functional_invariants_required():
 q=deepcopy(m.load(m.Q));q["functional_conclusion_only"]=False
 assert "NOT_CERTIFIED" in m.certify({"post":q})["status"]
def test_locked_required():
 l=deepcopy(m.load(m.L));l["status"]="LOCK_DEGRADED"
 assert "NOT_CERTIFIED" in m.certify({"locked":l})["status"]
def test_historical_failures_preserved():
 x=m.certify();assert x["historical_failed_certifications_preserved"] and not x["historical_failed_certifications_rewritten"]
def test_p160b_closed(): assert m.certify()["p160b_opened"] is False
def test_read_only(): assert m.certify()["production_modified"] is False
def test_deterministic(): assert m.certify()==m.certify()

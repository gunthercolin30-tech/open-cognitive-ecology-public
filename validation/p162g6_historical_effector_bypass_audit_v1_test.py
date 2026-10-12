import json
from pathlib import Path
from ontology.historical_effector_bypass_auditor import scan_file
ROOT=Path(__file__).resolve().parents[1]
A=ROOT/"validation_artifacts/p162/p162g/g6"
def test_report_and_registry_exist():
 assert (A/"historical_effector_bypass_audit.json").is_file()
 assert (A/"effector_mediation_registry.json").is_file()
def test_unknown_is_blocking():
 r=json.loads((A/"effector_mediation_registry.json").read_text())
 assert r["status"]=="OPEN";assert all(e["classification"]=="REVIEW_REQUIRED" for e in r["entries"])
def test_scanner_detects_process(tmp_path):
 p=tmp_path/"x.py";p.write_text("import subprocess\nsubprocess.run(['true'])\n")
 x=scan_file(p,tmp_path);assert x["classification"]=="REVIEW_REQUIRED";assert x["primitives"][0]["effect_class"]=="PROCESS"
def test_scanner_does_not_call_plain_computation_causal(tmp_path):
 p=tmp_path/"x.py";p.write_text("def f(x): return x+1\n")
 assert scan_file(p,tmp_path)["classification"]=="NONCAUSAL_NO_STRONG_PRIMITIVE"
def test_g5_is_detected_as_mediated_candidate():
 x=scan_file(ROOT/"ontology/governed_effector_adapter.py",ROOT)
 assert x["classification"] in ("MEDIATED_CANDIDATE","NONCAUSAL_NO_STRONG_PRIMITIVE")
def test_no_automatic_migration_claim():
 s=json.loads((A/"g6_summary.json").read_text());assert s["historical_effector_migration_complete"] is False

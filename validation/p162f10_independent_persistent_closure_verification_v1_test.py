"""Independent P162-F persistent closure verifier."""
from pathlib import Path
import hashlib,json
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"validation_artifacts/p162/p162f"
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def load(n): return json.loads((OUT/n).read_text(encoding="utf-8"))
def test_p162f10_manifest_integrity():
 m=load("protected_manifest.json")
 assert m["schema"]=="oce.p162f.protected_manifest.v1"
 for rel,h in m["files"].items(): assert (ROOT/rel).is_file() and sha(ROOT/rel)==h,rel
def test_p162f10_evidence_is_complete_and_functional_only():
 e=load("closure_evidence.json")
 assert e["targeted_f1_f9"]=="136/136_PASS" and e["transversal_p162a_f9"]=="423/423_PASS"
 assert e["f9_zero_gap"]=="22/22_PASS" and e["canonical_gaps_remaining"]==0
 assert (e["canonical_mutants_executed"],e["canonical_mutants_killed"],e["surviving_mutants"],e["mutation_score"])==(12,12,0,1.0)
 assert (e["conceptual_objects"],e["canonical_statuses"],e["doctrines"],e["invariants"],e["defense_cases"],e["root_cases"],e["canonical_mutations"],e["canonical_artifacts"])==(4,16,12,18,20,10,12,11)
 assert e["functional_only"] is True and e["phenomenology_undetermined"] is True
def test_p162f10_closure_boundary_noncausal():
 e=load("closure_evidence.json");r=load("closure_report.json")
 assert e["authorization_created"] is False and r["authorization_created"] is False
 assert e["capability_accessed"] is False and r["capability_accessed"] is False
 assert e["real_world_effect_performed"] is False and r["execution_performed"] is False
 assert e["p162g_opened"] is False and r["p162g_opened"] is False
def test_p162f10_bundle_hash_chain():
 b=load("closure_bundle.json")
 assert b["manifest"]==sha(OUT/"protected_manifest.json")
 assert b["evidence"]==sha(OUT/"closure_evidence.json")
 assert b["report"]==sha(OUT/"closure_report.json")
def test_p162f10_report_status_and_no_global_validation_claim():
 r=load("closure_report.json")
 assert r["status"]=="CLOSED" and r["global_validation_run"] is False
 assert r["protected_manifest_sha256"]==sha(OUT/"protected_manifest.json")
 assert r["closure_evidence_sha256"]==sha(OUT/"closure_evidence.json")

import json
from pathlib import Path
from ontology import occ_static_constitutional_checker as S
from ontology import occ_golden_constitutional_vectors as G
ROOT=Path(__file__).resolve().parents[1]
E=json.loads((ROOT/"validation_artifacts/p159/occ1i/f4g3_10a_dm015_dm018_dm033_minimal_existing_surface_refinement_v1.json").read_text())
def ev(m,k,b,a): return m.evaluate_defensive_semantic_transition(k,b,a)["status"]
def test_status(): assert E["status"].endswith("MINIMAL_EXISTING_SURFACE_REFINEMENT_COMPLETE")
def test_dm015_nominal(): assert all(ev(m,"scope_intersection",{"composition":"INTERSECTION"},{"composition":"INTERSECTION"})=="PASS" for m in (S,G))
def test_dm015_degraded(): assert all(ev(m,"scope_intersection",{"composition":"INTERSECTION"},{"composition":"UNION"})=="FAIL" for m in (S,G))
def test_dm018_nominal(): assert all(ev(m,"nondelegability",{"delegable":False},{"delegable":False})=="PASS" for m in (S,G))
def test_dm018_degraded(): assert all(ev(m,"nondelegability",{"delegable":False},{"delegable":True})=="FAIL" for m in (S,G))
def test_dm033_nominal(): assert all(ev(m,"timeout",{"timed_out":True},{"decision":"FAIL"})=="PASS" for m in (S,G))
def test_dm033_degraded(): assert all(ev(m,"timeout",{"timed_out":True},{"decision":"PASS"})=="FAIL" for m in (S,G))
def test_invalid_failclosed(): assert all(ev(m,"timeout",{}, {})=="FAIL" for m in (S,G))
def test_unknown_failclosed(): assert all(ev(m,"x",{}, {})=="FAIL" for m in (S,G))
def test_determinism(): assert len({json.dumps(S.evaluate_defensive_semantic_transition("timeout",{"timed_out":True},{"decision":"PASS"}),sort_keys=True) for _ in range(5)})==1
def test_backups(): assert all((ROOT/p).is_file() for p in E["backup_paths"])
def test_no_create(): assert E["new_primitive_created"] is False and E["new_norm_created"] is False and E["new_authority_created"] is False and E["new_detector_module_created"] is False and E["create_authorized"] is False
def test_no_verdict(): assert E["causal_verdicts_assigned"] is False and all(E[x]=="INCONCLUSIVE" for x in ("DM015","DM018","DM033"))
def test_refine_only(): assert set(E["decisions"].values())=={"REFINE_EXISTING_SURFACES"}
def test_next(): assert E["next_required_stage"]=="F4-G3.10B_DM015_DM018_DM033_REFINEMENT_QUALIFICATION"
def test_epistemics(): assert E["functional_conclusion_only"] is True and E["phenomenology_undetermined"] is True and E["p159_final_lock"] is False and E["p160_opened"] is False

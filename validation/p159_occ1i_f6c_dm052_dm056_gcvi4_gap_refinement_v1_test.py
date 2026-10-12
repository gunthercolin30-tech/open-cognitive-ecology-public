import json
from copy import deepcopy
from pathlib import Path
from ontology import occ_golden_constitutional_vectors as g
R=Path(__file__).resolve().parents[1]
A=json.loads((R/"validation_artifacts/p159/occ1i/f6c_dm052_dm056_gcvi4_gap_refinement_v1.json").read_text())
D=R/"validation_artifacts/p159/occ1g"
def load():
 return tuple(json.loads((D/n).read_text()) for n in ("gcv_core_v1.json","gcv_extended_v1.json","corpus_manifest_v1.json","change_ledger_v1.json","golden_run_report_v1.json"))
def test_backup(): assert A["pre_sha256"]==A["backup_sha256"]
def test_refine_not_create(): assert A["strategy"]=="REFINE_EXISTING_GCVI_4" and A["new_detector_created"] is False
def test_gcvi4_preserved(): assert A["gcvi_id_preserved"]=="GCVI-4"
def test_baseline_gcvi4_pass():
 c,e,m,l,r=load(); assert g.compute_gcvi(c,e,m,l,r,r["source_binding"])["GCVI-4"]=="PASS"
def test_dm052_omission_gcvi4_fail():
 c,e,m,l,r=load(); r=deepcopy(r); r["core_results"]=r["core_results"][:-1]; assert g.compute_gcvi(c,e,m,l,r,r["source_binding"])["GCVI-4"]=="FAIL"
def test_dm056_count_gcvi4_fail():
 c,e,m,l,r=load(); r=deepcopy(r); r["root_vector_count"]+=1; assert g.compute_gcvi(c,e,m,l,r,r["source_binding"])["GCVI-4"]=="FAIL"
def test_skipped_still_fail():
 c,e,m,l,r=load(); r=deepcopy(r); r["skipped_vectors"]=["X"]; assert g.compute_gcvi(c,e,m,l,r,r["source_binding"])["GCVI-4"]=="FAIL"
def test_root_bad_still_fail():
 c,e,m,l,r=load(); r=deepcopy(r); r["core_results"][0]["vector_verdict"]="FAIL"; assert g.compute_gcvi(c,e,m,l,r,r["source_binding"])["GCVI-4"]=="FAIL"
def test_replay(): assert A["replay_required"] is True
def test_epistemics(): assert A["functional_conclusion_only"] is True and A["phenomenology_undetermined"] is True
def test_boundaries(): assert A["p159_final_lock"] is False and A["p160_opened"] is False

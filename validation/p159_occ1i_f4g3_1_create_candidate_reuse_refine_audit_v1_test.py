import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
D=json.loads((ROOT/"validation_artifacts/p159/occ1i/f4g3_1_create_candidate_reuse_refine_audit_v1.json").read_text())
def test_status(): assert D["status"]=="F4_G3_1_REUSE_REFINE_AUDIT_COMPLETE"
def test_scope(): assert D["scope"]==["DM003","DM015","DM017","DM018","DM022","DM033"] and D["scope_count"]==6
def test_no_create(): assert D["reuse_or_refine_path_found_count"]==6 and D["create_justified_count"]==0 and D["create_authorized"] is False
def test_dm003(): assert D["decisions"]["DM003"]["decision"]=="RECONCILE_PROVENANCE_THEN_EXACT_REPLAY"
def test_dm017(): assert D["decisions"]["DM017"]["decision"]=="RECONCILE_PROVENANCE_THEN_EXACT_REPLAY"
def test_test_surface(): assert all(D["decisions"][x]["decision"]=="REFINE_EXISTING_TEST_SURFACE_THEN_EXACT_REPLAY" for x in ("DM015","DM018","DM033"))
def test_dm022(): assert D["decisions"]["DM022"]["decision"]=="REUSE_EXISTING_MECHANISMS_AND_REQUALIFY_EXACT_CAUSAL_EVIDENCE" and D["decisions"]["DM022"]["historical_map_status"]=="KILLED"
def test_no_verdict(): assert D["causal_verdicts_assigned"] is False and D["historical_states_preserved"] is True
def test_no_runtime(): assert D["runtime_mechanisms_modified"] is False and D["global_mutation_registry_modified"] is False
def test_next(): assert D["g3_2_ready"] is True and D["g3_closed"] is False and D["next_required_stage"]=="F4-G3.2_PROVENANCE_RECONCILIATION_DM003_DM017"
def test_epistemics(): assert D["functional_conclusion_only"] is True and D["phenomenology_undetermined"] is True and D["p159_final_lock"] is False and D["p160_opened"] is False

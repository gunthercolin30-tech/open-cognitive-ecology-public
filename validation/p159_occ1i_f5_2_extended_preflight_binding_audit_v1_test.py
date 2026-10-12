import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
D=json.loads((ROOT/"validation_artifacts/p159/occ1i/f5_2_extended_preflight_binding_audit_v1.json").read_text())
E={"DM039","DM043","DM044","DM046","DM048","DM049","DM051","DM052","DM054","DM056","DM057"}
def test_status(): assert D["status"]=="F5_2_EXTENDED_PREFLIGHT_BINDING_AUDIT_COMPLETE"
def test_count(): assert D["extended_count"]==11 and set(D["extended_ids"])==E
def test_groups_partition(): assert set(sum(D["groups"].values(),[]))==E and sum(len(v) for v in D["groups"].values())==11
def test_bindings(): assert set(D["target_bindings"])==E and D["all_target_bindings_present"] is True
def test_parseable(): assert D["all_target_bindings_parseable"] is True
def test_inventory(): assert D["ontology_inventory_checked"] is True
def test_support(): assert D["support_surfaces_present"] is True and len(D["support_surfaces"])==3
def test_dispositions(): assert set(D["dispositions"])==E and set(D["dispositions"].values())=={"REUSE_OR_REFINE_QUALIFICATION_REQUIRED"}
def test_no_create(): assert D["create_authorized"] is False and D["create_candidates"]==[]
def test_not_exhausted(): assert D["reuse_refine_exhausted"] is False
def test_no_runtime_change(): assert D["production_runtime_modified"] is False and D["canonical_sources_modified"] is False
def test_hashes(): assert all(len(v["sha256"])==64 for v in D["target_bindings"].values()) and all(len(v["sha256"])==64 for v in D["support_surfaces"])
def test_f5_2(): assert D["f5_2_complete"] is True
def test_next(): assert D["next_required_stage"]=="F5_3_EXTENDED_EXISTING_SURFACE_QUALIFICATION"
def test_epistemics(): assert D["functional_conclusion_only"] is True and D["phenomenology_undetermined"] is True and D["p159_final_lock"] is False and D["p160_opened"] is False

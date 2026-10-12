import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
D=json.loads((ROOT/"validation_artifacts/p159/occ1i/f4g3_6_dm003_dm017_reuse_refine_exhaustion_audit_v1.json").read_text())
def test_status(): assert D["status"]=="F4_G3_6_DM003_DM017_REUSE_REFINE_EXHAUSTION_AUDIT_COMPLETE"
def test_inventory(): assert D["ontology_inventory_checked"] is True
def test_dm003_refine(): assert D["DM003"]["decision"]=="REFINE_EXISTING_CANONICAL_SOURCE_SURFACE" and D["DM003"]["refine_exhausted"] is False
def test_dm003_nsi2(): assert D["DM003"]["refine_candidate"]["existing_semantic_anchor"]=="NSI-2:NO_SILENT_ACTIVE_NORM_LOSS"
def test_dm017_not_duplicate(): assert D["DM017"]["human_representative_interface_independent"] is False
def test_dm017_refine(): assert D["DM017"]["decision"]=="REFINE_EXISTING_INSTITUTIONAL_DOSSIER_SURFACE" and D["DM017"]["refine_exhausted"] is False
def test_dm017_anchor(): assert D["DM017"]["refine_candidate"]["existing_semantic_anchor"]=="INDEPENDENCE_DOMAIN_REQUIRED"
def test_reuse_exhausted(): assert D["DM003"]["reuse_exhausted"] is True and D["DM017"]["reuse_exhausted"] is True
def test_no_create(): assert D["DM003"]["create_justified"] is False and D["DM017"]["create_justified"] is False and D["create_authorized"] is False
def test_no_new_ontology(): assert D["new_primitive_required"] is False and D["new_norm_required"] is False and D["new_authority_required"] is False
def test_no_changes(): assert D["runtime_mechanisms_modified"] is False and D["test_surfaces_modified"] is False and D["new_detector_created"] is False
def test_no_verdict(): assert D["causal_verdicts_assigned"] is False and D["historical_states_preserved"] is True
def test_next(): assert D["next_required_stage"]=="F4-G3.7_DM003_DM017_MINIMAL_EXISTING_SURFACE_REFINEMENT"
def test_epistemics(): assert D["functional_conclusion_only"] is True and D["phenomenology_undetermined"] is True and D["p159_final_lock"] is False and D["p160_opened"] is False

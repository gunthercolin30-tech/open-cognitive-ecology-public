from pathlib import Path
import json
ROOT=Path.home()/"open-cognitive-ecology"
P=ROOT/"validation_artifacts/p159/occ1i/defensive_dm003_exact_binding_resolution_v3.json"
def load(): return json.loads(P.read_text())
def test_serialization_repair_is_semantic_preserving():
    d=load(); assert d["f4d2_semantics_preserved"] is True; assert d["f4d2_repair"]=="SERIALIZATION_ONLY_LITERAL_BACKSLASH_N_TO_NEWLINE"
def test_dm003_exact_binding():
    d=load(); assert d["dm003_state"]=="EXACT_STRUCTURAL_BINDING_RESOLVED_WITH_PROVENANCE_DEBT"; assert len(d["dm003_evidence"])==2
def test_evidence_is_hashed_and_structural():
    d=load()
    for e in d["dm003_evidence"]:
        assert len(e["sha256"])==64; assert len(e["signatures"])>=3; assert all(s["lines"] for s in e["signatures"])
def test_provenance_debt_and_no_empirical_upgrade():
    d=load(); assert d["dm003_provenance_debt"]=="PROVENANCE_UNRECONCILED"; assert d["binding_is_not_detector_evidence"] is True; assert d["f4b_statuses_not_reclassified"] is True; assert d["empirical_kill_claims_created"]==0
def test_stage_boundary():
    d=load(); assert d["all_11_original_f4d_bindings_structurally_resolved"] is True; assert d["dm045_survived_retained"] is True; assert d["next_stage_allowed"]=="F4-E"; assert d["extended_opened"] is False; assert d["occ1i_closed"] is False; assert d["p159_final_lock"] is False; assert d["p160_opened"] is False

import json
from pathlib import Path
R=Path(__file__).parents[1]
D=json.loads((R/"validation_artifacts/p159/occ1i/f4g1_dm002_provenance_reconciliation_v1.json").read_text())
def test_status(): assert D["status"]=="DM002_PROVENANCE_RECONCILED"
def test_id(): assert D["mutation_id"]=="DM002" and D["transformation"]=="MUST_NOT_TO_MAY"
def test_anchors(): assert len(D["anchors"])>=2
def test_ccad(): assert any(x["norm_id"]=="P156.BOUNDARIES.arbitration_creates_authority" for x in D["anchors"])
def test_r19(): assert any(x["norm_id"]=="R19.6" for x in D["anchors"])
def test_semantics(): assert all(x["semantic_polarity"]=="PROHIBITIVE" for x in D["anchors"])
def test_existing(): assert D["new_norm_created"] is False and D["existing_norms_reused"] is True
def test_no_verdict(): assert D["causal_verdict_assigned"] is False
def test_no_runtime(): assert not D["runtime_mechanisms_modified"]
def test_next(): assert D["dm002_causal_replay_ready"] is True and D["g1_replay_opened"] is False
def test_failclosed(): assert D["provenance_reconciliation_rule"]=="EXACT_EXISTING_PROHIBITIVE_ANCHORS_ONLY"
def test_epistemic(): assert D["functional_conclusion_only"] and D["phenomenology_undetermined"]

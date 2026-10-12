import hashlib,json
from pathlib import Path
R=Path(__file__).resolve().parents[1]; B=R/"validation_artifacts/p159/occ1i"
L=B/"f7a_consolidated_mroot_evidence_ledger_v2.json"; S=B/"f7a_consolidated_mroot_evidence_ledger_v2.identity_seal.json"; A=B/"f7b_mm05_external_identity_seal_refinement_v1.json"
D=json.loads(S.read_text()); X=json.loads(A.read_text()); J=json.loads(L.read_text())
def sh(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def test_seal_exists(): assert S.is_file()
def test_file_binding(): assert D["artifact_file_sha256"]==sh(L)
def test_identity_binding(): assert D["ledger_identity_sha256"]==J["ledger_identity_sha256"]
def test_counts(): assert D["mroot_expected_count"]==D["case_count"]==43
def test_non_authorizing(): assert D["non_authorizing_derived_evidence"] is True and X["new_normative_authority_created"] is False
def test_no_runtime(): assert X["production_runtime_modified"] is False
def test_no_history_change(): assert X["historical_artifacts_modified"] is False
def test_replay(): assert X["replay_required"] is True and X["next_required_stage"]=="F7_B_MM05_CAUSAL_REPLAY"
def test_epistemics(): assert X["functional_conclusion_only"] is True and X["phenomenology_undetermined"] is True
def test_boundaries(): assert X["p159_final_lock"] is False and X["p160_opened"] is False

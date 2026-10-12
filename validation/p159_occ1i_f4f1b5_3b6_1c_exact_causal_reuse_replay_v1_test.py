import json
from pathlib import Path
ROOT=Path(__file__).parents[1]
D=json.loads((ROOT/"validation_artifacts/p159/occ1i/f4f1b5_3b6_1c_exact_causal_reuse_replay_v1.json").read_text())
C={x["mutation_id"]:x for x in D["cases"]}
def test_status(): assert D["status"]=="CAUSAL_REUSE_REPLAY_COMPLETE"
def test_scope(): assert set(C)=={"DM038","DM042"}
def test_baselines(): assert all(x["baseline"]["closing_accepts"] and x["baseline"]["postclose_accepts"] for x in C.values())
def test_dm038_effective(): assert C["DM038"]["mutation_effective"] is True and C["DM038"]["root_compiler_hash_differs_from_snapshot"] is True
def test_dm038_closing_observes(): assert C["DM038"]["closing"]["decision"]=="OCC1E_CLOSE_REJECTED" and C["DM038"]["closing"]["profile_semantic_hash_valid"] is True and C["DM038"]["closing"]["profile_semantic_hash_bound"] is False
def test_dm038_postclose_observes(): assert C["DM038"]["postclose"]["decision"]=="OCC1E_POSTCLOSE_REJECTED" and C["DM038"]["postclose"]["exact_inputs_unchanged"] is False and C["DM038"]["postclose"]["profile_semantic_hash_matches_closure"] is False
def test_dm042_effective(): assert C["DM042"]["mutation_effective"] is True and C["DM042"]["false_declared_artifact_hash"] is True
def test_dm042_closing_observes(): assert C["DM042"]["closing"]["decision"]=="OCC1E_CLOSE_REJECTED" and C["DM042"]["closing"]["profile_semantic_hash_valid"] is False
def test_dm042_postclose_observes(): assert C["DM042"]["postclose"]["decision"]=="OCC1E_POSTCLOSE_REJECTED" and C["DM042"]["postclose"]["profile_semantic_hash_valid"] is False
def test_no_credit_or_patch(): assert D["detector_credit_assigned"] is False and D["runtime_mechanisms_modified"] is False and D["mutation_statuses_changed"] is False
def test_brest_boundary(): assert D["f4_f1b_5_3b6_1c"]=="DONE" and D["next_step_not_opened"] is True
def test_epistemic(): assert D["functional_conclusion_only"] is True and D["phenomenology_undetermined"] is True

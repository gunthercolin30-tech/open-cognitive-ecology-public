import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
D=json.loads((ROOT/"validation_artifacts/p159/occ1i/f6b_independent_verifier_causal_pilot_v2.json").read_text())
def test_cases(): assert set(D["cases"])=={"DM043","DM044","DM046"}
def test_isolated(): assert D["isolated_ast_mutation_only"] is True and D["production_runtime_modified"] is False
def test_effectiveness_consistency(): assert D["all_mutations_effective"]==all(x["mutation_effective"] for x in D["cases"].values())
def test_minimum(): assert all(x["minimum_distinct_detectors"]==2 for x in D["cases"].values())
def test_counts(): assert D["killed_count"]+D["inconclusive_count"]==3
def test_verdict_rule(): assert all(x["causal_verdict"]==("KILLED" if x["mutation_effective"] and x["distinct_protective_detections"]>=2 else "INCONCLUSIVE") for x in D["cases"].values())
def test_family_count(): assert all(x["distinct_protective_detections"]==sum(1 for f in x["protective_families"].values() if f["detected"]) for x in D["cases"].values())
def test_dm043(): assert D["cases"]["DM043"]["transformation"]=="IGNORE_MISSING_OR_EXTRA_RULES"
def test_dm044(): assert D["cases"]["DM044"]["transformation"]=="IGNORE_STRENGTHENING_OR_WEAKENING"
def test_dm046(): assert D["cases"]["DM046"]["transformation"]=="SKIP_SCOPE_CHECK"
def test_target_binding():
 assert D["cases"]["DM043"]["target_rule"]=="DNA.L0.2"
 assert D["cases"]["DM044"]["target_rule"]=="DNA.L0.6"
 assert D["cases"]["DM046"]["target_rule"]=="DNA.L0.2"
def test_no_create(): assert D["create_authorized"] is False
def test_hashes(): assert all(len(x)==64 for x in D["source_sha256"].values())
def test_next(): assert D["next_required_stage"] in {"F6_B_GAP_REFINEMENT","F6_C_GOLDEN_META_VALIDATION_CAMPAIGN"}
def test_epistemics(): assert D["functional_conclusion_only"] is True and D["phenomenology_undetermined"] is True
def test_no_final_lock(): assert D["p159_final_lock"] is False and D["p160_opened"] is False

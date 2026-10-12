import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
D=json.loads((ROOT/"validation_artifacts/p159/occ1i/f5_3_extended_existing_surface_qualification_v1.json").read_text())
E={"DM039","DM043","DM044","DM046","DM048","DM049","DM051","DM052","DM054","DM056","DM057"}
def test_status(): assert D["status"]=="F5_3_EXTENDED_EXISTING_SURFACES_QUALIFIED"
def test_count(): assert D["extended_count"]==D["qualified_count"]==11
def test_ids(): assert {x["mutation_id"] for x in D["cases"]}==E
def test_reuse(): assert D["reuse_qualified_count"]==11 and all(x["qualification"]=="REUSE_QUALIFIED_FOR_F6_CAUSAL_REPLAY" for x in D["cases"])
def test_no_refine(): assert D["refine_required_count"]==0 and all(x["refinement_required_before_f6"] is False for x in D["cases"])
def test_no_create(): assert D["create_required_count"]==0 and D["create_authorized"] is False and all(x["create_required"] is False for x in D["cases"])
def test_apis(): assert all(x["required_apis_present"] is True for x in D["cases"])
def test_mroot(): assert all(x["minimum_distinct_detectors"]==2 for x in D["cases"])
def test_detector_declarations(): assert all(len(x["expected_detector_families"])>=2 for x in D["cases"])
def test_no_causal_claim(): assert D["causal_mutation_executed"] is False and D["causal_verdicts_assigned"] is False and all(x["causal_verdict"]=="NOT_ASSIGNED_AT_F5_3" for x in D["cases"])
def test_scope(): assert D["qualification_scope"]=="EXISTING_SURFACE_AND_API_READINESS_ONLY"
def test_support(): assert len(D["support_surfaces"])==3 and all(len(x["sha256"])==64 for x in D["support_surfaces"].values())
def test_no_runtime_change(): assert D["production_runtime_modified"] is False and D["canonical_sources_modified"] is False
def test_next(): assert D["f5_3_complete"] is True and D["next_required_stage"]=="F6_EXTENDED_EMPIRICAL_CAMPAIGN"
def test_epistemics(): assert D["functional_conclusion_only"] is True and D["phenomenology_undetermined"] is True and D["p159_final_lock"] is False and D["p160_opened"] is False

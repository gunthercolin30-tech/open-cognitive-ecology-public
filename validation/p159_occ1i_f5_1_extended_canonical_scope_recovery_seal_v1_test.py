import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
D=json.loads((ROOT/"validation_artifacts/p159/occ1i/f5_1_extended_canonical_scope_recovery_seal_v1.json").read_text())
E=["DM039","DM043","DM044","DM046","DM048","DM049","DM051","DM052","DM054","DM056","DM057"]
def test_status(): assert D["status"]=="F5_1_EXTENDED_CANONICAL_SCOPE_SEALED"
def test_counts(): assert (D["total_mroot_count"],D["core_count"],D["extended_count"])==(43,32,11)
def test_identity(): assert D["partition_identity"]=="43=32+11" and D["partition_valid"] is True
def test_disjoint(): assert D["core_extended_intersection_count"]==0
def test_ids(): assert D["extended_ids"]==E
def test_case_count(): assert len(D["extended_cases"])==11
def test_all_mroot_policy(): assert all(c["minimum_distinct_detectors"]==2 for c in D["extended_cases"])
def test_pending(): assert D["all_extended_status"]=="PENDING_EXTENDED" and all(c["empirical_status"]=="PENDING_EXTENDED" for c in D["extended_cases"])
def test_required(): assert D["extended_required"] is True and D["extended_cannot_be_skipped"] is True
def test_no_creation(): assert D["new_mutation_created"] is False and D["new_operator_created"] is False and D["new_norm_created"] is False and D["new_authority_created"] is False
def test_no_runtime_change(): assert D["production_runtime_modified"] is False and D["canonical_sources_modified"] is False
def test_evidence(): assert len(D["evidence_sha256"])==5 and all(len(v)==64 for v in D["evidence_sha256"].values())
def test_sealed(): assert D["f5_1_sealed"] is True
def test_next(): assert D["next_required_stage"]=="F5_2_EXTENDED_PREFLIGHT_AND_BINDING_AUDIT"
def test_epistemics(): assert D["functional_conclusion_only"] is True and D["phenomenology_undetermined"] is True and D["p159_final_lock"] is False and D["p160_opened"] is False

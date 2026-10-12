from validation.p161j_semantic_mutation_crown_v1 import run_canonical_mutation_campaign
from validation.p161j_race_final_compare_crown_v1 import run_canonical_concurrency_crown
def test_mutations():
 r=run_canonical_mutation_campaign();assert r["zones_covered"]==[f"zone{x}" for x in "ABCDEFGH"];assert r["double_mutants"]>=2 and r["false_restrictive_mutants"]>=2 and r["meta_mutants"]>=2;assert r["ROOT_SURVIVED"]==r["ROOT_INCONCLUSIVE"]==r["META_TEST_FAILURE"]==r["CONTROL_MUTANT_FAILURE"]==r["MUTATION_CONTAMINATION"]==0;assert r["baseline_hash"]==r["restored_hash"];assert r["status"]=="PASS"
def test_concurrency():
 r=run_canonical_concurrency_crown();assert r["pass_count"]==r["total"]==11 and r["status"]=="PASS"

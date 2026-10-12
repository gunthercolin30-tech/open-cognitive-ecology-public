from pathlib import Path
from ontology import occ_constitutional_adversarial_crown as h
ROOT=Path(__file__).resolve().parents[1]
def test_extended_exact_a01_a105():
 x=h.build_extended(); assert len(x)==105; assert [r["attack_id"] for r in x]==["A%03d"%i for i in range(1,106)]
def test_all_ten_families():
 assert {r["family_id"] for r in h.build_extended()}=={"H"+str(i) for i in range(1,11)}
def test_core_40_stratified():
 c=h.build_core(); assert len(c)==40; assert all(sum(x["family_id"]=="H"+str(i) for x in c)==4 for i in range(1,11))
def test_verdicts_noncompensatory():
 assert {"VIOLATED","INCONCLUSIVE","RESISTED"}<=set(h.VERDICTS); assert all(x["root_non_compensatory"] for x in h.build_extended())
def test_compound_first_class():
 assert all(x["compound_or_sequential_first_class"] for x in h.build_extended() if x["family_id"] in ("H6","H10"))
def test_reuse_each_family():
 m=h.coverage_matrix(ROOT); assert len(m)==10; assert all(x["present_reuse"] for x in m)
def test_achi_1_16():
 assert [x["invariant"] for x in h.achi_matrix()]==["ACHI-"+str(i) for i in range(1,17)]
def test_counterexample_and_boundaries():
 f=h.foundation(ROOT); assert f["counterexample_registry"]["successful_attack_requires_record"]; assert f["counterexample_registry"]["silent_normative_repair_forbidden"]
 assert not any(f["boundaries"].values()); assert f["functional_only"] and f["phenomenology_undetermined"]

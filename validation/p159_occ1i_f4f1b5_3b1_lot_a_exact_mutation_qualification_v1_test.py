from pathlib import Path
import json
ROOT=Path.home()/"open-cognitive-ecology"
A=ROOT/"validation_artifacts/p159/occ1i/f4f1b5_3b1_lot_a_exact_mutation_qualification_v1.json"
def d(): return json.loads(A.read_text())
def test_six_cases(): assert [x["mutation_id"] for x in d()["cases"]]==["DM002","DM019","DM020","DM021","DM038","DM042"]
def test_dm002_not_promoted(): 
 x=d()["cases"][0]; assert x["qualification"]=="INCONCLUSIVE_PROVENANCE_DEBT" and x["provenance_debt"]=="PROVENANCE_UNRECONCILED"
def test_other_recipes_exactly_one_anchor():
 for x in d()["cases"][1:]: assert x["qualification"]=="EXACT_RECIPE_QUALIFIED" and x["anchor_occurrences"]==1
def test_hash_change_proven():
 for x in d()["cases"][1:]: assert x["baseline_sha256"] != x["mutated_sha256"]
def test_canonical_unchanged():
 for x in d()["cases"]: assert x["canonical_hash_after"]==x["canonical_hash_before"]
def test_no_status_promotion(): assert d()["mutation_statuses_changed"] is False and d()["detector_verdicts_assigned"] is False
def test_stage(): assert d()["stage_transition"]=={"F4-F1B.5.3B1":"DONE","F4-F1B.5.3B2":"NEXT"}
def test_boundaries(): 
 x=d(); assert not x["create_authorized"] and not x["occ1i_closed"] and not x["p159_final_lock"] and not x["p160_opened"]

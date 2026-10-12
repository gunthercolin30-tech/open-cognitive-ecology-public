from pathlib import Path
import json
ROOT=Path.home()/"open-cognitive-ecology"
P=ROOT/"validation_artifacts/p159/occ1i/f4f1b5_3a_lot_a_causal_preflight_v1.json"
def d(): return json.loads(P.read_text())
def test_ids(): assert [x["mutation_id"] for x in d()["cases"]]==["DM002","DM019","DM020","DM021","DM038","DM042"]
def test_targets(): assert all(x["target_path"] for x in d()["cases"])
def test_no_downstream_substitution(): assert all(x["downstream_equivalent_fixture_is_exact_replay"] is False for x in d()["cases"])
def test_dm002_debt(): assert next(x for x in d()["cases"] if x["mutation_id"]=="DM002")["provenance_debt"]=="PROVENANCE_UNRECONCILED"
def test_no_modification(): assert d()["mechanisms_modified"] is False and d()["mutation_statuses_changed"] is False
def test_stage(): assert d()["stage_transition"]=={"F4-F1B.5.3A":"DONE","F4-F1B.5.3B":"NEXT"}
def test_boundaries(): x=d(); assert not x["create_authorized"] and not x["occ1i_closed"] and not x["p159_final_lock"] and not x["p160_opened"]

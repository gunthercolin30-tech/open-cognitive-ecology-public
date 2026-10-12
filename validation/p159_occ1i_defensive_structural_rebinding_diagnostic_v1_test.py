from pathlib import Path
import json
ROOT=Path.home()/"open-cognitive-ecology"
P=ROOT/"validation_artifacts/p159/occ1i/defensive_structural_rebinding_diagnostic_v1.json"
def load(): return json.loads(P.read_text())
def test_accounting_and_no_reclassification():
 d=load(); assert d["blocked_case_count"]==25; assert d["f4b_statuses_not_reclassified"] is True; assert d["empirical_kill_claims_created"]==0
def test_dm045_survivor_is_retained():
 d=load(); r={x["mutation_id"]:x for x in d["results"]}; assert r["DM045"]["f4b_status"]=="SURVIVED"; assert r["DM045"]["survivor_retained"] is True
def test_m1_drift_is_fail_closed():
 d=load(); assert d["m1_source_package_hash_drift"] is True; assert {"DM002","DM003","DM005"}.issubset(set(d["unresolved_rebinding_ids"]))
def test_boundaries():
 d=load(); assert d["canonical_files_modified"] is False; assert d["extended_opened"] is False; assert d["occ1i_closed"] is False; assert d["p159_final_lock"] is False; assert d["p160_opened"] is False

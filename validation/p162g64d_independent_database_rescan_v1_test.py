import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
R=ROOT/"validation_artifacts/p162/p162g/g64d/independent_database_rescan.json"
def data(): return json.loads(R.read_text())
def test_database_zero_verified():
 d=data(); assert d["status"]=="DATABASE_ZERO_VERIFIED"; assert d["direct_database_bypass_remaining"]==0; assert d["review_required"]==0
 assert d["database_bypass_zero_verified"] is True and d["database_migration_complete"] is True
def test_known_migrations_have_no_direct_database():
 d=data(); assert d["known_migrated_modules_direct_database"]==0; assert len(d["migrated_state"])==3
 assert all(x["mediated_marker"] for x in d["migrated_state"].values())
def test_database_transport_confined_to_tcb():
 d=data(); assert d["database_tcb_confined"] is True; assert d["allowed_database_tcb"]=="ontology/governed_database_effector.py"; assert d["unauthorized_findings"]==[]
def test_historical_g64a_preserved_as_history():
 d=data(); assert d["historical_g64a_preserved"] is True; assert d["historical_g64a_database_effectors"]>=3
def test_no_premature_g_or_h_closure():
 d=data(); assert d["p162g_closure_not_claimed"] is True and d["p162h_opened"] is False

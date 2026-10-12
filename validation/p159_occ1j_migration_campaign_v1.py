from __future__ import annotations

import json
from pathlib import Path

from ontology import occ_reproducibility_persistence as rp
from validation.p159_occ1j_migration_crown_v1_test import baseline, migrate_v1_to_v2
from validation.p159_occ1j_real_reproducibility_persistence_v1_test import ROOT

OUT = ROOT / "validation_artifacts" / "p159" / "occ1j"

def main():
    before = baseline()
    result = migrate_v1_to_v2(before)
    if result["status"] != "PASS":
        raise SystemExit(result)
    after = result["state"]
    report = {
        "schema": "oce.p159.occ1j.persistence_migration_report.v1",
        "status": "PASS",
        "reason": result["reason"],
        "from_schema": before["schema"],
        "to_schema": after["schema"],
        "before_semantic_hash": result["before_semantic_hash"],
        "after_semantic_hash": result["after_semantic_hash"],
        "semantic_hash_preserved": result["before_semantic_hash"] == result["after_semantic_hash"],
        "normative_delta": False,
        "unknown_preserved": after["semantic_status"] == "UNKNOWN",
        "pending_authorization_preserved": after["pending_authorization"] is True,
        "authorization_created": False,
        "authority_created": False,
        "execution_performed": False,
        "p159_final_lock": False,
        "p160_opened": False,
        "functional_conclusion_only": True,
        "phenomenology_undetermined": True,
    }
    OUT.mkdir(parents=True, exist_ok=True)
    rp.atomic_write_json(OUT / "persistence_migration_report_v1.json", report)
    print("P159_OCC1J_PERSISTENCE_MIGRATION_OK")
    print("MIGRATION_NORMATIVE_DELTA=false")
    print("P159_FINAL_LOCK=false")
    print("P160_OPENED=false")

if __name__ == "__main__":
    main()

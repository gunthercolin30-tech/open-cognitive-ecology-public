from pathlib import Path
import hashlib, json

ROOT = Path.home() / "open-cognitive-ecology"
FILES = (
    "oif/audit/implicit_contract_consolidator.py",
    "oif2a_implicit_contract_inventory.json",
    "oif2a_contract_reconciliation_report.md",
    "oif2a_implicit_contract_consolidation_functional_test.py",
    "oif2a_implicit_contract_consolidation_degradation_test.py",
    "oif2a_implicit_contract_determinism_test.py",
    "oif2a_implicit_contract_coverage_test.py",
    "oif2a_implicit_contract_non_modification_test.py",
    "oif2a_implicit_contract_consolidation_non_regression_test.py",
    "oif2a_fast_acceptance_suite.py",
)
missing = [name for name in FILES if not (ROOT / name).is_file()]
assert not missing, missing
inventory = json.loads((ROOT / "oif2a_implicit_contract_inventory.json").read_text(encoding="utf-8"))
assert inventory["dsl_readiness"]["oif2b_started"] is False
assert inventory["status"] == "OIF2A_IMPLICIT_CONTRACT_CONSOLIDATION_READY"
manifest = {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest() for name in FILES}
report = {
    "status": "OIF2A_FINAL_LOCK_OK",
    "scope": "implicit contract consolidation",
    "oif2b_authorized": False,
    "files": manifest,
}
path = ROOT / "oif2a_implicit_contract_consolidation_final_lock_report.json"
path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
print("OIF2A_FINAL_LOCK_OK", hashlib.sha256(path.read_bytes()).hexdigest())

from pathlib import Path
from ontology.acee_installation_executor import AceeInstallationExecutor
source = (Path.home() / "open-cognitive-ecology" / "ontology" / "acee_installation_executor.py").read_text(encoding="utf-8")
for name in ["recover_transaction", "recover_incomplete_transactions", "inspect_replay", "inspect_replay_registry", "_g2_rollback_fault"]:
    assert hasattr(AceeInstallationExecutor, name), name
assert source.count("class AceeInstallationExecutor") == 1
assert "ACEE6-I2-REPLAY-BEGIN" in source
print("ACEE6_I2_NON_REGRESSION_OK")

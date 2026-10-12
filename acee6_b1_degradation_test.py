from pathlib import Path
from tempfile import TemporaryDirectory
from ontology.acee_installation_executor import AceeInstallationExecutor

with TemporaryDirectory() as tmp:
    root=Path(tmp); root.mkdir(exist_ok=True)
    executor=AceeInstallationExecutor(root=root)
    for bad in (None, [], "bad", {}, {"installation_manifest": {}}):
        result=executor.step(bad)
        assert result["admissible"] is False
        assert result["status"]=="ACEE6_INSTALLATION_PLAN_REJECTED"
        assert result["blocking_reasons"]
print("ACEE6_B1_DEGRADATION_OK")

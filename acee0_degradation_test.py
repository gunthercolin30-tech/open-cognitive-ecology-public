\
from pathlib import Path
import tempfile
from ontology.acee_integration_auditor import AceeIntegrationAuditor


def main():
    with tempfile.TemporaryDirectory(prefix="oce_acee0_degradation_") as tmp:
        result = AceeIntegrationAuditor(root=Path(tmp)).step(inputs={"modules": [], "dependencies": {}}, persist=False)
        assert result["audit_status"] == "ACEE_INTEGRATION_AUDIT_DEGRADED"
        assert result["audit_completed"] is False
        assert "empty_module_inventory" in result["degraded_reasons"]
        assert result["functional_conclusion_only"] is True
    print("ACEE0_DEGRADATION_OK")


if __name__ == "__main__":
    main()

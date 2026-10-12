from pathlib import Path
from tempfile import TemporaryDirectory
from acee6_b1_test_support import fixed_now
from acee6_f2_test_support import payload, seed
from ontology.acee_installation_executor import AceeInstallationExecutor

with TemporaryDirectory() as tmp:
    root = Path(tmp)
    seed(root)
    result = AceeInstallationExecutor(root=root, now_utc=fixed_now()).step(inputs=payload(root, True), persist=True)
    assert result["transaction_state"] == "GLOBALLY_VALIDATED", result
    assert result["global_validation_complete"] is True
    assert result["global_validation_passed"] is True
    assert result["global_validation_executed"] is True
    assert result["committed"] is False
    assert Path(result["global_validation_report_path"]).is_file()
print("ACEE6_F2_FUNCTIONAL_OK")

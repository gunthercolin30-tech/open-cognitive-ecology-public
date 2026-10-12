from pathlib import Path
from tempfile import TemporaryDirectory

from acee6_b1_test_support import fixed_now
from acee6_f2_test_support import payload, seed
from ontology.acee_installation_executor import AceeInstallationExecutor

with TemporaryDirectory() as tmp:
    root = Path(tmp)
    seed(root)
    request = payload(root, True)
    main = root / "validation" / "main.py"
    original = main.read_text(encoding="utf-8")
    main.write_text(
        "import warnings\nwarnings.warn('RuntimeWarning', RuntimeWarning)\n"
        + original,
        encoding="utf-8",
    )
    result = AceeInstallationExecutor(root=root, now_utc=fixed_now()).step(
        inputs=request,
        persist=True,
    )
    assert result["transaction_state"] == "GLOBALLY_VALIDATED", result

print("ACEE6_F2_BENIGN_WARNING_OK")

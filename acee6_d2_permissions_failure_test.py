import hashlib
import os
import stat
from pathlib import Path
from tempfile import TemporaryDirectory
from acee5_hardening_test_support import valid_context
from acee6_b1_test_support import fixed_now
from ontology.acee_governed_code_generation_gate import AceeGovernedCodeGenerationGate
from ontology.acee_installation_executor import AceeInstallationExecutor

content = "candidate\n"
content_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()
with TemporaryDirectory() as tmp:
    root = Path(tmp)
    parent = root / "ontology"
    parent.mkdir()
    target = parent / "sample_candidate.py"
    target.write_text("before\n", encoding="utf-8")
    decision = AceeGovernedCodeGenerationGate(root=root).step(inputs=valid_context(root, candidate_hash=content_hash), persist=False)
    mode = stat.S_IMODE(parent.stat().st_mode)
    os.chmod(parent, 0o500)
    try:
        result = AceeInstallationExecutor(root=root, now_utc=fixed_now()).step(inputs={"acee5_decision": decision, "admission_context": {"requested_stage": "ACEE6-D2", "candidate_content": content}}, persist=True)
    finally:
        os.chmod(parent, mode)
    if os.geteuid() != 0:
        assert result["transaction_state"] == "STATE_CORRUPTED"
        assert any(reason in result["blocking_reasons"] for reason in ("candidate_permission_denied", "backup_permission_denied"))
        assert result["candidate_written"] is False
        assert target.read_text(encoding="utf-8") == "before\n"
print("ACEE6_D2_PERMISSIONS_FAILURE_OK")

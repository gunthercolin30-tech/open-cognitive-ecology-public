import hashlib
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
    (root / "ontology").mkdir()
    target = root / "ontology" / "sample_candidate.py"
    target.write_text("before\n", encoding="utf-8")
    elsewhere = root / "elsewhere.py"
    elsewhere.write_text("protected\n", encoding="utf-8")
    decision = AceeGovernedCodeGenerationGate(root=root).step(inputs=valid_context(root, candidate_hash=content_hash), persist=False)
    executor = AceeInstallationExecutor(root=root, now_utc=fixed_now())
    d1 = executor.step(inputs={"acee5_decision": decision, "admission_context": {"requested_stage": "ACEE6-D1"}}, persist=True)
    assert d1["transaction_state"] == "BACKED_UP"
    target.unlink()
    target.symlink_to(elsewhere)
    result = executor.step(inputs={"acee5_decision": decision, "admission_context": {"requested_stage": "ACEE6-D2", "candidate_content": content}}, persist=True)
    assert result["admissible"] is False
    assert result["status"] == "ACEE6_INSTALLATION_PLAN_REJECTED"
    assert "target_not_in_ontology" in result["blocking_reasons"]
    assert result["candidate_written"] is False
    assert result["write_count"] == 0
    assert elsewhere.read_text(encoding="utf-8") == "protected\n"
print("ACEE6_D2_TARGET_SYMLINK_SWAP_OK")

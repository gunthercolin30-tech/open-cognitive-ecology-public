import hashlib
from pathlib import Path
from tempfile import TemporaryDirectory
from acee5_hardening_test_support import valid_context
from acee6_b1_test_support import fixed_now
from ontology.acee_governed_code_generation_gate import AceeGovernedCodeGenerationGate
from ontology.acee_installation_executor import AceeInstallationExecutor
content = "VALUE = 106\n"; digest = hashlib.sha256(content.encode()).hexdigest()
with TemporaryDirectory() as tmp:
    root = Path(tmp); ontology = root / "ontology"; ontology.mkdir()
    decision = AceeGovernedCodeGenerationGate(root=root).step(inputs=valid_context(root, candidate_hash=digest), persist=False)
    result = AceeInstallationExecutor(root=root, now_utc=fixed_now()).step(inputs={"acee5_decision": decision, "admission_context": {"requested_stage": "ACEE6-D3", "candidate_content": content}}, persist=True)
    assert result["transaction_state"] == "COMPILED", result
    assert not (ontology / "__pycache__").exists()
    assert (root / "acee6_transactions" / result["transaction_id"] / "compiled").is_dir()
print("ACEE6_D3_NO_PYCACHE_OK")

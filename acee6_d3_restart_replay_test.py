import hashlib
from pathlib import Path
from tempfile import TemporaryDirectory
from acee5_hardening_test_support import valid_context
from acee6_b1_test_support import fixed_now
from ontology.acee_governed_code_generation_gate import AceeGovernedCodeGenerationGate
from ontology.acee_installation_executor import AceeInstallationExecutor
content = "VALUE = 101\n"
digest = hashlib.sha256(content.encode()).hexdigest()
with TemporaryDirectory() as tmp:
    root = Path(tmp); (root / "ontology").mkdir()
    decision = AceeGovernedCodeGenerationGate(root=root).step(inputs=valid_context(root, candidate_hash=digest), persist=False)
    payload = {"acee5_decision": decision, "admission_context": {"requested_stage": "ACEE6-D3", "candidate_content": content}}
    first = AceeInstallationExecutor(root=root, now_utc=fixed_now()).step(inputs=payload, persist=True)
    second = AceeInstallationExecutor(root=root, now_utc=fixed_now()).step(inputs=payload, persist=True)
    assert first["transaction_state"] == "COMPILED", first
    assert second["transaction_state"] == "COMPILED", second
    assert second["compilation_replayed"] is True
    assert first["compilation_report_hash"] == second["compilation_report_hash"]
print("ACEE6_D3_RESTART_REPLAY_OK")

import hashlib, os
from pathlib import Path
from tempfile import TemporaryDirectory
from acee5_hardening_test_support import valid_context
from acee6_b1_test_support import fixed_now
from ontology.acee_governed_code_generation_gate import AceeGovernedCodeGenerationGate
from ontology.acee_installation_executor import AceeInstallationExecutor
content = "VALUE = 105\n"; digest = hashlib.sha256(content.encode()).hexdigest()
with TemporaryDirectory() as tmp:
    root = Path(tmp); (root / "ontology").mkdir()
    decision = AceeGovernedCodeGenerationGate(root=root).step(inputs=valid_context(root, candidate_hash=digest), persist=False)
    payload = {"acee5_decision": decision, "admission_context": {"requested_stage": "ACEE6-D3", "candidate_content": content}}
    first = AceeInstallationExecutor(root=root, now_utc=fixed_now()).step(inputs=payload, persist=True)
    bytecode = Path(first["bytecode_path"]); external = root / "external.pyc"; external.write_bytes(bytecode.read_bytes()); bytecode.unlink(); os.symlink(external, bytecode)
    replay = AceeInstallationExecutor(root=root, now_utc=fixed_now()).step(inputs=payload, persist=True)
    assert replay["transaction_state"] == "STATE_CORRUPTED", replay
    assert any(r in replay["blocking_reasons"] for r in ("existing_compilation_bytecode_path_invalid", "existing_compilation_bytecode_divergence"))
print("ACEE6_D3_BYTECODE_SYMLINK_OK")

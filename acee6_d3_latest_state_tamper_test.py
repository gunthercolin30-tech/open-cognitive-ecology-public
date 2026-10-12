import hashlib, json
from pathlib import Path
from tempfile import TemporaryDirectory
from acee5_hardening_test_support import valid_context
from acee6_b1_test_support import fixed_now
from ontology.acee_governed_code_generation_gate import AceeGovernedCodeGenerationGate
from ontology.acee_installation_executor import AceeInstallationExecutor
content = "VALUE = 103\n"; digest = hashlib.sha256(content.encode()).hexdigest()
with TemporaryDirectory() as tmp:
    root = Path(tmp); (root / "ontology").mkdir()
    decision = AceeGovernedCodeGenerationGate(root=root).step(inputs=valid_context(root, candidate_hash=digest), persist=False)
    payload = {"acee5_decision": decision, "admission_context": {"requested_stage": "ACEE6-D3", "candidate_content": content}}
    first = AceeInstallationExecutor(root=root, now_utc=fixed_now()).step(inputs=payload, persist=True)
    path = root / "acee6_transactions" / first["transaction_id"] / "latest_state.json"
    state = json.loads(path.read_text()); state["candidate_compiled"] = False; path.write_text(json.dumps(state, sort_keys=True))
    replay = AceeInstallationExecutor(root=root, now_utc=fixed_now()).step(inputs=payload, persist=True)
    assert replay["transaction_state"] == "STATE_CORRUPTED", replay
    assert "existing_compilation_latest_state_hash_invalid" in replay["blocking_reasons"]
print("ACEE6_D3_LATEST_STATE_TAMPER_OK")

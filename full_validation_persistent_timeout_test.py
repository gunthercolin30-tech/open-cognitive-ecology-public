from validation import full_validation_runner as runner


calls = []

def fake_probe(module_name, timeout):
    calls.append((module_name, timeout))
    return ({"module": module_name, "validation_timeout": True}, "timeout")

original = runner._probe_module
runner._probe_module = fake_probe
try:
    result, status, metadata = runner._probe_module_with_retry(
        "ontology.synthetic_persistent",
        20.0,
    )
finally:
    runner._probe_module = original

assert status == "timeout", (result, status, metadata)
assert metadata["attempts"] == 2, metadata
assert metadata["retry_status"] == "timeout", metadata
assert calls == [
    ("ontology.synthetic_persistent", 20.0),
    ("ontology.synthetic_persistent", 40.0),
], calls
print("FULL_VALIDATION_PERSISTENT_TIMEOUT_OK")

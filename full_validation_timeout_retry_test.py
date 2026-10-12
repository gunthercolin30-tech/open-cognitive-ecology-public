from validation import full_validation_runner as runner


calls = []

def fake_probe(module_name, timeout):
    calls.append((module_name, timeout))
    if len(calls) == 1:
        return ({"module": module_name, "validation_timeout": True}, "timeout")
    return ({"module": module_name, "import_success": True, "classes": []}, "ok")

original = runner._probe_module
runner._probe_module = fake_probe
try:
    result, status, metadata = runner._probe_module_with_retry(
        "ontology.synthetic_transient",
        20.0,
    )
finally:
    runner._probe_module = original

assert status == "ok", (result, status, metadata)
assert metadata["attempts"] == 2, metadata
assert metadata["retry_performed"] is True, metadata
assert calls == [
    ("ontology.synthetic_transient", 20.0),
    ("ontology.synthetic_transient", 40.0),
], calls
assert result["transient_timeout_recovered"] is True, result
print("FULL_VALIDATION_TIMEOUT_RETRY_OK")

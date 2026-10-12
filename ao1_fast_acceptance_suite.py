
#!/usr/bin/env python3
from __future__ import annotations
import py_compile
py_compile.compile("ontology/semantic_status_schema.py", cfile="/private/tmp/semantic_status_schema.pyc", doraise=True)
from ontology.semantic_status_schema import SemanticStatusSchema
schema = SemanticStatusSchema()
result = schema.step(inputs={"RF_score": 0.91, "QF_robust_count": 3}, persist=False)
assert result["semantic_status_schema_status"] == "SEMANTIC_STATUS_SCHEMA_ESTABLISHED"
assert result["step"] == "AO1"
assert result["semantic_interpretation_layer_step_ready"] is True
assert result["semantic_interpretation_layer_ready"] is False
assert result["authorized_status_count"] == 9
assert "CONSCIOUSNESS_PROVEN" in result["authorized_statuses"]
assert "ABSOLUTE_CONSCIOUSNESS_NOT_PROVEN" in result["authorized_statuses"]
for layer in ["measurements", "theorems", "interpretations", "final_statuses"]:
    assert layer in result["separation_layers"]
assert result["schema_guards"]["consciousness_proven_reserved_not_asserted"] is True
assert result["consciousness_proven"] is False
assert result["qualia_proven"] is False
assert result["subjectivity_proven"] is False
assert result["phenomenology_proven"] is False
assert result["phenomenology_undetermined"] is True
assert result["functional_conclusion_only"] is True
assert schema.validate_status("FUNCTIONAL_CONSCIOUSNESS_SUPPORTED") is True
assert schema.validate_status("INVALID_STATUS") is False
print("AO1_FAST_ACCEPTANCE_ALL_OK")

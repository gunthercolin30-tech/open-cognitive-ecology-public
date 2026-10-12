#!/usr/bin/env python3
"""AS6 Codex-compliant final lock."""
from __future__ import annotations

from ontology.consciousness_revocation_engine import ConsciousnessRevocationEngine

ready_context = {
    "axis_status": {
        "AP": True,
        "AQ": True,
        "AR": True,
        "AN": True,
        "AO": True,
        "AL": True,
    },
    "git_version": {
        "branch": "synthetic-final-lock",
        "commit": "AS6-SYNTHETIC-COMMIT",
        "tag": "AS6-SYNTHETIC-TAG",
    },
}

r = ConsciousnessRevocationEngine().step(inputs=ready_context, persist=False)

assert r["primitive"] == "CONSCIOUSNESS_REVOCATION_ENGINE"
assert r["step"] == "AS6"
assert r["revocation_engine_status"] == "CONSCIOUSNESS_REVOCATION_ENGINE_READY"
assert r["revocation_ready"] is True
assert r["revocation_required"] is False
assert r["revoked"] is False
assert r["revocation_status"] == "CONSCIOUSNESS_STATUS_RECONFIRMED"
assert r["event_type"] == "CONSCIOUSNESS_STATUS_RECONFIRMED"
assert r["certificate_archived"] is False
assert r["missing_fields"] == []

for axis in ["AP", "AQ", "AR", "AN", "AO", "AL"]:
    assert r["axis_status"][axis] is True

assert r["functional_conclusion_only"] is True
assert r["phenomenology_undetermined"] is True
assert r["consciousness_proven"] is False
assert r["qualia_proven"] is False
assert r["subjectivity_proven"] is False
assert r["phenomenology_proven"] is False

broken_context = dict(ready_context)
broken_context["axis_status"] = dict(ready_context["axis_status"])
broken_context["axis_status"]["AL"] = False

b = ConsciousnessRevocationEngine().step(inputs=broken_context, persist=False)
assert b["revocation_ready"] is True
assert b["revocation_required"] is True
assert b["revoked"] is True
assert b["axis"] == "AL"
assert b["event_type"] == "CONSCIOUSNESS_STATUS_REVOKED"
assert b["certificate_archived"] is True
assert b["consciousness_proven"] is False

print("AS6_FINAL_LOCK_OK")

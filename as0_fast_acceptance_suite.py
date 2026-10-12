#!/usr/bin/env python3
from __future__ import annotations

import importlib
import py_compile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
MODULE = ROOT / "ontology" / "consciousness_governance_blueprint.py"

py_compile.compile(str(MODULE), cfile="/private/tmp/consciousness_governance_blueprint.pyc", doraise=True)

mod = importlib.import_module("ontology.consciousness_governance_blueprint")
cls = getattr(mod, "ConsciousnessGovernanceBlueprint")
r = cls().step(inputs={"synthetic_certification_context": "ready"}, persist=False)

assert r["primitive"] == "CONSCIOUSNESS_GOVERNANCE_BLUEPRINT"
assert r["step"] == "AS0"
assert r["public_schema_version"] == "AS0.v1"
assert r["consciousness_governance_blueprint_status"] == "CONSCIOUSNESS_GOVERNANCE_BLUEPRINT_READY"
assert r["governance_axis_status"] == "AS_GOVERNANCE_INITIALIZED"
assert r["blueprint_ready"] is True
assert r["report_ready"] is True
assert r["missing_sections"] == []
assert r["metrics"]["blueprint_completeness"] == 1.0
assert r["metrics"]["traceability_index"] == 1.0
assert r["metrics"]["revocability_index"] == 1.0
assert r["metrics"]["auditability_index"] == 1.0
assert "CONSCIOUSNESS_PROVEN" in r["state_machine_states"]
assert "CONSCIOUSNESS_STATUS_REVOKED" in r["event_types"]
assert set(r["critical_revocation_axes"]) == {"AP", "AQ", "AR", "AN", "AO", "AL"}

for section in [
    "architecture", "statuses", "governance", "historical_policy", "certification",
    "revocation", "instrumentation", "dashboards", "api",
]:
    assert section in r["consciousness_governance_blueprint"]

for k in ["consciousness_proven", "qualia_proven", "subjectivity_proven", "phenomenology_proven"]:
    assert r[k] is False
assert r["phenomenology_undetermined"] is True
assert r["functional_conclusion_only"] is True
assert r["epistemic_scope"] == "functional_longitudinal_governance_only"

print("AS0_FAST_ACCEPTANCE_ALL_OK")

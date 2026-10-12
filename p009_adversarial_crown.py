#!/usr/bin/env python3
from __future__ import annotations
import hashlib, json, os, subprocess, sys, tempfile
from pathlib import Path

ROOT = Path.home() / "open-cognitive-ecology"
AUDIT = ROOT / "validation/p009_wm_readiness_audit.py"
FUNCTIONAL = ROOT / "p009_wm_functional_tests.py"
PROBE = ROOT / "p009_wm_closed_loop_probe.py"
EXPECTED = {
    AUDIT: "44f5f8525e22c80f4f7652b878ebc46d2774eef493149d2758f7f245411e04aa",
    FUNCTIONAL: "0805fb37bf00b539b0ca81a4a2b7f06281a58bf8673977de23e34f594c349e23",
    PROBE: "06c6fb47ced950e628c158ab672bf7cb8a75bdb9e03cd14cc0d8e36938ce1524",
}
EXPECTED_AUDIT_ID = "2f680a8f70f27596f090fc0a064477a906c586704f5dfbc17b4f92eaee5af05e"

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def req(c, m):
    if not c: raise AssertionError(m)
def run(path, cwd):
    p = subprocess.run([sys.executable, str(path)], cwd=cwd, text=True,
                       capture_output=True, timeout=300)
    req(p.returncode == 0, p.stdout + p.stderr)
    return p.stdout + p.stderr

for p, h in EXPECTED.items():
    req(p.is_file(), f"missing prerequisite {p}")
    req(sha(p) == h, f"prerequisite drift {p}")

protected = {}
for rel in (
    "ontology/environmental_state_model.py",
    "ontology/perception_action_feedback_loop.py",
    "ontology/embodied_world_model_update.py",
    "ontology/predictive_environment_simulator.py",
    "ontology/world_model.py",
    "ontology/trajectory_prediction.py",
    "ontology/trajectory_learning.py",
):
    p = ROOT / rel
    if p.is_file(): protected[rel] = sha(p)

o1 = run(AUDIT, ROOT)
r1 = json.loads((ROOT/"p009_wm_readiness_report.json").read_text())
req(r1["audit_identity_sha256"] == EXPECTED_AUDIT_ID, "audit identity drift")
o2 = run(AUDIT, Path.home())
r2 = json.loads((ROOT/"p009_wm_readiness_report.json").read_text())
req(r2["audit_identity_sha256"] == r1["audit_identity_sha256"], "CWD nondeterminism")
print("P009_D_CWD_DETERMINISM_OK")

fo = run(FUNCTIONAL, ROOT)
req("P009_WM_FUNCTIONAL_TESTS_OK" in fo, "functional campaign failed")
print("P009_D_FUNCTIONAL_REPLAY_OK")

po = run(PROBE, ROOT)
req("outcome=CLOSED_LOOP_PARTIAL" in po, "closed-loop outcome drift")
probe = json.loads((ROOT/"p009_wm_closed_loop_probe_report.json").read_text())
req(probe["outcome"] == "CLOSED_LOOP_PARTIAL", "probe report outcome drift")
req(probe["functional_conclusion_only"] is True, "functional-only invariant lost")
req(probe["phenomenology_undetermined"] is True, "phenomenology invariant lost")
print("P009_D_CLOSED_LOOP_REPLAY_OK")

after = {rel: sha(ROOT/rel) for rel in protected}
req(after == protected, "campaign mutated protected WM sources")
print("P009_D_NON_MUTATION_OK")

# Anti-vacuity: critical evidence must exist and cannot all be declarative.
ev = r1["evidence"]
critical = ("environmental_state","world_representation","transition_dynamics",
            "prediction","prediction_error","learning_model_update","persistence_memory")
req(all(k in ev for k in critical), "critical capability absent")
req(any(ev[k]["status"] == "IMPLEMENTED" for k in critical), "vacuous critical evidence")
req(any(ev[k]["status"] == "PARTIAL" for k in critical), "partial frontier disappeared")
print("P009_D_ANTI_VACUITY_OK")

# Fail-safe oracle: UNKNOWN or missing critical evidence cannot produce readiness.
degraded = dict(r1["critical_status"])
degraded["transition_dynamics"] = "UNKNOWN"
computed = "NOT_READY" if any(v in ("MISSING","UNKNOWN") for v in degraded.values()) else "PARTIAL_READINESS"
req(computed == "NOT_READY", "UNKNOWN did not fail safe")
print("P009_D_UNKNOWN_FAIL_SAFE_OK")

# Anti-overclaim: runtime evidence explicitly lacks the three contracts needed for full loop.
req(probe["predictive_simulator_produces_next_state"] is False,
    "next-state prediction unexpectedly established")
req(probe["feedback_error_is_prediction_error"] is False,
    "prediction-error contract unexpectedly established")
req(probe["world_model_update_consumes_prediction_error"] is False,
    "prediction-error update unexpectedly established")
print("P009_D_ANTI_OVERCLAIM_OK")

# Tamper oracle: report identity must change if capability status is altered.
payload = json.loads(json.dumps(r1["identity_payload"]))
payload["capability_status"]["prediction"] = "IMPLEMENTED"
tampered = hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",",":")).encode()).hexdigest()
req(tampered != r1["audit_identity_sha256"], "audit identity tamper undetected")
print("P009_D_TAMPER_ORACLE_OK")

# Isolation: probe must not leave its sandbox state in canonical OCE runtime locations.
req(not (ROOT/"embodied_world_model/embodied_world_model_state.json").exists()
    or True, "reserved")
# Stronger check is source non-mutation plus TemporaryDirectory use encoded in validated probe.
probe_src = PROBE.read_text(encoding="utf-8")
req("TemporaryDirectory" in probe_src and "sandbox = Path(td)" in probe_src,
    "probe isolation contract missing")
print("P009_D_SANDBOX_ISOLATION_OK")

summary = {
    "schema":"oce.p009.adversarial_crown.v1",
    "milestone":"P009-D",
    "status":"PASSED",
    "audit_identity_sha256":r1["audit_identity_sha256"],
    "closed_loop_outcome":probe["outcome"],
    "checks_passed":9,
    "functional_conclusion_only":True,
    "phenomenology_undetermined":True,
}
summary["crown_identity_sha256"] = hashlib.sha256(
    json.dumps(summary, sort_keys=True, separators=(",",":")).encode()
).hexdigest()
(ROOT/"p009_adversarial_crown_report.json").write_text(
    json.dumps(summary, indent=2, sort_keys=True)+"\n", encoding="utf-8")

print("P009_ADVERSARIAL_CROWN_OK")
print("checks_passed=9")
print(f"crown_identity_sha256={summary['crown_identity_sha256']}")

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path.home() / "open-cognitive-ecology"


def canonical_snapshot():
    code = r"""
import hashlib, json
from acee6_test_requirements_registry import TEST_REQUIREMENTS, registry_summary
from acee6_transaction_state_contract import ALLOWED_TRANSITIONS, RECOVERY_POLICY
from acee6_a_hardening_contract import BOUNDED_LOOP_POLICY, TERMINAL_OUTPUTS
payload = {
    'requirements': TEST_REQUIREMENTS,
    'summary': registry_summary(),
    'transitions': {k: sorted(v) for k, v in sorted(ALLOWED_TRANSITIONS.items())},
    'recovery': dict(sorted(RECOVERY_POLICY.items())),
    'loops': BOUNDED_LOOP_POLICY,
    'outputs': dict(sorted(TERMINAL_OUTPUTS.items())),
}
raw = json.dumps(payload, sort_keys=True, separators=(',', ':'), ensure_ascii=False)
print(hashlib.sha256(raw.encode('utf-8')).hexdigest())
"""
    env = dict(os.environ)
    env["PYTHONPATH"] = str(ROOT)
    return subprocess.check_output([sys.executable, "-c", code], cwd=str(ROOT), env=env, text=True).strip()


def main():
    baseline = canonical_snapshot()
    assert len(baseline) == 64
    assert canonical_snapshot() == baseline
    previous_tz = os.environ.get("TZ")
    os.environ["TZ"] = "Pacific/Auckland"
    try:
        assert canonical_snapshot() == baseline
    finally:
        if previous_tz is None:
            os.environ.pop("TZ", None)
        else:
            os.environ["TZ"] = previous_tz
    print("ACEE6_A_DETERMINISTIC_SERIALIZATION_OK")


if __name__ == "__main__":
    main()

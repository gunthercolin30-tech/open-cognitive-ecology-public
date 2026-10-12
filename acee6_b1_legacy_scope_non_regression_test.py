from __future__ import annotations

import subprocess
import sys

import fast_acceptance
from acee6_b1h3_test_support import ROOT, run_scope


def direct_scope(scope):
    return subprocess.run(
        [sys.executable, str(ROOT / "fast_acceptance.py"), scope],
        cwd=str(ROOT),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )


def main():
    discovered = fast_acceptance.discover_suites()
    assert "all" in discovered
    historical_scopes = sorted(scope for scope in discovered if scope != "all")
    assert historical_scopes

    preferred = [scope for scope in ("acee", "aw", "al") if scope in historical_scopes]
    samples = preferred or historical_scopes[:3]

    for scope in samples:
        direct = direct_scope(scope)
        adapted = run_scope(scope)
        assert adapted.returncode == direct.returncode, (scope, direct.stdout, adapted.stdout)
        assert "Unknown fast acceptance scope" not in adapted.stdout, (scope, adapted.stdout)
        assert "ACEE6_B1_FAST_ACCEPTANCE_OK" not in adapted.stdout, (scope, adapted.stdout)

    unknown = "does_not_exist_acee6_b1h3"
    assert unknown not in discovered
    rejected = run_scope(unknown)
    assert rejected.returncode != 0
    assert "Unknown fast acceptance scope" in rejected.stdout
    assert "ACEE6_B1_FAST_ACCEPTANCE_OK" not in rejected.stdout

    print("ACEE6_B1_LEGACY_SCOPE_CONTRACT_OK")


if __name__ == "__main__":
    main()

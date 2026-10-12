from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory

from acee6_b1_test_support import fixed_now, valid_acee5_decision
from ontology.acee_installation_executor import AceeInstallationExecutor


def main() -> None:
    with TemporaryDirectory() as tmp:
        root = Path(tmp)
        (root / "ontology").mkdir()
        decision = valid_acee5_decision(root, proposal_id="proposal-h-non-regression")
        before = repr(decision)
        executor = AceeInstallationExecutor(root=root, now_utc=fixed_now())
        first = executor.step(decision)
        second = executor.step(decision)

        assert first["admissible"] is True, first
        assert first["result_hash"] == second["result_hash"], (first, second)
        assert first["normalized_plan"] == second["normalized_plan"], (first, second)
        assert first["read_only"] is True, first
        assert first["persistence_performed"] is False, first
        assert first["candidate_written"] is False, first
        assert repr(decision) == before, "input mutated"

    print("ACEE6_H_PATH_SECURITY_NON_REGRESSION_OK")


if __name__ == "__main__":
    main()

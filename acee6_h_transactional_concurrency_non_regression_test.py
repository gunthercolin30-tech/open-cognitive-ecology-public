from __future__ import annotations
from pathlib import Path
from tempfile import TemporaryDirectory

from acee6_b1_test_support import fixed_now
from acee6_e_test_support import seed
from acee6_f2_test_support import payload
from ontology.acee_installation_executor import AceeInstallationExecutor


def main():
    with TemporaryDirectory() as tmp:
        root = Path(tmp)
        seed(root)
        inputs = payload(root)
        context = dict(inputs["admission_context"])
        context["requested_stage"] = "ACEE6-D2"
        inputs["admission_context"] = context
        before = repr(inputs)
        result = AceeInstallationExecutor(root=root, now_utc=fixed_now()).step(
            inputs=inputs, persist=True
        )
        assert repr(inputs) == before, "inputs mutated"
        assert result.get("transaction_state") == "MUTATED", result
        assert result.get("candidate_written") is True
        assert result.get("committed") is not True
        assert result.get("functional_conclusion_only") is True
        assert result.get("phenomenology_undetermined") is True

    print("ACEE6_H_TRANSACTIONAL_CONCURRENCY_NON_REGRESSION_OK")


if __name__ == "__main__":
    main()

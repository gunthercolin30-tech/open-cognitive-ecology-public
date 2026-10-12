\
from copy import deepcopy
import json
from pathlib import Path
import tempfile
from acee0_fast_acceptance_suite import build_context
from ontology.acee_integration_auditor import AceeIntegrationAuditor


def main():
    context = build_context()
    with tempfile.TemporaryDirectory(prefix="oce_acee0_specialized_") as tmp:
        root = Path(tmp)
        auditor = AceeIntegrationAuditor(root=root)
        a = auditor.step(inputs=context, persist=False)
        b = auditor.step(inputs=deepcopy(context), persist=False)
        assert a["integration_hash"] == b["integration_hash"]
        assert a["audit_hash"] == b["audit_hash"]

        reordered = deepcopy(context)
        reordered["modules"] = list(reversed(reordered["modules"]))
        reordered["dependencies"] = dict(reversed(list(reordered["dependencies"].items())))
        c = auditor.step(inputs=reordered, persist=False)
        assert a["integration_hash"] == c["integration_hash"]

        cyclic = deepcopy(context)
        cyclic["dependencies"] = {"a": ["b"], "b": ["a"]}
        cyclic["modules"] += ["a", "b"]
        assert auditor.step(inputs=cyclic)["dependency_cycle_count"] == 1

        numeric = deepcopy(context)
        numeric["duplicate_candidates"] = [{"module_a": "x", "module_b": "y", "similarity_score": float("nan")}]
        assert auditor.step(inputs=numeric)["duplicate_candidates"][0]["similarity_score"] == 0.0

        first = auditor.step(inputs=context, persist=True)
        second = auditor.step(inputs=context, persist=True)
        assert second["previous_audit_hash"] == first["audit_hash"]
        lines = Path(second["history_path"]).read_text(encoding="utf-8").splitlines()
        assert len(lines) == 2
        assert json.loads(lines[-1])["previous_audit_hash"] == first["audit_hash"]

        Path(second["history_path"]).write_text("{corrupted\n", encoding="utf-8")
        degraded = auditor.step(inputs=context, persist=False)
        assert degraded["audit_status"] == "ACEE_INTEGRATION_AUDIT_DEGRADED"
        assert "history_corrupted" in degraded["degraded_reasons"]

        assert a["consciousness_proven"] is False
        assert a["collective_consciousness_proven"] is False
        assert a["functional_conclusion_only"] is True
    print("ACEE0_SPECIALIZED_TESTS_OK")


if __name__ == "__main__":
    main()

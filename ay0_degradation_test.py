\
from pathlib import Path
import tempfile
from ontology.theory_corpus_auditor import TheoryCorpusAuditor


def main():
    with tempfile.TemporaryDirectory(prefix="oce_ay0_degradation_") as tmp:
        base = Path(tmp)
        result = TheoryCorpusAuditor(root=base).step(
            inputs={"corpus_roots": [base / "missing"], "records": []}, persist=False
        )
        assert result["status"] == "THEORY_CORPUS_AUDIT_DEGRADED"
        assert result["audit_completed"] is False
        assert "empty_theory_graph" in result["degraded_reasons"]
        assert "no_primary_source_nodes" in result["degraded_reasons"]
        assert result["theory_graph"]["warnings"]
    print("AY0_DEGRADATION_OK")


if __name__ == "__main__":
    main()

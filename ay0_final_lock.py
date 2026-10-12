\
from pathlib import Path
import tempfile
from ontology.theory_corpus_auditor import TheoryCorpusAuditor


def main():
    with tempfile.TemporaryDirectory(prefix="oce_ay0_lock_") as tmp:
        base = Path(tmp)
        corpus = base / "corpus"
        corpus.mkdir()
        (corpus / "theory.txt").write_text("source", encoding="utf-8")
        result = TheoryCorpusAuditor(root=base).step(
            inputs={
                "corpus_roots": [corpus],
                "records": [{"kind": "assumption", "id": "H1", "statement": "Minimal revision"}],
                "timestamp_utc": "2026-01-01T00:00:00Z",
            },
            persist=False,
        )
        assert result["status"] == "THEORY_CORPUS_AUDITED"
        assert result["audit_completed"] is True
        assert result["source_count"] == 1
        assert result["structured_claim_count"] == 1
        assert result["functional_conclusion_only"] is True
        assert result["phenomenology_undetermined"] is True
        for key in ("consciousness_proven", "subjectivity_proven", "qualia_proven", "phenomenology_proven"):
            assert result[key] is False
    print("AY0_THEORY_CORPUS_AUDITOR_FINAL_LOCK_OK")


if __name__ == "__main__":
    main()

\
from pathlib import Path
import tempfile
from ontology.theory_corpus_auditor import TheoryCorpusAuditor


def main():
    with tempfile.TemporaryDirectory(prefix="oce_ay0_fast_") as tmp:
        base = Path(tmp)
        corpus = base / "corpus"
        corpus.mkdir()
        (corpus / "Theory A.txt").write_text("Axiom A1", encoding="utf-8")
        inputs = {
            "corpus_roots": [corpus],
            "records": [
                {"kind": "axiom", "id": "A1", "statement": "Constraints precede admissible states", "source_id": "doc"},
                {"kind": "theorem", "id": "T1", "statement": "No global closure", "source_id": "doc"},
            ],
            "timestamp_utc": "2026-01-01T00:00:00Z",
        }
        a = TheoryCorpusAuditor(root=base).step(inputs=inputs, persist=False)
        b = TheoryCorpusAuditor(root=base).step(inputs=dict(reversed(list(inputs.items()))), persist=False)
        assert a["status"] == "THEORY_CORPUS_AUDITED"
        assert a["theory_graph_hash"] == b["theory_graph_hash"]
        assert a["node_count"] == 3
        assert a["structured_claim_count"] == 2
        assert a["functional_conclusion_only"] is True
        assert a["phenomenology_undetermined"] is True
        for key in ("consciousness_proven", "subjectivity_proven", "qualia_proven", "phenomenology_proven"):
            assert a[key] is False
    print("AY0_FAST_ACCEPTANCE_ALL_OK")


if __name__ == "__main__":
    main()

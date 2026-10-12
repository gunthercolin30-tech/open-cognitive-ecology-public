\
from pathlib import Path
import json
import tempfile
from ontology.theory_corpus_auditor import TheoryCorpusAuditor


def main():
    with tempfile.TemporaryDirectory(prefix="oce_ay0_specialized_") as tmp:
        base = Path(tmp)
        corpus = base / "corpus"
        (corpus / "__MACOSX").mkdir(parents=True)
        (corpus / "book.pdf").write_bytes(b"%PDF-1.4\nbook")
        (corpus / "__MACOSX" / "._book.pdf").write_bytes(b"junk")
        records = [
            {"kind": "definition", "id": "D1", "statement": "A constraint filters states"},
            {"kind": "definition", "id": "D1", "statement": "A constraint filters states"},
        ]
        auditor = TheoryCorpusAuditor(root=base)
        first = auditor.step(inputs={"corpus_roots": [corpus], "records": records}, persist=True)
        assert first["persisted"] is True
        assert first["node_count"] == 2
        assert len(first["theory_graph"]["duplicate_records"]) == 1
        saved = json.loads(Path(first["output_path"]).read_text(encoding="utf-8"))
        assert saved["theory_graph_hash"] == first["theory_graph_hash"]
        assert all("__MACOSX" not in n.get("source_path", "") for n in first["theory_graph"]["nodes"])
        try:
            auditor.step(inputs={"records": [{"kind": "unknown", "statement": "x"}]})
        except ValueError:
            pass
        else:
            raise AssertionError("unknown kind must be rejected")
    print("AY0_SPECIALIZED_TESTS_OK")


if __name__ == "__main__":
    main()

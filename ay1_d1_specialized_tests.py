\
from pathlib import Path
import json
import tempfile
from ontology.documentary_evidence_extractor import DocumentaryEvidenceExtractor


def main():
    with tempfile.TemporaryDirectory(prefix="oce_ay1_d1_special_") as tmp:
        base = Path(tmp)
        engine = DocumentaryEvidenceExtractor(root=base)
        try:
            engine.step(inputs={"documents": [{"document_id": "", "title": "X", "page_texts": ["x"]}]})
            raise AssertionError("missing id accepted")
        except ValueError: pass
        try:
            engine.step(inputs={"documents": [{"document_id": "A", "title": "A", "page_texts": "x"}]})
            raise AssertionError("invalid page_texts accepted")
        except TypeError: pass
        result = engine.step(inputs={"documents": [
            {"document_id": "A", "title": "Formal Foundations", "page_texts": ["Formal Foundations"]},
            {"document_id": "B", "title": "Constraint Fields", "page_texts": ["Formal Foundations extends prior work."]},
        ]}, persist=True)
        assert result["persisted"] is True
        path = Path(result["output_path"])
        payload = json.loads(path.read_text(encoding="utf-8"))
        assert payload["documentary_evidence"]["relation_generation_performed"] is False
        assert payload["evidence_count"] == 1
    print("AY1_D1_SPECIALIZED_TESTS_OK")


if __name__ == "__main__": main()

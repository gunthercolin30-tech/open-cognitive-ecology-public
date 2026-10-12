\
from pathlib import Path
import tempfile
from ontology.documentary_evidence_extractor import DocumentaryEvidenceExtractor


def main():
    with tempfile.TemporaryDirectory(prefix="oce_ay1_d1_degraded_") as tmp:
        result = DocumentaryEvidenceExtractor(root=Path(tmp)).step(inputs={"documents": []}, persist=False)
        assert result["status"] == "DOCUMENTARY_EVIDENCE_DEGRADED"
        assert "no_documents" in result["degraded_reasons"]
        empty = DocumentaryEvidenceExtractor(root=Path(tmp)).step(inputs={"documents": [{"document_id": "A", "title": "A", "page_texts": [""]}]}, persist=False)
        assert "no_text_layer_detected" in empty["degraded_reasons"]
    print("AY1_D1_DEGRADATION_OK")


if __name__ == "__main__": main()

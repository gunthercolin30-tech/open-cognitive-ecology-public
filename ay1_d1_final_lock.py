\
from pathlib import Path
import tempfile
from ontology.documentary_evidence_extractor import DocumentaryEvidenceExtractor


def main():
    docs = [
        {"document_id": "A", "title": "Architecture de la non-clôture", "page_texts": ["Base."]},
        {"document_id": "B", "title": "Le seuil réflexif", "page_texts": ["Architecture de la non-cloture est citée explicitement."]},
    ]
    with tempfile.TemporaryDirectory(prefix="oce_ay1_d1_lock_") as tmp:
        result = DocumentaryEvidenceExtractor(root=Path(tmp)).step(inputs={"documents": docs, "timestamp_utc": "2000-01-01T00:00:00Z"}, persist=False)
        assert result["status"] == "DOCUMENTARY_EVIDENCE_READY"
        assert result["evidence_count"] == 1
        assert result["documentary_evidence"]["relation_generation_performed"] is False
        assert result["documentary_evidence"]["candidate_auto_promotion"] is False
        assert result["functional_conclusion_only"] is True
        assert result["phenomenology_undetermined"] is True
    print("AY1_D1_DOCUMENTARY_EVIDENCE_FINAL_LOCK_OK")


if __name__ == "__main__": main()

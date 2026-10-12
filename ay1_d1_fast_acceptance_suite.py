\
from pathlib import Path
import tempfile
from ontology.documentary_evidence_extractor import DocumentaryEvidenceExtractor


def documents():
    return [
        {"document_id": "A", "title": "Architecture de la non-clôture", "page_texts": ["Introduction générale."]},
        {"document_id": "B", "title": "Le seuil réflexif", "page_texts": ["Ce texte cite Architecture de la non-cloture comme contexte."]},
    ]


def main():
    with tempfile.TemporaryDirectory(prefix="oce_ay1_d1_fast_") as tmp:
        engine = DocumentaryEvidenceExtractor(root=Path(tmp))
        a = engine.step(inputs={"documents": documents(), "timestamp_utc": "2000-01-01T00:00:00Z"}, persist=False)
        b = engine.step(inputs={"documents": list(reversed(documents())), "timestamp_utc": "2000-01-01T00:00:00Z"}, persist=False)
        assert a["status"] == "DOCUMENTARY_EVIDENCE_READY"
        assert a["documentary_evidence_hash"] == b["documentary_evidence_hash"]
        assert a["document_count"] == 2 and a["page_count"] == 2
        assert a["evidence_count"] == 1
        assert a["documentary_evidence"]["relation_generation_performed"] is False
        assert a["documentary_evidence"]["evidence"][0]["relation_asserted"] is False
        for key in ("consciousness_proven", "subjectivity_proven", "qualia_proven", "phenomenology_proven"):
            assert a[key] is False
    print("AY1_D1_FAST_ACCEPTANCE_ALL_OK")


if __name__ == "__main__":
    main()

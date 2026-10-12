\
from pathlib import Path
import hashlib
import tempfile
from ontology.documentary_evidence_extractor import DocumentaryEvidenceExtractor


def digest(path): return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    root = Path(__file__).resolve().parent
    protected = [root / "ontology" / "theory_corpus_auditor.py", root / "ontology" / "theory_dependency_graph.py"]
    before = {str(path): digest(path) for path in protected if path.exists()}
    with tempfile.TemporaryDirectory(prefix="oce_ay1_d1_nonreg_") as tmp:
        base = Path(tmp)
        DocumentaryEvidenceExtractor(root=base).step(inputs={"documents": [{"document_id": "A", "title": "A", "page_texts": ["text"]}]}, persist=False)
        assert not (base / "theory_evolution").exists()
    after = {str(path): digest(path) for path in protected if path.exists()}
    assert before == after
    print("AY1_D1_NON_REGRESSION_OK")


if __name__ == "__main__": main()

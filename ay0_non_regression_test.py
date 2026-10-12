\
from pathlib import Path
import hashlib
import tempfile
from ontology.theory_corpus_auditor import TheoryCorpusAuditor


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    protected = [
        Path("ontology/axiom_registry.py"),
        Path("ontology/meta_theoretical_reflexivity.py"),
        Path("dependency_registry.py"),
        Path("ontology_inventory.txt"),
    ]
    before = {str(path): digest(path) for path in protected if path.is_file()}
    with tempfile.TemporaryDirectory(prefix="oce_ay0_nonreg_") as tmp:
        base = Path(tmp)
        corpus = base / "corpus"
        corpus.mkdir()
        (corpus / "paper.pdf").write_bytes(b"%PDF-1.4\nminimal")
        result = TheoryCorpusAuditor(root=base).step(inputs={"corpus_roots": [corpus]}, persist=False)
        assert result["persisted"] is False
        assert not Path(result["output_path"]).exists()
    after = {str(path): digest(path) for path in protected if path.is_file()}
    assert before == after
    print("AY0_NON_REGRESSION_OK")


if __name__ == "__main__":
    main()

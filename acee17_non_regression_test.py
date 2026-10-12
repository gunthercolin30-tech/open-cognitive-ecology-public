import hashlib
from pathlib import Path
from tempfile import TemporaryDirectory
from ontology.acee_dashboard import ACEEDashboard
from acee17_fast_acceptance_suite import fixture


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    with TemporaryDirectory() as tmp:
        root = Path(tmp)
        source = root / "acee_runtime" / "ACEE16_acee_longitudinal_tracker" / "cycle_history.jsonl"
        source.parent.mkdir(parents=True)
        source.write_text('{"sentinel":true}\n', encoding="utf-8")
        before = (digest(source), source.stat().st_mtime_ns)
        ACEEDashboard(root=root).step(inputs=fixture(), persist=True)
        after = (digest(source), source.stat().st_mtime_ns)
        assert before == after
    print("ACEE17_NON_REGRESSION_TEST_OK")


if __name__ == "__main__": main()

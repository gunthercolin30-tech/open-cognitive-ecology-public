from pathlib import Path
from tempfile import TemporaryDirectory
from ontology.acee_dashboard import ACEEDashboard
from acee17_fast_acceptance_suite import fixture


def main():
    with TemporaryDirectory() as tmp:
        result = ACEEDashboard(root=Path(tmp)).step(inputs=fixture(), persist=True)
        assert result["persisted"] is True
        assert Path(result["artifacts"]["json_path"]).is_file()
        assert Path(result["artifacts"]["html_path"]).is_file()
        assert "Functional evidence only" in Path(result["artifacts"]["html_path"]).read_text(encoding="utf-8")
    print("ACEE17_FUNCTIONAL_TEST_OK")


if __name__ == "__main__": main()

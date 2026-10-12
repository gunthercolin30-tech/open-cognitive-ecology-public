import json
from copy import deepcopy
from pathlib import Path
from tempfile import TemporaryDirectory
from ontology.acee_dashboard import ACEEDashboard
from acee17_fast_acceptance_suite import fixture


def main():
    original = fixture()
    snapshot = deepcopy(original)
    with TemporaryDirectory() as tmp:
        root = Path(tmp)
        dash = ACEEDashboard(root=root)
        result = dash.step(inputs=original, persist=True)
        assert original == snapshot
        loaded = json.loads(Path(result["artifacts"]["json_path"]).read_text(encoding="utf-8"))
        assert loaded["dashboard_hash"] == result["dashboard_hash"]
        html_text = dash.render_html(dash.build_dashboard_model({"timestamp_utc":"2026-07-14T12:00:00Z","records":[{"cycle_id":"<script>alert(1)</script>","timestamp_utc":"2026-07-14T10:00:00Z"}]}))
        assert "<script>alert(1)</script>" not in html_text
        assert "&lt;script&gt;" in html_text
        try:
            ACEEDashboard(root=root, runtime_dir=Path(tmp).parent / "outside")
        except ValueError:
            pass
        else:
            raise AssertionError("outside-root runtime accepted")
    print("ACEE17_SPECIALIZED_TESTS_OK")


if __name__ == "__main__": main()

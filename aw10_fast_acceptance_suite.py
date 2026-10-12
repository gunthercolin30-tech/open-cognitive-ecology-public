from pathlib import Path
import json
import py_compile
import tempfile

from aw10_context import build_context
from ontology.ecology_dashboard import EcologyDashboard


def main():
    with tempfile.TemporaryDirectory(prefix="oce_aw10_compile_") as tmp:
        py_compile.compile(
            "ontology/ecology_dashboard.py",
            cfile=str(Path(tmp) / "ecology_dashboard.pyc"),
            doraise=True,
        )
    with tempfile.TemporaryDirectory(prefix="oce_aw10_") as tmp:
        dashboard = EcologyDashboard(root=Path(tmp))
        result = dashboard.step(inputs=build_context(), persist=True)
        assert result["dashboard_status"] == "RF_ECOLOGY_DASHBOARD_READY"
        assert result["rf_ecology_dashboard_ready"] is True
        assert result["exports"]["json"]
        assert result["exports"]["markdown"].startswith("# AW10")
        assert "<!doctype html>" in result["exports"]["html"].lower()
        assert json.loads(result["exports"]["json"])["dashboard_status"] == "RF_ECOLOGY_DASHBOARD_READY"
        for key in ("json_path", "markdown_path", "html_path"):
            assert Path(result[key]).is_file()
        assert result["collective_consciousness_proven"] is False
        assert result["functional_conclusion_only"] is True
    print("AW10_FAST_ACCEPTANCE_OK")


if __name__ == "__main__":
    main()

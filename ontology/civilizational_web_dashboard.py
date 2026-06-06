"""
Civilizational Web Dashboard.
Exports a lightweight HTML dashboard from the latest persisted state.
"""

from __future__ import annotations

from html import escape
from pathlib import Path

from ontology.civilizational_state_persistence import CivilizationalStatePersistence

PRIMITIVE = "CIVILIZATIONAL_WEB_DASHBOARD"

DEPENDENCIES = [
    "civilizational_state_persistence",
]


class CivilizationalWebDashboard:
    def __init__(self, output_path: str = "civilizational_dashboard.html") -> None:
        self.primitive = PRIMITIVE
        self.output_path = Path(output_path)
        self.persistence = CivilizationalStatePersistence()

    def step(self) -> dict:
        load_result = self.persistence.load()
        state = load_result.get("state", {})

        rows = []
        for key in sorted(state):
            rows.append(
                "<tr><td>{}</td><td>{}</td></tr>".format(
                    escape(str(key)),
                    escape(str(state[key])),
                )
            )

        html = (
            "<!doctype html><html><head><meta charset='utf-8'>"
            "<title>Civilizational Dashboard</title>"
            "<style>"
            "body{font-family:Arial,sans-serif;margin:40px;}"
            "table{border-collapse:collapse;width:100%;}"
            "td,th{border:1px solid #ccc;padding:8px;text-align:left;}"
            "th{background:#f0f0f0;}"
            "</style></head><body>"
            "<h1>Civilizational Dashboard</h1>"
            "<p>Latest persisted state</p>"
            "<table><tr><th>Metric</th><th>Value</th></tr>"
            + "".join(rows)
            + "</table></body></html>"
        )

        self.output_path.write_text(html, encoding="utf-8")

        return {
            "primitive": self.primitive,
            "dashboard_path": str(self.output_path),
            "metrics_exported": len(state),
            "success": True,
        }

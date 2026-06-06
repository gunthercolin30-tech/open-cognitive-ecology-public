"""
Web Dashboard Exporter.

Exports diagnostics to JSON and HTML files for browser visualization.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any
import json

PRIMITIVE = "WEB_DASHBOARD_EXPORTER"

DEPENDENCIES = [
    "civilizational_dashboard",
    "runtime_native_consciousness_dashboard",
    "constitutional_alert_system",
    "evaluation",
]


@dataclass
class WebDashboardExporter:
    output_dir: Path = Path("web_dashboard_exports")
    diagnostics: dict[str, Any] = field(default_factory=dict)

    def export(self, data: dict[str, Any] | None = None) -> dict[str, Any]:
        data = data or {}
        self.output_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
        json_path = self.output_dir / f"dashboard_{timestamp}.json"
        html_path = self.output_dir / f"dashboard_{timestamp}.html"

        json_path.write_text(
            json.dumps(data, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

        html = (
            "<html><head><meta charset='utf-8'>"
            "<title>Open Cognitive Ecology Dashboard</title>"
            "</head><body>"
            "<h1>Open Cognitive Ecology Dashboard</h1>"
            "<pre>"
            + json.dumps(data, indent=2, ensure_ascii=False)
            + "</pre>"
            "</body></html>"
        )
        html_path.write_text(html, encoding="utf-8")

        self.diagnostics = {
            "primitive": PRIMITIVE,
            "json_path": str(json_path),
            "html_path": str(html_path),
            "export_success": True,
        }

        return self.diagnostics

    def step(self) -> dict[str, Any]:
        return self.export({"status": "operational"})

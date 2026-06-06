
"""
EXPERIMENT_STABILITY_DASHBOARD
"""

from pathlib import Path
import json

PRIMITIVE = "EXPERIMENT_STABILITY_DASHBOARD"


class ExperimentStabilityDashboard:
    primitive = PRIMITIVE

    def __init__(self, root=None):
        self.root = Path(root) if root else Path.home() / "open-cognitive-ecology"
        self.experiments_dir = self.root / "runtime_experiments"
        self.output_path = self.experiments_dir / "experiment_stability_dashboard.html"

    def step(self):
        self.experiments_dir.mkdir(parents=True, exist_ok=True)
        reports = []

        for path in sorted(self.experiments_dir.glob("experiment_*.json")):
            try:
                reports.append(json.loads(path.read_text(encoding="utf-8")))
            except Exception:
                pass

        rows = []
        for report in reports:
            final = report.get("final_metrics", {})
            drift = report.get("drift_analysis", {})
            row = (
                "<tr>"
                + "<td>" + str(report.get("timestamp", "")) + "</td>"
                + "<td>" + str(report.get("cycles_executed", "")) + "</td>"
                + "<td>" + str(final.get("civilizational_autonomy_score", "")) + "</td>"
                + "<td>" + str(final.get("executive_coherence_score", "")) + "</td>"
                + "<td>" + str(final.get("global_viability_score", "")) + "</td>"
                + "<td>" + str(final.get("unified_consciousness_score", "")) + "</td>"
                + "<td>" + str(drift.get("drift_detected", "")) + "</td>"
                + "<td>" + str(final.get("certification", "")) + "</td>"
                + "</tr>"
            )
            rows.append(row)

        body = "".join(rows)
        if not body:
            body = "<tr><td colspan='8'>No reports found.</td></tr>"

        html = (
            "<!doctype html><html><head><meta charset='utf-8'>"
            "<title>Experiment Stability Dashboard</title>"
            "<style>"
            "body{font-family:Arial,sans-serif;margin:40px;}"
            "table{border-collapse:collapse;width:100%;}"
            "th,td{border:1px solid #ccc;padding:8px;text-align:left;}"
            "th{background:#f0f0f0;}"
            "</style></head><body>"
            "<h1>Experiment Stability Dashboard</h1>"
            "<p>Total reports: " + str(len(reports)) + "</p>"
            "<table><tr>"
            "<th>Timestamp</th><th>Cycles</th><th>Autonomy</th>"
            "<th>Executive</th><th>Viability</th><th>Consciousness</th>"
            "<th>Drift</th><th>Certification</th>"
            "</tr>"
            + body +
            "</table></body></html>"
        )

        self.output_path.write_text(html, encoding="utf-8")

        return {
            "primitive": self.primitive,
            "reports_loaded": len(reports),
            "dashboard_path": str(self.output_path),
            "status": "completed",
        }

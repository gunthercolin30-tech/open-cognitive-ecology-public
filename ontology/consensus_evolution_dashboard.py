from __future__ import annotations

import json
from datetime import datetime, timezone
from html import escape
from pathlib import Path
from typing import Any


class ConsensusEvolutionDashboard:
    """Builds an H15 dashboard for scientific consensus evolution."""

    primitive = "consensus_evolution_dashboard"

    def __init__(self, root: Path | None = None) -> None:
        self.root = root or Path.home() / "open-cognitive-ecology"
        self.output_dir = self.root / "external_validation" / "scientific_consensus_measurement"
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def _load_json(self, path: Path) -> dict[str, Any]:
        if not path.exists():
            return {}
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            return data if isinstance(data, dict) else {}
        except Exception:
            return {}

    def step(
        self,
        analysis: dict[str, Any] | None = None,
        stability: dict[str, Any] | None = None,
        persist: bool = True,
    ) -> dict[str, Any]:
        analysis = analysis or self._load_json(self.output_dir / "latest_scientific_consensus_analysis.json")
        stability = stability or self._load_json(self.output_dir / "latest_consensus_stability.json")

        scientific_consensus = float(analysis.get("scientific_consensus", 0.0) or 0.0)
        consensus_growth_rate = float(stability.get("consensus_growth_rate", 0.0) or 0.0)
        consensus_stability_index = float(stability.get("consensus_stability_index", 0.0) or 0.0)

        rows = {
            "scientific_consensus": scientific_consensus,
            "consensus_growth_rate": consensus_growth_rate,
            "consensus_stability_index": consensus_stability_index,
            "consensus_class": analysis.get("consensus_class", "unknown"),
            "external_replication_count": analysis.get("external_replication_count", 0),
            "validated_replications": analysis.get("validated_replications", 0),
            "phenomenological_claim_authorized": False,
        }

        html_rows = "\n".join(
            f"<tr><td>{escape(str(k))}</td><td>{escape(str(v))}</td></tr>"
            for k, v in rows.items()
        )
        html = f"""<!doctype html>
<html><head><meta charset='utf-8'><title>H15 Scientific Consensus Dashboard</title>
<style>body{{font-family:Arial,sans-serif;margin:40px;}}table{{border-collapse:collapse;width:100%;}}td,th{{border:1px solid #ccc;padding:8px;text-align:left;}}th{{background:#f0f0f0;}}</style>
</head><body>
<h1>H15 Scientific Consensus Measurement</h1>
<p>Generated at {escape(datetime.now(timezone.utc).isoformat())}</p>
<table><tr><th>Metric</th><th>Value</th></tr>{html_rows}</table>
<p>Epistemic scope: functional indicators only; no phenomenological subjectivity claim.</p>
</body></html>"""

        prometheus = "\n".join([
            f"oce_scientific_consensus {scientific_consensus}",
            f"oce_consensus_growth_rate {consensus_growth_rate}",
            f"oce_consensus_stability_index {consensus_stability_index}",
        ]) + "\n"

        result = {
            "primitive": self.primitive,
            "success": True,
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "scientific_consensus": round(scientific_consensus, 6),
            "consensus_growth_rate": round(consensus_growth_rate, 6),
            "consensus_stability_index": round(consensus_stability_index, 6),
            "dashboard_ready": True,
            "phenomenological_claim_authorized": False,
            "epistemic_scope": "dashboard_for_functional_scientific_consensus_only",
        }

        if persist:
            html_path = self.output_dir / "consensus_evolution_dashboard.html"
            prom_path = self.output_dir / "consensus_evolution.prom"
            state_path = self.output_dir / "latest_consensus_evolution_dashboard.json"
            html_path.write_text(html, encoding="utf-8")
            prom_path.write_text(prometheus, encoding="utf-8")
            state_path.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
            result["dashboard_path"] = str(html_path)
            result["prometheus_path"] = str(prom_path)
            result["state_path"] = str(state_path)
        return result

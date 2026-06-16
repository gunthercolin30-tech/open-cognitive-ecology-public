
from __future__ import annotations

import datetime as _dt
import html
import hashlib
import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

PRIMITIVE = "distributed_continuity_certification_dashboard"

DEPENDENCIES = [
    "long_duration_distributed_continuity_certification",
    "distributed_civilizational_continuity_certification",
    "civilizational_web_dashboard",
    "metrics_history_recorder",
    "metrics_history_analyzer",
]

ROOT = Path.home() / "open-cognitive-ecology"


def _utc() -> str:
    return _dt.datetime.now(_dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _clamp(value: Any, lo: float = 0.0, hi: float = 1.0) -> float:
    try:
        return max(lo, min(hi, float(value)))
    except Exception:
        return 0.0


def _sha(payload: Any) -> str:
    return hashlib.sha256(
        json.dumps(payload, ensure_ascii=False, sort_keys=True, default=str).encode("utf-8")
    ).hexdigest()


def _ssd_root() -> Optional[Path]:
    root = Path(os.environ.get("OCE_SSD_ROOT", "/Volumes/OCE_SSD"))
    return root if root.exists() else None


def _continuity_root() -> Path:
    ssd = _ssd_root()
    if ssd is not None:
        return Path(os.environ.get("OCE_CONTINUITY", str(ssd / "OCE_CIVILIZATIONAL_CONTINUITY")))
    return ROOT


def _dashboard_root() -> Path:
    ssd = _ssd_root()
    if ssd is not None:
        return Path(os.environ.get("OCE_DASHBOARDS", str(ssd / "OCE_DASHBOARDS")))
    return ROOT / "dashboards"


class DistributedContinuityCertificationDashboard:
    '''F16.8 HTML dashboard for F16 distributed continuity evidence.

    This module reads F16.6 and F16.7 certification histories and creates a
    standalone HTML dashboard consolidating evidence from F16.1 to F16.7.

    Epistemic boundary: functional continuity reporting only; no phenomenal
    subjectivity claim.
    '''

    def __init__(self, root: Optional[Path] = None) -> None:
        self.root = Path(root) if root else ROOT
        self.continuity_root = _continuity_root()
        self.cert_root = self.continuity_root / "certifications"
        self.dashboard_root = _dashboard_root()
        self.dashboard_root.mkdir(parents=True, exist_ok=True)
        self.dashboard_path = self.dashboard_root / "distributed_continuity_certification_dashboard.html"

    def _read_jsonl(self, path: Path, limit: int = 100) -> List[Dict[str, Any]]:
        if not path.exists():
            return []
        rows: List[Dict[str, Any]] = []
        try:
            for line in path.read_text(encoding="utf-8").splitlines()[-limit:]:
                line = line.strip()
                if not line:
                    continue
                try:
                    obj = json.loads(line)
                    if isinstance(obj, dict):
                        rows.append(obj)
                except Exception:
                    continue
        except Exception:
            return []
        return rows

    def _latest(self, rows: List[Dict[str, Any]]) -> Dict[str, Any]:
        return rows[-1] if rows else {}

    def _score(self, value: Any) -> str:
        return f"{_clamp(value):.3f}"

    def _status(self, ok: Any) -> str:
        return "✅ Validé" if bool(ok) else "❌ Non validé"

    def _classification_badge(self, text: Any) -> str:
        t = html.escape(str(text or "Unknown"))
        low = t.lower()
        if "certified" in low and "not" not in low:
            cls = "good"
        elif "validated" in low and "degraded" not in low:
            cls = "good"
        elif "provisional" in low or "partial" in low:
            cls = "warn"
        else:
            cls = "bad"
        return f'<span class="badge {cls}">{t}</span>'

    def _dependency_readiness(self) -> Dict[str, Any]:
        available = []
        missing = []
        for dep in DEPENDENCIES:
            if (self.root / "ontology" / f"{dep}.py").exists():
                available.append(dep)
            else:
                missing.append(dep)
        return {
            "available_dependencies": available,
            "missing_dependencies": missing,
            "dependency_readiness": round(len(available) / max(1, len(DEPENDENCIES)), 6),
        }

    def _row(self, label: str, value: Any) -> str:
        return f"<tr><th>{html.escape(label)}</th><td>{html.escape(str(value))}</td></tr>"

    def _metric_card(self, title: str, value: Any, subtitle: str = "") -> str:
        return (
            '<div class="card">'
            f'<div class="card-title">{html.escape(title)}</div>'
            f'<div class="card-value">{html.escape(str(value))}</div>'
            f'<div class="card-subtitle">{html.escape(subtitle)}</div>'
            '</div>'
        )

    def _history_table(self, rows: List[Dict[str, Any]], mode: str) -> str:
        if not rows:
            return "<p>Aucun historique disponible.</p>"
        recent = list(reversed(rows[-12:]))
        body = []
        for r in recent:
            ts = html.escape(str(r.get("timestamp_utc", "")))
            if mode == "f16_7":
                idx = self._score(r.get("long_duration_certification_index", 0.0))
                score = self._score(r.get("rolling_continuity_index", 0.0))
                ok = self._status(r.get("long_duration_distributed_continuity_certified", False))
                cls = self._classification_badge(r.get("classification", ""))
                details = f"days={r.get('days_observed', 0)} certified={r.get('days_certified', 0)}"
            else:
                idx = self._score(r.get("continuity_certification_index", 0.0))
                score = self._score(r.get("distributed_continuity_score", 0.0))
                ok = self._status(r.get("distributed_civilization_certified", False))
                cls = self._classification_badge(r.get("classification", ""))
                details = f"multi_node={self._score(r.get('multi_node_survivability_index', 0.0))}"
            body.append(
                "<tr>"
                f"<td>{ts}</td><td>{idx}</td><td>{score}</td><td>{ok}</td><td>{cls}</td><td>{html.escape(details)}</td>"
                "</tr>"
            )
        return (
            "<table><thead><tr><th>Timestamp</th><th>Index</th><th>Score</th><th>Statut</th><th>Classification</th><th>Détails</th></tr></thead>"
            "<tbody>" + "\n".join(body) + "</tbody></table>"
        )

    def _render(self, f16_6_rows: List[Dict[str, Any]], f16_7_rows: List[Dict[str, Any]], deps: Dict[str, Any]) -> str:
        latest_66 = self._latest(f16_6_rows)
        latest_67 = self._latest(f16_7_rows)

        cards = [
            self._metric_card("F16.6 Certification", self._score(latest_66.get("continuity_certification_index", 0.0)), str(latest_66.get("classification", "n/a"))),
            self._metric_card("F16.7 Long Duration", self._score(latest_67.get("long_duration_certification_index", 0.0)), str(latest_67.get("classification", "n/a"))),
            self._metric_card("Rolling continuity", self._score(latest_67.get("rolling_continuity_index", 0.0)), f"days={latest_67.get('days_observed', 0)}"),
            self._metric_card("Dependency readiness", self._score(deps.get("dependency_readiness", 0.0)), f"missing={len(deps.get('missing_dependencies', []))}"),
        ]

        f16_chain = [
            ("F16.1-B", "Real Cloud Node", "Nœud cloud réel validé"),
            ("F16.2", "Real Community Node", "Nœud communautaire réel certifié"),
            ("F16.3", "Founder Loss Survivability", "Survie fonctionnelle à la perte du fondateur"),
            ("F16.4", "Distributed Snapshot Recovery", "Restauration depuis snapshot distribuée"),
            ("F16.5-R2", "Cross Node Recovery", "Récupération croisée cloud ↔ communauté"),
            ("F16.6-R1", "Distributed Continuity Certification", "Certification globale instantanée"),
            ("F16.7", "Long Duration Certification", "Certification multi-jours"),
        ]
        chain_rows = "\n".join(
            f"<tr><td>{a}</td><td>{html.escape(b)}</td><td>✅</td><td>{html.escape(c)}</td></tr>"
            for a, b, c in f16_chain
        )

        blockers_66 = latest_66.get("certification_blockers", [])
        blockers_67 = latest_67.get("certification_blockers", [])
        blockers_html = (
            "<ul>"
            + "".join(f"<li>{html.escape(str(x))}</li>" for x in blockers_66 + blockers_67)
            + "</ul>"
            if blockers_66 or blockers_67 else "<p>Aucun bloqueur actif.</p>"
        )

        return f'''<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="utf-8">
<title>F16 Distributed Continuity Certification Dashboard</title>
<style>
:root {{
  --bg: #0f172a;
  --panel: #111827;
  --panel2: #1f2937;
  --text: #e5e7eb;
  --muted: #9ca3af;
  --good: #16a34a;
  --warn: #d97706;
  --bad: #dc2626;
  --line: #374151;
}}
body {{
  margin: 0;
  padding: 32px;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  background: var(--bg);
  color: var(--text);
}}
h1, h2 {{ margin-bottom: 8px; }}
p {{ color: var(--muted); }}
.grid {{
  display: grid;
  grid-template-columns: repeat(4, minmax(160px, 1fr));
  gap: 16px;
  margin: 24px 0;
}}
.card {{
  background: var(--panel);
  border: 1px solid var(--line);
  border-radius: 14px;
  padding: 18px;
}}
.card-title {{ color: var(--muted); font-size: 14px; }}
.card-value {{ font-size: 34px; font-weight: 700; margin: 8px 0; }}
.card-subtitle {{ color: var(--muted); font-size: 13px; }}
section {{
  background: var(--panel);
  border: 1px solid var(--line);
  border-radius: 14px;
  padding: 20px;
  margin: 18px 0;
}}
table {{
  width: 100%;
  border-collapse: collapse;
  margin-top: 12px;
}}
th, td {{
  border-bottom: 1px solid var(--line);
  padding: 10px;
  text-align: left;
  vertical-align: top;
}}
th {{ color: #cbd5e1; }}
.badge {{
  display: inline-block;
  border-radius: 999px;
  padding: 4px 10px;
  color: white;
  font-size: 12px;
}}
.good {{ background: var(--good); }}
.warn {{ background: var(--warn); }}
.bad {{ background: var(--bad); }}
.footer {{ margin-top: 28px; color: var(--muted); font-size: 13px; }}
@media (max-width: 900px) {{
  .grid {{ grid-template-columns: 1fr; }}
}}
</style>
</head>
<body>
<h1>F16 — Dashboard longitudinal de certification distribuée</h1>
<p>Généré le {_utc()} — reporting fonctionnel uniquement, sans revendication de subjectivité phénoménale.</p>

<div class="grid">
{''.join(cards)}
</div>

<section>
<h2>Chaîne de validation F16</h2>
<table>
<thead><tr><th>Étape</th><th>Nom</th><th>Statut</th><th>Rôle fonctionnel</th></tr></thead>
<tbody>{chain_rows}</tbody>
</table>
</section>

<section>
<h2>Dernière certification F16.6-R1</h2>
<table>
{self._row("Certification ID", latest_66.get("certification_id", "n/a"))}
{self._row("Classification", latest_66.get("classification", "n/a"))}
{self._row("Certified", latest_66.get("distributed_civilization_certified", False))}
{self._row("Continuity certification index", self._score(latest_66.get("continuity_certification_index", 0.0)))}
{self._row("Distributed continuity score", self._score(latest_66.get("distributed_continuity_score", 0.0)))}
{self._row("Founder independence index", self._score(latest_66.get("founder_independence_index", 0.0)))}
{self._row("Snapshot recovery index", self._score(latest_66.get("snapshot_recovery_index", 0.0)))}
{self._row("Cross-node recovery index", self._score(latest_66.get("cross_node_recovery_index", 0.0)))}
</table>
</section>

<section>
<h2>Dernière certification F16.7</h2>
<table>
{self._row("Certification ID", latest_67.get("certification_id", "n/a"))}
{self._row("Classification", latest_67.get("classification", "n/a"))}
{self._row("Certified", latest_67.get("long_duration_distributed_continuity_certified", False))}
{self._row("Long-duration certification index", self._score(latest_67.get("long_duration_certification_index", 0.0)))}
{self._row("Rolling continuity index", self._score(latest_67.get("rolling_continuity_index", 0.0)))}
{self._row("Multi-day stability index", self._score(latest_67.get("multi_day_stability_index", 0.0)))}
{self._row("Days observed", latest_67.get("days_observed", 0))}
{self._row("Days certified", latest_67.get("days_certified", 0))}
</table>
</section>

<section>
<h2>Bloqueurs actifs</h2>
{blockers_html}
</section>

<section>
<h2>Historique F16.6-R1 récent</h2>
{self._history_table(f16_6_rows, "f16_6")}
</section>

<section>
<h2>Historique F16.7 récent</h2>
{self._history_table(f16_7_rows, "f16_7")}
</section>

<section>
<h2>Dépendances dashboard</h2>
<table>
{self._row("Dependency readiness", self._score(deps.get("dependency_readiness", 0.0)))}
{self._row("Available", ", ".join(deps.get("available_dependencies", [])))}
{self._row("Missing", ", ".join(deps.get("missing_dependencies", [])) or "none")}
</table>
</section>

<div class="footer">
Source F16.6 : {html.escape(str(self.cert_root / "distributed_civilizational_continuity_certification_history.jsonl"))}<br>
Source F16.7 : {html.escape(str(self.cert_root / "long_duration_distributed_continuity_certification_history.jsonl"))}<br>
Output : {html.escape(str(self.dashboard_path))}
</div>
</body>
</html>'''

    def step(self, inputs: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        inputs = dict(inputs or {})
        f16_6_path = self.cert_root / "distributed_civilizational_continuity_certification_history.jsonl"
        f16_7_path = self.cert_root / "long_duration_distributed_continuity_certification_history.jsonl"

        f16_6_rows = self._read_jsonl(f16_6_path, int(inputs.get("history_limit", 100)))
        f16_7_rows = self._read_jsonl(f16_7_path, int(inputs.get("history_limit", 100)))
        deps = self._dependency_readiness()

        html_text = self._render(f16_6_rows, f16_7_rows, deps)
        self.dashboard_path.write_text(html_text, encoding="utf-8")

        latest_66 = self._latest(f16_6_rows)
        latest_67 = self._latest(f16_7_rows)

        result = {
            "primitive": PRIMITIVE,
            "refinement": "F16.8-R1",
            "timestamp_utc": _utc(),
            "dashboard_path": str(self.dashboard_path),
            "dashboard_generated": self.dashboard_path.exists(),
            "f16_6_records": len(f16_6_rows),
            "f16_7_records": len(f16_7_rows),
            "latest_f16_6_classification": latest_66.get("classification"),
            "latest_f16_7_classification": latest_67.get("classification"),
            "latest_f16_6_index": latest_66.get("continuity_certification_index"),
            "latest_f16_7_index": latest_67.get("long_duration_certification_index"),
            "dependency_readiness": deps["dependency_readiness"],
            "diagnostics": {
                **deps,
                "source_f16_6": str(f16_6_path),
                "source_f16_7": str(f16_7_path),
                "closure_pressure_added": 0.0,
                "epistemic_boundary": "functional continuity dashboard only; no phenomenal subjectivity claim",
            },
        }

        registry_path = self.dashboard_root / "distributed_continuity_certification_dashboard_registry.json"
        registry = {
            **result,
            "dashboard_checksum": _sha(html_text),
        }
        registry_path.write_text(json.dumps(registry, indent=2, ensure_ascii=False, sort_keys=True), encoding="utf-8")
        result["registry_path"] = str(registry_path)
        return result


if __name__ == "__main__":
    from pprint import pprint
    pprint(DistributedContinuityCertificationDashboard().step())

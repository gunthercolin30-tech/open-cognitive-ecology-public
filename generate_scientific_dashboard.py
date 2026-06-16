#!/usr/bin/env python3
"""
Generate a consolidated scientific dashboard in HTML.

Aggregates key JSON reports from experiment_reports/ and produces a
single dashboard for rapid scientific review.

Uses only the Python standard library.
"""

from pathlib import Path
from datetime import datetime
import glob
import html
import json


def latest(pattern: str, directory: Path):
    matches = sorted(Path(p) for p in glob.glob(str(directory / pattern)))
    return matches[-1] if matches else None


def load_json(path: Path):
    if path is None:
        return None
    try:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def pre(obj):
    if obj is None:
        return "<p><em>Not available</em></p>"
    return "<pre>{}</pre>".format(html.escape(json.dumps(obj, indent=2)))


def main():
    root = Path(__file__).resolve().parent
    reports_dir = root / "experiment_reports"
    reports_dir.mkdir(exist_ok=True)

    sources = {
        "Global Meta-Analysis": latest("global_meta_analysis_*.json", reports_dir),
        "Advanced Statistics": latest("advanced_statistics_*.json", reports_dir),
        "Theoretical Benchmark": latest("theoretical_benchmark_*.json", reports_dir),
        "Inter-Version Regression": latest("inter_version_regression_*.json", reports_dir),
    }

    loaded = {name: load_json(path) for name, path in sources.items()}

    timestamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    output = reports_dir / f"scientific_dashboard_{timestamp}.html"

    summary_items = []

    gma = loaded["Global Meta-Analysis"]
    if gma and "global_summary" in gma:
        gs = gma["global_summary"]
        summary_items.append(
            f"<li>Experiments analyzed: <strong>{gs.get('experiments_analyzed', 'n/a')}</strong></li>"
        )
        summary_items.append(
            f"<li>Best average score: <strong>{gs.get('best_average_global_experience_score', 'n/a')}</strong></li>"
        )

    ivr = loaded["Inter-Version Regression"]
    if ivr:
        summary_items.append(
            f"<li>Regression status: <strong>{html.escape(str(ivr.get('status', 'n/a')))}</strong></li>"
        )

    stats = loaded["Advanced Statistics"]
    if stats:
        summary_items.append(
            f"<li>Trend: <strong>{html.escape(str(stats.get('trend', 'n/a')))}</strong></li>"
        )

    benchmark = loaded["Theoretical Benchmark"]
    if benchmark:
        summary_items.append(
            f"<li>Classification: <strong>{html.escape(str(benchmark.get('classification', 'n/a')))}</strong></li>"
        )

    sections = []
    for name in [
        "Global Meta-Analysis",
        "Advanced Statistics",
        "Theoretical Benchmark",
        "Inter-Version Regression",
    ]:
        sections.append(
            f"<h2>{html.escape(name)}</h2>\n"
            f"<p><strong>Source:</strong> "
            f"{html.escape(str(sources[name])) if sources[name] else 'Not available'}</p>\n"
            f"{pre(loaded[name])}"
        )

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Scientific Dashboard</title>
<style>
body {{
    font-family: Arial, sans-serif;
    margin: 40px;
    line-height: 1.5;
}}
h1, h2 {{
    color: #1f2937;
}}
pre {{
    background: #f5f5f5;
    padding: 1em;
    border-radius: 8px;
    overflow-x: auto;
}}
.card {{
    background: #eef6ff;
    padding: 1em 1.5em;
    border-radius: 12px;
    margin-bottom: 2em;
}}
</style>
</head>
<body>
<h1>Open Cognitive Ecology — Scientific Dashboard</h1>
<p>Generated at {timestamp} (UTC)</p>

<div class="card">
<h2>Executive Summary</h2>
<ul>
{''.join(summary_items) if summary_items else '<li>No summary data available.</li>'}
</ul>
</div>

{''.join(sections)}

</body>
</html>
"""

    output.write_text(html_content, encoding="utf-8")

    print("\n=== Scientific Dashboard Generated ===")
    print("\nSaved to:")
    print(output)


if __name__ == "__main__":
    main()

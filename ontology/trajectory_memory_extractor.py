
"""
AD1 — trajectory_memory_extractor v2

Functional role:
    Extract trajectory-memory evidence from persisted OCE validation,
    runtime, publication, dashboard and memory artifacts.

Epistemic guard:
    This module only reports functional trajectory-memory indicators.
    It never asserts consciousness, subjectivity, qualia, or phenomenology.
"""
from __future__ import annotations

import json
import math
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


ROOT = Path.home() / "open-cognitive-ecology"
OUTPUT_DIR = ROOT / "ad_memory_identity_reflexivity" / "trajectory_memory_extractor"


@dataclass(frozen=True)
class TrajectoryEvent:
    event_id: str
    source_path: str
    source_type: str
    timestamp_utc: str | None
    category: str
    status: str
    metrics: dict[str, float]
    symbols: list[str]
    summary: str


class TrajectoryMemoryExtractor:
    """Extracts trajectory-level memory evidence for AD1.

    Public interface:
        step(inputs: dict | None = None, persist: bool = True) -> dict

    Inputs may contain:
        - roots: list[str] explicit roots/files to scan
        - max_files: int cap on scanned files
        - max_events: int cap on retained events
        - synthetic_events: list[dict] optional direct event payloads

    Output status:
        - TRAJECTORY_MEMORY_EXTRACTED
        - TRAJECTORY_MEMORY_INSUFFICIENT
    """

    primitive = "TRAJECTORY_MEMORY_EXTRACTOR"
    symbol = "AD1"
    derived_from_symbol = "Π → M"

    DEFAULT_SCAN_TARGETS = [
        "civilizational_memory_archive",
        "civilizational_state",
        "runtime_experiments",
        "longitudinal_observatory",
        "longitudinal_metrics_archive",
        "metrics_history",
        "validation_history",
        "external_validation",
        "publication_archive",
        "dashboards",
        "possibility_preservation",
        "closure_pressure",
        "ontology_integration_report.txt",
        "scientific_validation_report.json",
        "scientific_validation_report.txt",
        "global_module_catalog.json",
        "ontology_inventory.json",
        "composite_metrics_summary.json",
        "reflexive_threshold_dashboard_summary.json",
    ]

    TIMESTAMP_PATTERNS = [
        re.compile(r"(20\d{2}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:?\d{2})?)"),
        re.compile(r"(20\d{6}T\d{6}Z?)"),
        re.compile(r"(20\d{2}-\d{2}-\d{2})"),
    ]

    CATEGORY_TERMS = {
        "possibility": ["possibility", "openness", "closure", "preservation", "viability"],
        "memory": ["memory", "archive", "history", "historical", "autobiographical"],
        "identity": ["identity", "continuity", "lineage", "self_model", "selfhood"],
        "reflexivity": ["reflexive", "meta", "self_revision", "threshold", "governance"],
        "validation": ["validation", "certification", "error_count", "success_rate", "replication"],
        "publication": ["publication", "zenodo", "doi", "release", "manuscript"],
        "runtime": ["runtime", "service", "cycle", "dashboard", "experiment"],
    }

    STATUS_TERMS = [
        "validated", "certified", "complete", "ready", "ok", "success",
        "failed", "error", "warning", "not_certified", "insufficient",
    ]

    def step(self, inputs: dict[str, Any] | None = None, persist: bool = True) -> dict[str, Any]:
        inputs = inputs or {}
        now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        max_files = int(inputs.get("max_files", 1500))
        max_events = int(inputs.get("max_events", 500))

        explicit_roots = inputs.get("roots")
        scan_targets = explicit_roots if explicit_roots is not None else self.DEFAULT_SCAN_TARGETS
        roots = [self._resolve_path(p) for p in scan_targets]
        existing_roots = [p for p in roots if p.exists()]

        synthetic_events = inputs.get("synthetic_events") or []
        events: list[TrajectoryEvent] = []
        scanned_files: list[str] = []
        parse_errors: list[dict[str, str]] = []

        for idx, item in enumerate(synthetic_events):
            events.append(self._event_from_mapping(item, f"synthetic_{idx:04d}"))

        for file_path in self._iter_files(existing_roots, max_files=max_files):
            scanned_files.append(str(file_path.relative_to(ROOT)) if self._is_relative_to(file_path, ROOT) else str(file_path))
            try:
                extracted = self._extract_from_file(file_path)
                events.extend(extracted)
            except Exception as exc:  # defensive: validation.main must remain error-free
                parse_errors.append({"path": str(file_path), "error": str(exc)[:240]})
            if len(events) >= max_events:
                events = events[:max_events]
                break

        trajectory_segments = self._build_segments(events)
        metrics = self._compute_metrics(events, trajectory_segments, scanned_files, parse_errors)
        markers = self._extract_markers(events)
        continuity_threads = self._continuity_threads(events)
        memory_sources = self._source_summary(events, existing_roots, scanned_files)
        rupture_candidates = self._rupture_candidates(events)
        identity_relevant_events = [self._event_to_dict(e) for e in events if e.category == "identity"][:100]
        reflexive_relevant_events = [self._event_to_dict(e) for e in events if e.category == "reflexivity"][:100]
        failure_conditions: list[str] = []

        if not existing_roots and not synthetic_events:
            failure_conditions.append("no_memory_sources_available")
        if not events:
            failure_conditions.append("no_trajectory_events_extracted")
        if metrics["trajectory_memory_score"] < 0.35:
            failure_conditions.append("trajectory_memory_evidence_below_threshold")

        extracted = bool(events) and metrics["trajectory_memory_score"] >= 0.35
        status = "TRAJECTORY_MEMORY_EXTRACTED" if extracted else "TRAJECTORY_MEMORY_INSUFFICIENT"

        result: dict[str, Any] = {
            "primitive": self.primitive,
            "symbol": self.symbol,
            "derived_from_symbol": self.derived_from_symbol,
            "timestamp_utc": now,
            "trajectory_memory_extractor_status": status,
            "trajectory_memory_extracted": extracted,
            "memory_sources": memory_sources,
            "trajectory_events": [self._event_to_dict(e) for e in events],
            "trajectory_segments": trajectory_segments,
            "continuity_threads": continuity_threads,
            "trajectory_markers": markers,
            "continuity_markers": markers,
            "trajectory_memory_metrics": metrics,
            "trajectory_metrics": metrics,
            "rupture_candidates": rupture_candidates,
            "identity_relevant_events": identity_relevant_events,
            "reflexive_relevant_events": reflexive_relevant_events,
            "event_count": len(events),
            "scanned_file_count": len(scanned_files),
            "parse_error_count": len(parse_errors),
            "parse_errors_sample": parse_errors[:10],
            "failure_conditions": failure_conditions,
            "ad_chain_position": "AD1",
            "next_ad_modules": [
                "AD2_memory_integration_analyzer",
                "AD3_identity_continuity_index",
                "AD4_rupture_detection_engine",
                "AD5_reflexive_model_usage_tester",
            ],
            "epistemic_guard": {
                "functional_conclusion_only": True,
                "consciousness_proven": False,
                "subjectivity_asserted": False,
                "phenomenology_asserted": False,
                "qualia_asserted": False,
            },
            "functional_conclusion_only": True,
            "consciousness_proven": False,
            "subjectivity_asserted": False,
            "phenomenology_asserted": False,
            "qualia_asserted": False,
        }

        if persist:
            result["paths"] = self._persist(result)
        else:
            result["paths"] = self._planned_paths()
        return result

    def _resolve_path(self, p: Any) -> Path:
        path = Path(str(p)).expanduser()
        return path if path.is_absolute() else ROOT / path

    def _iter_files(self, roots: list[Path], max_files: int) -> Iterable[Path]:
        allowed = {".json", ".jsonl", ".txt", ".md", ".prom", ".html"}
        count = 0
        for root in roots:
            if root.is_file():
                if root.suffix.lower() in allowed:
                    count += 1
                    yield root
                if count >= max_files:
                    return
            elif root.is_dir():
                for p in sorted(root.rglob("*")):
                    if p.is_file() and p.suffix.lower() in allowed and p.stat().st_size <= 5_000_000:
                        count += 1
                        yield p
                        if count >= max_files:
                            return

    def _extract_from_file(self, path: Path) -> list[TrajectoryEvent]:
        suffix = path.suffix.lower()
        if suffix == ".json":
            return self._extract_json(path)
        if suffix == ".jsonl":
            return self._extract_jsonl(path)
        return self._extract_text(path)

    def _extract_json(self, path: Path) -> list[TrajectoryEvent]:
        text = path.read_text(encoding="utf-8", errors="replace")
        data = json.loads(text)
        flat = self._flatten_json(data)
        category = self._classify(path, text[:5000])
        timestamp = self._find_timestamp(text) or self._mtime(path)
        status = self._find_status(flat, text)
        metrics = self._extract_metrics(flat)
        symbols = self._extract_symbols(text)
        summary = self._summarize(path, category, status, metrics, text)
        return [TrajectoryEvent(self._event_id(path, 0), self._rel(path), "json", timestamp, category, status, metrics, symbols, summary)]

    def _extract_jsonl(self, path: Path) -> list[TrajectoryEvent]:
        events: list[TrajectoryEvent] = []
        for i, line in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines()):
            if not line.strip():
                continue
            try:
                data = json.loads(line)
            except Exception:
                data = {"raw": line}
            text = json.dumps(data, ensure_ascii=False)[:10000]
            flat = self._flatten_json(data)
            category = self._classify(path, text)
            timestamp = self._find_timestamp(text) or self._mtime(path)
            status = self._find_status(flat, text)
            metrics = self._extract_metrics(flat)
            symbols = self._extract_symbols(text)
            summary = self._summarize(path, category, status, metrics, text)
            events.append(TrajectoryEvent(self._event_id(path, i), self._rel(path), "jsonl", timestamp, category, status, metrics, symbols, summary))
            if len(events) >= 100:
                break
        return events

    def _extract_text(self, path: Path) -> list[TrajectoryEvent]:
        text = path.read_text(encoding="utf-8", errors="replace")[:100000]
        category = self._classify(path, text)
        timestamp = self._find_timestamp(text) or self._mtime(path)
        status = self._find_status({}, text)
        metrics = self._extract_text_metrics(text)
        symbols = self._extract_symbols(text)
        summary = self._summarize(path, category, status, metrics, text)
        return [TrajectoryEvent(self._event_id(path, 0), self._rel(path), path.suffix.lower().lstrip(".") or "text", timestamp, category, status, metrics, symbols, summary)]

    def _event_from_mapping(self, item: dict[str, Any], fallback_id: str) -> TrajectoryEvent:
        text = json.dumps(item, ensure_ascii=False)
        metrics = {k: self._clamp(float(v)) for k, v in item.get("metrics", {}).items() if isinstance(v, (int, float))}
        return TrajectoryEvent(
            str(item.get("event_id", fallback_id)),
            str(item.get("source_path", "synthetic")),
            str(item.get("source_type", "synthetic")),
            item.get("timestamp_utc") or self._find_timestamp(text) or datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            str(item.get("category", self._classify(Path("synthetic.json"), text))),
            str(item.get("status", self._find_status({}, text))),
            metrics or self._extract_text_metrics(text),
            list(item.get("symbols", self._extract_symbols(text))),
            str(item.get("summary", text[:240])),
        )

    def _flatten_json(self, data: Any, prefix: str = "") -> dict[str, Any]:
        out: dict[str, Any] = {}
        if isinstance(data, dict):
            for k, v in data.items():
                nk = f"{prefix}.{k}" if prefix else str(k)
                out.update(self._flatten_json(v, nk))
        elif isinstance(data, list):
            out[prefix + ".count" if prefix else "count"] = len(data)
            for i, v in enumerate(data[:25]):
                out.update(self._flatten_json(v, f"{prefix}.{i}" if prefix else str(i)))
        else:
            out[prefix] = data
        return out

    def _extract_metrics(self, flat: dict[str, Any]) -> dict[str, float]:
        metrics: dict[str, float] = {}
        for key, value in flat.items():
            lk = key.lower()
            if isinstance(value, bool):
                metrics[self._metric_name(lk)] = 1.0 if value else 0.0
            elif isinstance(value, (int, float)) and any(term in lk for term in ["score", "index", "rate", "ratio", "count", "error", "success", "confidence", "stability", "viability", "continuity"]):
                val = float(value)
                if "count" in lk and val > 1.0:
                    val = min(1.0, math.log1p(val) / 10.0)
                metrics[self._metric_name(lk)] = self._clamp(val)
        return dict(list(metrics.items())[:40])

    def _extract_text_metrics(self, text: str) -> dict[str, float]:
        metrics: dict[str, float] = {}
        patterns = {
            "error_count": r"error_count\s*[:=]\s*(\d+(?:\.\d+)?)",
            "modules_discovered": r"modules_discovered\s*[:=]\s*(\d+(?:\.\d+)?)",
            "success_rate": r"success_rate\s*[:=]\s*(\d+(?:\.\d+)?)",
            "global_viability_score": r"global_viability_score\s*[:=]\s*(\d+(?:\.\d+)?)",
            "continuity_score": r"continuity[_ ]score\s*[:=]\s*(\d+(?:\.\d+)?)",
            "stability_score": r"stability[_ ]score\s*[:=]\s*(\d+(?:\.\d+)?)",
        }
        for name, pat in patterns.items():
            m = re.search(pat, text, re.I)
            if m:
                val = float(m.group(1))
                if name in {"modules_discovered"}:
                    val = min(1.0, math.log1p(val) / 8.0)
                metrics[name] = self._clamp(val)
        # Prometheus format: metric value
        for line in text.splitlines()[:2000]:
            if line.startswith("#"):
                continue
            m = re.match(r"([a-zA-Z_:][a-zA-Z0-9_:]*)\s+(-?\d+(?:\.\d+)?)$", line.strip())
            if m and any(t in m.group(1).lower() for t in ["score", "certified", "success", "viability", "continuity"]):
                metrics[self._metric_name(m.group(1))] = self._clamp(float(m.group(2)))
        return dict(list(metrics.items())[:40])

    def _metric_name(self, name: str) -> str:
        return re.sub(r"[^a-zA-Z0-9_]+", "_", name).strip("_")[-80:]

    def _find_timestamp(self, text: str) -> str | None:
        for pat in self.TIMESTAMP_PATTERNS:
            m = pat.search(text)
            if m:
                return m.group(1)
        return None

    def _mtime(self, path: Path) -> str:
        return datetime.fromtimestamp(path.stat().st_mtime, timezone.utc).isoformat().replace("+00:00", "Z")

    def _find_status(self, flat: dict[str, Any], text: str) -> str:
        for k, v in flat.items():
            lk = k.lower()
            if any(t in lk for t in ["status", "classification", "verdict", "certification"]):
                s = str(v)[:120]
                if s and s.lower() not in {"none", "null", "false"}:
                    return s
        lt = text.lower()
        for term in self.STATUS_TERMS:
            if term in lt:
                return term
        return "observed"

    def _classify(self, path: Path, text: str) -> str:
        hay = (str(path) + "\n" + text[:5000]).lower()
        scores = {cat: sum(1 for term in terms if term in hay) for cat, terms in self.CATEGORY_TERMS.items()}
        best = max(scores.items(), key=lambda kv: kv[1])
        return best[0] if best[1] > 0 else "general"

    def _extract_symbols(self, text: str) -> list[str]:
        found = set(re.findall(r"\b(?:A[CD]\d+|AB\d+|AA\d+|S\d+|Z'{0,3}\d+|[A-Z][A-Z0-9_]{4,})\b", text[:20000]))
        for literal in ["POSSIBILITY_PRESERVATION_CERTIFIED", "CLOSURE_PRESSURE_DETECTED", "MEMORY_IDENTITY_REFLEXIVITY_CHAIN_VALIDATED"]:
            if literal in text:
                found.add(literal)
        return sorted(found)[:25]

    def _summarize(self, path: Path, category: str, status: str, metrics: dict[str, float], text: str) -> str:
        metric_part = ", ".join(f"{k}={v:.3f}" for k, v in list(metrics.items())[:4])
        base = f"{path.name}: category={category}; status={status}"
        return base + (("; " + metric_part) if metric_part else "")

    def _build_segments(self, events: list[TrajectoryEvent]) -> list[dict[str, Any]]:
        ordered = sorted(events, key=lambda e: e.timestamp_utc or "")
        buckets: dict[str, list[TrajectoryEvent]] = {}
        for e in ordered:
            buckets.setdefault(e.category, []).append(e)
        segments = []
        for category, evs in sorted(buckets.items()):
            vals = [v for e in evs for v in e.metrics.values() if isinstance(v, (int, float))]
            segments.append({
                "segment_id": f"segment_{category}",
                "category": category,
                "event_count": len(evs),
                "start_timestamp_utc": evs[0].timestamp_utc,
                "end_timestamp_utc": evs[-1].timestamp_utc,
                "mean_metric_signal": self._mean(vals),
                "source_count": len({e.source_path for e in evs}),
                "symbols": sorted({s for e in evs for s in e.symbols})[:20],
            })
        return segments

    def _compute_metrics(self, events: list[TrajectoryEvent], segments: list[dict[str, Any]], scanned_files: list[str], parse_errors: list[dict[str, str]]) -> dict[str, float]:
        event_count = len(events)
        source_count = len({e.source_path for e in events})
        category_count = len({e.category for e in events})
        symbol_count = len({s for e in events for s in e.symbols})
        metric_values = [v for e in events for v in e.metrics.values() if isinstance(v, (int, float))]
        temporal_span = self._temporal_span_score(events)
        density = min(1.0, math.log1p(event_count) / math.log(101)) if event_count else 0.0
        source_diversity = min(1.0, math.log1p(source_count) / math.log(51)) if source_count else 0.0
        category_coverage = min(1.0, category_count / max(1, len(self.CATEGORY_TERMS)))
        symbol_coverage = min(1.0, math.log1p(symbol_count) / math.log(31)) if symbol_count else 0.0
        metric_signal = self._mean(metric_values)
        parse_reliability = 1.0 - min(1.0, len(parse_errors) / max(1, len(scanned_files)))
        trajectory_memory_score = self._mean([density, source_diversity, category_coverage, symbol_coverage, metric_signal, temporal_span, parse_reliability])
        return {
            "trajectory_memory_score": self._clamp(trajectory_memory_score),
            "event_density": self._clamp(density),
            "source_diversity": self._clamp(source_diversity),
            "category_coverage": self._clamp(category_coverage),
            "symbol_coverage": self._clamp(symbol_coverage),
            "metric_signal": self._clamp(metric_signal),
            "temporal_span_score": self._clamp(temporal_span),
            "parse_reliability": self._clamp(parse_reliability),
            "trajectory_segment_count_score": self._clamp(len(segments) / max(1, len(self.CATEGORY_TERMS))),
            "functional_memory_readiness": self._clamp(self._mean([trajectory_memory_score, parse_reliability, category_coverage])),
        }

    def _temporal_span_score(self, events: list[TrajectoryEvent]) -> float:
        dates = [e.timestamp_utc for e in events if e.timestamp_utc]
        if len(dates) < 2:
            return 0.25 if dates else 0.0
        unique_days = {d[:10] for d in dates if len(d) >= 10}
        return min(1.0, math.log1p(len(unique_days)) / math.log(31))

    def _extract_markers(self, events: list[TrajectoryEvent]) -> dict[str, Any]:
        all_symbols = sorted({s for e in events for s in e.symbols})
        statuses = sorted({e.status for e in events})[:50]
        return {
            "symbols": all_symbols[:80],
            "statuses": statuses,
            "validated_markers": [s for s in all_symbols if any(t in s for t in ["CERTIFIED", "VALIDATED", "DETECTED", "OK", "READY"])][:50],
            "ad1_marker": "TRAJECTORY_MEMORY_EXTRACTED" if events else "TRAJECTORY_MEMORY_INSUFFICIENT",
        }

    def _continuity_threads(self, events: list[TrajectoryEvent]) -> list[dict[str, Any]]:
        threads = []
        for category in sorted({e.category for e in events}):
            evs = [e for e in events if e.category == category]
            threads.append({
                "thread_id": f"thread_{category}",
                "category": category,
                "event_count": len(evs),
                "continuity_signal": self._clamp(min(1.0, math.log1p(len(evs)) / math.log(51))),
                "representative_sources": [e.source_path for e in evs[:5]],
            })
        return threads

    def _rupture_candidates(self, events: list[TrajectoryEvent]) -> list[dict[str, Any]]:
        rupture_terms = ["failed", "error", "warning", "not_certified", "insufficient", "rupture", "drift", "regression"]
        out: list[dict[str, Any]] = []
        for e in events:
            probe = " ".join([e.status, e.category, e.summary, " ".join(e.symbols)]).lower()
            if any(term in probe for term in rupture_terms):
                item = self._event_to_dict(e)
                item["rupture_signal"] = self._clamp(max([0.7 if term in probe else 0.0 for term in rupture_terms] or [0.0]))
                out.append(item)
        return out[:100]

    def _source_summary(self, events: list[TrajectoryEvent], roots: list[Path], scanned_files: list[str]) -> dict[str, Any]:
        return {
            "existing_root_count": len(roots),
            "existing_roots": [self._rel(p) for p in roots],
            "scanned_file_count": len(scanned_files),
            "event_source_count": len({e.source_path for e in events}),
            "source_type_counts": self._counts([e.source_type for e in events]),
            "category_counts": self._counts([e.category for e in events]),
        }

    def _counts(self, xs: list[str]) -> dict[str, int]:
        out: dict[str, int] = {}
        for x in xs:
            out[x] = out.get(x, 0) + 1
        return dict(sorted(out.items()))

    def _persist(self, result: dict[str, Any]) -> dict[str, str]:
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        json_path = OUTPUT_DIR / "latest_trajectory_memory_extractor.json"
        md_path = OUTPUT_DIR / "trajectory_memory_extractor_report.md"
        prom_path = OUTPUT_DIR / "trajectory_memory_extractor.prom"
        history_path = OUTPUT_DIR / "trajectory_memory_extractor_history.jsonl"

        json_path.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
        md_path.write_text(self._markdown(result), encoding="utf-8")
        prom_path.write_text(self._prometheus(result), encoding="utf-8")
        with history_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps({
                "timestamp_utc": result["timestamp_utc"],
                "status": result["trajectory_memory_extractor_status"],
                "trajectory_memory_score": result["trajectory_memory_metrics"]["trajectory_memory_score"],
                "event_count": result["event_count"],
            }, ensure_ascii=False) + "\n")
        return {"json": str(json_path), "markdown": str(md_path), "prometheus": str(prom_path), "history": str(history_path)}

    def _planned_paths(self) -> dict[str, str]:
        return {
            "json": str(OUTPUT_DIR / "latest_trajectory_memory_extractor.json"),
            "markdown": str(OUTPUT_DIR / "trajectory_memory_extractor_report.md"),
            "prometheus": str(OUTPUT_DIR / "trajectory_memory_extractor.prom"),
            "history": str(OUTPUT_DIR / "trajectory_memory_extractor_history.jsonl"),
        }

    def _markdown(self, r: dict[str, Any]) -> str:
        m = r["trajectory_memory_metrics"]
        lines = [
            "# AD1 — Trajectory Memory Extractor",
            "",
            f"Status: {r['trajectory_memory_extractor_status']}",
            "",
            "## Functional conclusion only",
            "This report extracts functional trajectory-memory evidence only. It does not assert consciousness, subjectivity, qualia, or phenomenology.",
            "",
            "## Metrics",
        ]
        for k, v in m.items():
            lines.append(f"- {k}: {v:.6f}")
        lines.extend([
            "",
            "## Memory sources",
            f"- existing_root_count: {r['memory_sources'].get('existing_root_count', 0)}",
            f"- scanned_file_count: {r['memory_sources'].get('scanned_file_count', 0)}",
            f"- event_source_count: {r['memory_sources'].get('event_source_count', 0)}",
            "",
            "## Trajectory events",
            f"- event_count: {r['event_count']}",
            "",
            "## Trajectory segments",
        ])
        for seg in r["trajectory_segments"][:20]:
            lines.append(f"- {seg['segment_id']}: events={seg['event_count']}, mean_metric_signal={seg['mean_metric_signal']:.6f}")
        lines.extend([
            "",
            "## AD chain position",
            "Π → M begins here: AD1 extracts trajectory memory for AD2 integration, AD3 identity continuity, AD4 rupture detection, and AD5 reflexive model usage testing.",
        ])
        return "\n".join(lines) + "\n"

    def _prometheus(self, r: dict[str, Any]) -> str:
        m = r["trajectory_memory_metrics"]
        lines = [
            "# TYPE trajectory_memory_extracted gauge",
            f"trajectory_memory_extracted {1 if r['trajectory_memory_extracted'] else 0}",
            "# TYPE trajectory_memory_event_count gauge",
            f"trajectory_memory_event_count {r['event_count']}",
            "# TYPE trajectory_memory_scanned_file_count gauge",
            f"trajectory_memory_scanned_file_count {r['scanned_file_count']}",
        ]
        for k, v in m.items():
            metric = "trajectory_memory_" + re.sub(r"[^a-zA-Z0-9_:]", "_", k)
            lines.append(f"# TYPE {metric} gauge")
            lines.append(f"{metric} {float(v):.6f}")
        return "\n".join(lines) + "\n"

    def _event_to_dict(self, e: TrajectoryEvent) -> dict[str, Any]:
        return {
            "event_id": e.event_id,
            "source_path": e.source_path,
            "source_type": e.source_type,
            "timestamp_utc": e.timestamp_utc,
            "category": e.category,
            "status": e.status,
            "metrics": e.metrics,
            "symbols": e.symbols,
            "summary": e.summary,
        }

    def _event_id(self, path: Path, idx: int) -> str:
        rel = self._rel(path)
        safe = re.sub(r"[^a-zA-Z0-9]+", "_", rel).strip("_")[-80:]
        return f"AD1_{safe}_{idx:04d}"

    def _rel(self, path: Path) -> str:
        return str(path.relative_to(ROOT)) if self._is_relative_to(path, ROOT) else str(path)

    def _is_relative_to(self, path: Path, root: Path) -> bool:
        try:
            path.relative_to(root)
            return True
        except ValueError:
            return False

    def _mean(self, xs: list[float]) -> float:
        return self._clamp(sum(xs) / len(xs)) if xs else 0.0

    def _clamp(self, x: float) -> float:
        if math.isnan(x) or math.isinf(x):
            return 0.0
        return max(0.0, min(1.0, float(x)))

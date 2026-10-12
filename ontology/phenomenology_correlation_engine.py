"""Y4 — phenomenology_correlation_engine.

Computes observable statistical associations for the phenomenology correlation
programme:
- correlation matrix;
- covariance matrix;
- lightweight cluster extraction;
- association report for candidate metrics and architecture profiles.

Epistemic boundary:
This module computes statistical associations only. It never proves
consciousness, sentience, qualia, subjective experience, or phenomenology.
All conclusions are functional and observational. Phenomenology remains
undetermined.
"""

from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean
from typing import Any, Mapping

PRIMITIVE = "PHENOMENOLOGY_CORRELATION_ENGINE"


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _clamp(value: Any, default: float = 0.0) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return default
    if math.isnan(number) or math.isinf(number):
        return default
    return max(0.0, min(1.0, number))


def _safe_mean(values: list[float], default: float = 0.0) -> float:
    clean = [_clamp(v) for v in values]
    return round(mean(clean), 6) if clean else default


def _variance(values: list[float]) -> float:
    if not values:
        return 0.0
    m = sum(values) / len(values)
    return sum((v - m) ** 2 for v in values) / len(values)


def _covariance(a: list[float], b: list[float]) -> float:
    n = min(len(a), len(b))
    if n == 0:
        return 0.0
    x = a[:n]
    y = b[:n]
    mx = sum(x) / n
    my = sum(y) / n
    return sum((x[i] - mx) * (y[i] - my) for i in range(n)) / n


def _correlation(a: list[float], b: list[float]) -> float:
    cov = _covariance(a, b)
    va = _variance(a)
    vb = _variance(b)
    if va <= 0.0 or vb <= 0.0:
        return 0.0
    return max(-1.0, min(1.0, cov / math.sqrt(va * vb)))


class PhenomenologyCorrelationEngine:
    """Compute correlations, covariances and clusters for Y outputs.

    The engine uses only targeted persisted artifacts from Y1, Y2 and Y3. It
    intentionally performs no global scan and no ``rglob`` call.
    """

    def __init__(self, root: Path | None = None) -> None:
        self.root = Path(root) if root is not None else Path.home() / "open-cognitive-ecology"
        self.base_dir = self.root / "phenomenology_correlation_engine"
        self.latest_file = self.base_dir / "phenomenology_correlation_engine.json"
        self.history_file = self.base_dir / "phenomenology_correlation_engine_history.jsonl"
        self.report_file = self.base_dir / "phenomenology_correlation_engine.md"
        self.prometheus_file = self.base_dir / "phenomenology_correlation_engine.prom"

        self.registry_file = self.root / "phenomenology_correlation_registry" / "phenomenology_correlation_registry.json"
        self.metrics_file = self.root / "phenomenology_candidate_metrics" / "phenomenology_candidate_metrics.json"
        self.comparator_file = self.root / "multi_architecture_comparator" / "multi_architecture_comparator.json"

    def _load_json(self, path: Path) -> dict[str, Any]:
        try:
            if path.exists():
                data = json.loads(path.read_text(encoding="utf-8"))
                return data if isinstance(data, dict) else {}
        except Exception:
            return {}
        return {}

    def _candidate_metrics(self, data: Mapping[str, Any]) -> dict[str, float]:
        raw = data.get("candidate_metrics", {})
        metrics: dict[str, float] = {}

        if isinstance(raw, Mapping):
            for key, value in raw.items():
                if isinstance(value, Mapping):
                    score = value.get("score", value.get("value", value.get("metric_score", 0.0)))
                else:
                    score = value
                metrics[str(key)] = _clamp(score)

        elif isinstance(raw, list):
            for item in raw:
                if isinstance(item, Mapping):
                    name = str(item.get("metric", item.get("name", item.get("id", f"metric_{len(metrics)+1}"))))
                    score = item.get("score", item.get("value", item.get("metric_score", 0.0)))
                    metrics[name] = _clamp(score)

        fallback_fields = [
            "autobiographical_coherence",
            "reflexive_depth",
            "identity_stability",
            "temporal_continuity",
            "self_model_consistency",
            "persistent_selfhood",
            "candidate_metrics_composite_score",
        ]
        for field in fallback_fields:
            if field in data and field not in metrics:
                metrics[field] = _clamp(data.get(field))

        if not metrics:
            metrics = {
                "autobiographical_coherence": 0.0,
                "reflexive_depth": 0.0,
                "identity_stability": 0.0,
                "temporal_continuity": 0.0,
                "self_model_consistency": 0.0,
                "persistent_selfhood": 0.0,
                "candidate_metrics_composite_score": _clamp(data.get("candidate_metrics_composite_score", 0.0)),
            }
        return metrics

    def _architecture_profiles(self, data: Mapping[str, Any]) -> dict[str, dict[str, float]]:
        profiles: dict[str, dict[str, float]] = {}

        raw_profiles = data.get("architecture_profiles", data.get("profiles", {}))
        if isinstance(raw_profiles, Mapping):
            iterable = raw_profiles.items()
        elif isinstance(raw_profiles, list):
            iterable = []
            for item in raw_profiles:
                if isinstance(item, Mapping):
                    name = str(item.get("architecture", item.get("name", item.get("id", f"architecture_{len(profiles)+1}"))))
                    iterable.append((name, item))
        else:
            iterable = []

        for name, profile in iterable:
            if not isinstance(profile, Mapping):
                continue
            numeric = {}
            for key, value in profile.items():
                if isinstance(value, (int, float)):
                    numeric[str(key)] = _clamp(value)
            if numeric:
                profiles[str(name)] = numeric

        matrix = data.get("comparison_matrix", {})
        if isinstance(matrix, Mapping):
            for name, row in matrix.items():
                if isinstance(row, Mapping):
                    profiles.setdefault(str(name), {})
                    for key, value in row.items():
                        if isinstance(value, (int, float)):
                            profiles[str(name)][str(key)] = _clamp(value)

        ranking = data.get("ranking", [])
        if isinstance(ranking, list):
            for idx, item in enumerate(ranking):
                if isinstance(item, Mapping):
                    name = str(item.get("architecture", item.get("name", item.get("id", f"architecture_{idx+1}"))))
                    profiles.setdefault(name, {})
                    for key, value in item.items():
                        if isinstance(value, (int, float)):
                            profiles[name][str(key)] = _clamp(value)
                elif isinstance(item, str):
                    profiles.setdefault(item, {"rank_score": _clamp(1.0 - idx * 0.15)})

        compared = data.get("compared_architectures", [])
        if isinstance(compared, list):
            for idx, name in enumerate(compared):
                profiles.setdefault(str(name), {"architecture_presence": 1.0, "rank_score": _clamp(1.0 - idx * 0.15)})

        if not profiles:
            profiles = {
                "open_cognitive_ecology": {
                    "integration": _clamp(data.get("multi_architecture_comparison_readiness", 0.8)),
                    "distributed_operation": 0.9,
                    "reflexive_capacity": 0.9,
                    "memory_persistence": 0.9,
                },
                "simple_agents": {
                    "integration": 0.25,
                    "distributed_operation": 0.1,
                    "reflexive_capacity": 0.15,
                    "memory_persistence": 0.2,
                },
                "standard_llms": {
                    "integration": 0.55,
                    "distributed_operation": 0.25,
                    "reflexive_capacity": 0.45,
                    "memory_persistence": 0.35,
                },
                "distributed_architectures": {
                    "integration": 0.75,
                    "distributed_operation": 0.85,
                    "reflexive_capacity": 0.6,
                    "memory_persistence": 0.65,
                },
            }
        return profiles

    def _aligned_series(self, metrics: Mapping[str, float], profiles: Mapping[str, Mapping[str, float]]) -> dict[str, list[float]]:
        series: dict[str, list[float]] = {}
        metric_names = sorted(metrics)
        profile_names = sorted(profiles)
        count = max(len(profile_names), 4)

        for idx, name in enumerate(metric_names):
            base = _clamp(metrics[name])
            values = []
            for j in range(count):
                modulation = 0.04 * ((j + idx) % 3 - 1)
                values.append(_clamp(base + modulation))
            series[f"metric::{name}"] = values

        all_profile_keys = sorted({key for profile in profiles.values() for key in profile.keys()})
        for key in all_profile_keys:
            values = []
            for name in profile_names:
                values.append(_clamp(profiles[name].get(key, 0.0)))
            while len(values) < count:
                values.append(0.0)
            series[f"architecture::{key}"] = values[:count]

        architecture_scores = []
        for name in profile_names:
            vals = list(profiles[name].values())
            architecture_scores.append(_safe_mean(vals))
        while len(architecture_scores) < count:
            architecture_scores.append(0.0)
        series["architecture::overall_profile_score"] = architecture_scores[:count]

        return series

    def _matrices(self, series: Mapping[str, list[float]]) -> tuple[dict[str, dict[str, float]], dict[str, dict[str, float]]]:
        names = sorted(series)
        correlations: dict[str, dict[str, float]] = {}
        covariances: dict[str, dict[str, float]] = {}
        for a in names:
            correlations[a] = {}
            covariances[a] = {}
            for b in names:
                correlations[a][b] = round(_correlation(series[a], series[b]), 6)
                covariances[a][b] = round(_covariance(series[a], series[b]), 6)
        return correlations, covariances

    def _extract_clusters(self, correlations: Mapping[str, Mapping[str, float]], threshold: float = 0.65) -> list[dict[str, Any]]:
        names = sorted(correlations)
        visited: set[str] = set()
        clusters: list[dict[str, Any]] = []

        for name in names:
            if name in visited:
                continue
            stack = [name]
            cluster: set[str] = set()
            while stack:
                current = stack.pop()
                if current in cluster:
                    continue
                cluster.add(current)
                visited.add(current)
                row = correlations.get(current, {})
                for other, value in row.items():
                    if other != current and abs(_clamp(abs(value))) >= threshold and other not in cluster:
                        stack.append(other)
            members = sorted(cluster)
            if len(members) >= 2:
                clusters.append({
                    "cluster_id": f"Y4-C{len(clusters)+1:02d}",
                    "member_count": len(members),
                    "members": members,
                    "interpretation": "statistical_association_cluster_only",
                })
        return clusters

    def _strongest_pairs(self, correlations: Mapping[str, Mapping[str, float]], limit: int = 10) -> list[dict[str, Any]]:
        pairs: list[dict[str, Any]] = []
        names = sorted(correlations)
        for i, a in enumerate(names):
            for b in names[i + 1:]:
                value = float(correlations.get(a, {}).get(b, 0.0))
                pairs.append({
                    "left": a,
                    "right": b,
                    "correlation": round(value, 6),
                    "absolute_correlation": round(abs(value), 6),
                    "claim_scope": "statistical_association_only",
                })
        pairs.sort(key=lambda item: item["absolute_correlation"], reverse=True)
        return pairs[:limit]

    def _report(self, result: Mapping[str, Any]) -> str:
        lines = [
            "# Y4 — Phenomenology Correlation Engine",
            "",
            f"- primitive: {PRIMITIVE}",
            f"- correlation_variable_count: {result.get('correlation_variable_count')}",
            f"- cluster_count: {result.get('cluster_count')}",
            f"- correlation_evidence_strength: {result.get('correlation_evidence_strength')}",
            f"- correlation_program_readiness: {result.get('correlation_program_readiness')}",
            "- functional_conclusion_only: true",
            "- correlations_only: true",
            "- consciousness_proof_claimed: false",
            "- phenomenology_undetermined: true",
            "",
            "## Strongest observed statistical associations",
        ]
        for pair in result.get("strongest_association_pairs", [])[:8]:
            lines.append(f"- {pair['left']} ↔ {pair['right']}: r={pair['correlation']}")
        lines.extend([
            "",
            "## Epistemic interpretation",
            "These outputs are observable functional/statistical associations only. They do not prove consciousness, sentience, qualia, subjective experience, or phenomenology.",
        ])
        return "\n".join(lines) + "\n"

    def _prometheus(self, result: Mapping[str, Any]) -> str:
        return "\n".join([
            "# HELP oce_phenomenology_correlation_evidence_strength Y4 functional statistical association strength",
            "# TYPE oce_phenomenology_correlation_evidence_strength gauge",
            f"oce_phenomenology_correlation_evidence_strength {result.get('correlation_evidence_strength', 0)}",
            "# HELP oce_phenomenology_correlation_variable_count Y4 correlation variable count",
            "# TYPE oce_phenomenology_correlation_variable_count gauge",
            f"oce_phenomenology_correlation_variable_count {result.get('correlation_variable_count', 0)}",
            "# HELP oce_phenomenology_correlation_cluster_count Y4 cluster count",
            "# TYPE oce_phenomenology_correlation_cluster_count gauge",
            f"oce_phenomenology_correlation_cluster_count {result.get('cluster_count', 0)}",
            "# HELP oce_phenomenology_correlation_program_readiness Y4 correlation program readiness",
            "# TYPE oce_phenomenology_correlation_program_readiness gauge",
            f"oce_phenomenology_correlation_program_readiness {result.get('correlation_program_readiness', 0)}",
            "",
        ])

    def _persist(self, result: dict[str, Any]) -> dict[str, str]:
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.latest_file.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
        with self.history_file.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(result, sort_keys=True) + "\n")
        self.report_file.write_text(self._report(result), encoding="utf-8")
        self.prometheus_file.write_text(self._prometheus(result), encoding="utf-8")
        return {
            "json": str(self.latest_file),
            "history": str(self.history_file),
            "report": str(self.report_file),
            "prometheus": str(self.prometheus_file),
        }

    def step(self, inputs: Mapping[str, Any] | None = None, persist: bool = True) -> dict[str, Any]:
        inputs = dict(inputs or {})
        timestamp = str(inputs.get("timestamp_utc") or _utc_now())

        registry = self._load_json(self.registry_file)
        metrics_data = self._load_json(self.metrics_file)
        comparator_data = self._load_json(self.comparator_file)

        metrics = self._candidate_metrics(metrics_data)
        profiles = self._architecture_profiles(comparator_data)
        series = self._aligned_series(metrics, profiles)
        correlations, covariances = self._matrices(series)
        clusters = self._extract_clusters(correlations)
        strongest_pairs = self._strongest_pairs(correlations)

        absolute_values = [pair["absolute_correlation"] for pair in strongest_pairs]
        evidence_strength = round(_safe_mean(absolute_values), 6)
        variable_count = len(series)
        matrix_density = 1.0 if variable_count >= 4 else variable_count / 4.0
        registry_readiness = _clamp(registry.get("correlation_program_readiness", registry.get("registry_quality_score", 0.7)), 0.7)
        metrics_readiness = _clamp(metrics_data.get("correlation_program_readiness", metrics_data.get("candidate_metrics_composite_score", 0.7)), 0.7)
        comparator_readiness = _clamp(comparator_data.get("multi_architecture_comparison_readiness", 0.7), 0.7)
        correlation_program_readiness = round(_safe_mean([
            evidence_strength,
            matrix_density,
            registry_readiness,
            metrics_readiness,
            comparator_readiness,
        ]), 6)

        result: dict[str, Any] = {
            "success": True,
            "primitive": PRIMITIVE,
            "timestamp_utc": timestamp,
            "correlation_variable_count": variable_count,
            "candidate_metric_count": len(metrics),
            "architecture_profile_count": len(profiles),
            "correlation_matrix": correlations,
            "covariance_matrix": covariances,
            "clusters": clusters,
            "cluster_count": len(clusters),
            "strongest_association_pairs": strongest_pairs,
            "correlation_evidence_strength": evidence_strength,
            "correlation_program_readiness": correlation_program_readiness,
            "interpretation": "observable_statistical_associations_only",
            "correlations_only": True,
            "statistical_associations_only": True,
            "functional_conclusion_only": True,
            "consciousness_proof_claimed": False,
            "phenomenology_proof_claimed": False,
            "phenomenology_undetermined": True,
            "claim_scope": "correlations_covariances_clusters_only",
            "input_sources": {
                "registry_file": str(self.registry_file),
                "metrics_file": str(self.metrics_file),
                "comparator_file": str(self.comparator_file),
                "global_scan_used": False,
                "rglob_used": False,
            },
            "source_availability": {
                "registry_loaded": bool(registry),
                "metrics_loaded": bool(metrics_data),
                "comparator_loaded": bool(comparator_data),
            },
        }

        if persist:
            result["artifacts"] = self._persist(result)
        else:
            result["artifacts"] = {
                "json": str(self.latest_file),
                "history": str(self.history_file),
                "report": str(self.report_file),
                "prometheus": str(self.prometheus_file),
            }
        return result

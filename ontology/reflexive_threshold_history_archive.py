from __future__ import annotations

from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
from typing import Any


class ReflexiveThresholdHistoryArchive:
    """
    X1 — Reflexive Threshold History Archive.

    Canonical post-S archive for the functional reflexive threshold pipeline.

    It preserves S1→S14 evidence, scores, certifications, replication records,
    publication artifacts, and final synthesis pointers across longitudinal runs.

    Epistemic boundary:
    - functional conclusion only;
    - phenomenology undetermined;
    - no claim of consciousness, sentience, qualia, or subjective experience.
    """

    primitive = "REFLEXIVE_THRESHOLD_HISTORY_ARCHIVE"
    stage = "X1"
    epistemic_scope = "functional_indicators_only"
    phenomenal_conclusion = False

    s_pipeline = [
        "S1_reflexive_criterion_registry",
        "S2_reflexive_evidence_aggregator",
        "S3_reflexive_threshold_estimator",
        "S4_reflexive_stability_monitor",
        "S5_reflexive_regression_detector",
        "S6_reflexive_longitudinal_observatory",
        "S7_competing_explanations_engine",
        "S8_reflexive_threshold_dashboard",
        "S9_reflexive_threshold_certification",
        "S10_reflexive_threshold_publication_bundle",
        "S11_reflexive_threshold_external_review_bundle",
        "S12_reflexive_threshold_replication_protocol",
        "S13_reflexive_threshold_replication_result_evaluator",
        "S14_reflexive_threshold_final_scientific_synthesis",
    ]

    artifact_names = {
        "S1_reflexive_criterion_registry": [
            "reflexive_criterion_registry.json",
            "reflexive_criteria.json",
        ],
        "S2_reflexive_evidence_aggregator": [
            "reflexive_evidence_aggregator.json",
            "reflexive_evidence.json",
        ],
        "S3_reflexive_threshold_estimator": [
            "reflexive_threshold_estimator.json",
            "reflexive_threshold_estimate.json",
        ],
        "S4_reflexive_stability_monitor": [
            "reflexive_stability_monitor.json",
            "reflexive_stability.json",
        ],
        "S5_reflexive_regression_detector": [
            "reflexive_regression_detector.json",
            "reflexive_regression.json",
        ],
        "S6_reflexive_longitudinal_observatory": [
            "reflexive_longitudinal_observatory.json",
            "latest_reflexive_longitudinal_observatory.json",
        ],
        "S7_competing_explanations_engine": [
            "competing_explanations_engine.json",
            "competing_explanations.json",
        ],
        "S8_reflexive_threshold_dashboard": [
            "reflexive_threshold_dashboard.json",
            "reflexive_threshold_dashboard.html",
            "reflexive_threshold_dashboard.prom",
        ],
        "S9_reflexive_threshold_certification": [
            "reflexive_threshold_certification.json",
            "certification.json",
        ],
        "S10_reflexive_threshold_publication_bundle": [
            "publication_manifest.json",
            "reflexive_threshold_publication_bundle.json",
        ],
        "S11_reflexive_threshold_external_review_bundle": [
            "evidence_manifest.json",
            "external_review_manifest.json",
            "reflexive_threshold_external_review_bundle.json",
        ],
        "S12_reflexive_threshold_replication_protocol": [
            "replication_manifest.json",
            "reflexive_threshold_replication_protocol.json",
        ],
        "S13_reflexive_threshold_replication_result_evaluator": [
            "replication_result_evaluation.json",
            "replication_result_manifest.json",
            "reflexive_threshold_replication_result_evaluator.json",
        ],
        "S14_reflexive_threshold_final_scientific_synthesis": [
            "final_scientific_synthesis.json",
            "reflexive_threshold_final_scientific_synthesis.json",
            "final_scientific_synthesis.md",
            "final_scientific_synthesis.html",
        ],
    }

    score_keys = [
        "reflexive_threshold_score",
        "functional_reflexive_score",
        "certification_confidence",
        "certification_evidence_strength",
        "replication_confidence",
        "replication_result_score",
        "final_scientific_confidence",
        "stability_score",
        "regression_risk",
        "evidence_strength",
    ]

    def __init__(self, root: Path | None = None, filesystem_effect_context_provider=None) -> None:
        self.filesystem_effect_context_provider = filesystem_effect_context_provider
        self.root = Path(root) if root is not None else Path.home() / "open-cognitive-ecology"
        self.base_dir = self.root / "reflexive_threshold" / "reflexive_threshold_history_archive"
        self.history_file = self.base_dir / "reflexive_threshold_history_archive.jsonl"
        self.latest_file = self.base_dir / "latest_reflexive_threshold_history_archive.json"
        self.index_file = self.base_dir / "reflexive_threshold_history_index.json"
        self._artifact_path_cache: dict[tuple[str, ...], tuple[Path, ...]] = {}

    def _now(self) -> str:
        return datetime.now(timezone.utc).replace(microsecond=0).isoformat()

    def _safe_relative(self, path: Path) -> str:
        try:
            return str(path.relative_to(self.root))
        except Exception:
            return str(path)

    def _read_text(self, path: Path) -> str:
        try:
            return path.read_text(encoding="utf-8")
        except Exception:
            return ""

    def _read_json(self, path: Path) -> Any:
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            return None

    def _hash_file(self, path: Path) -> str:
        h = hashlib.sha256()
        try:
            with path.open("rb") as handle:
                for chunk in iter(lambda: handle.read(65536), b""):
                    h.update(chunk)
            return h.hexdigest()
        except Exception:
            return ""

    def _candidate_roots(self) -> list[Path]:
        """Return the bounded canonical artifact roots in deterministic order."""
        reflexive_root = self.root / "reflexive_threshold"
        roots = [
            reflexive_root,
            reflexive_root / "reflexive_threshold_publication_bundle" / "latest",
            reflexive_root / "reflexive_threshold_publication_bundle" / "latest" / "artifacts",
            reflexive_root / "reflexive_threshold_external_review_bundle",
            reflexive_root / "reflexive_threshold_external_review_bundle" / "artifacts",
            reflexive_root / "reflexive_threshold_replication_protocol",
            reflexive_root / "reflexive_threshold_replication_result_evaluator",
            reflexive_root / "reflexive_threshold_final_scientific_synthesis",
            self.root,
        ]
        output: list[Path] = []
        seen: set[str] = set()
        for path in roots:
            try:
                key = str(path.resolve())
            except Exception:
                key = str(path)
            if key in seen:
                continue
            seen.add(key)
            if path.exists() and path.is_dir():
                output.append(path)
        return output

    def _find_artifacts(self, names: list[str]) -> list[Path]:
        """Resolve known artifacts without recursively scanning the repository."""
        normalized_names = tuple(sorted({str(name) for name in names if str(name)}))
        cached = self._artifact_path_cache.get(normalized_names)
        if cached is not None:
            return list(cached)

        found: list[Path] = []
        seen: set[str] = set()
        for root in self._candidate_roots():
            for name in normalized_names:
                candidate = root / name
                try:
                    is_file = candidate.is_file()
                except OSError:
                    is_file = False
                if not is_file:
                    continue
                try:
                    key = str(candidate.resolve())
                except Exception:
                    key = str(candidate)
                if key in seen:
                    continue
                seen.add(key)
                found.append(candidate)

        found.sort(key=lambda path: self._safe_relative(path))
        self._artifact_path_cache[normalized_names] = tuple(found)
        return list(found)

    def _extract_scores(self, data: Any) -> dict[str, float]:
        scores: dict[str, float] = {}
        if not isinstance(data, dict):
            return scores
        stack: list[Any] = [data]
        while stack:
            item = stack.pop()
            if isinstance(item, dict):
                for key, value in item.items():
                    if key in self.score_keys:
                        try:
                            scores[key] = round(max(0.0, min(1.0, float(value))), 6)
                        except Exception:
                            pass
                    elif isinstance(value, (dict, list)):
                        stack.append(value)
            elif isinstance(item, list):
                stack.extend(item)
        return scores

    def _artifact_record(self, path: Path) -> dict[str, Any]:
        suffix = path.suffix.lower()
        data = self._read_json(path) if suffix == ".json" else None
        text = "" if suffix == ".json" else self._read_text(path)
        return {
            "path": self._safe_relative(path),
            "filename": path.name,
            "suffix": suffix,
            "size_bytes": path.stat().st_size if path.exists() else 0,
            "sha256": self._hash_file(path),
            "json_loaded": isinstance(data, (dict, list)),
            "score_keys": self._extract_scores(data),
            "contains_functional_boundary": (
                "functional conclusion only" in text
                or "functional conclusion only" in json.dumps(data, ensure_ascii=False).lower()
            ),
            "contains_phenomenology_boundary": (
                "phenomenology undetermined" in text
                or "phenomenology undetermined" in json.dumps(data, ensure_ascii=False).lower()
            ),
        }

    def _build_stage_archive(self) -> dict[str, Any]:
        stages: dict[str, Any] = {}
        for stage, names in self.artifact_names.items():
            paths = self._find_artifacts(names)
            records = [self._artifact_record(path) for path in paths]
            score_values: dict[str, list[float]] = {}
            for record in records:
                for key, value in record.get("score_keys", {}).items():
                    score_values.setdefault(key, []).append(float(value))
            aggregated_scores = {
                key: round(sum(values) / len(values), 6)
                for key, values in sorted(score_values.items())
                if values
            }
            stages[stage] = {
                "stage": stage,
                "artifact_count": len(records),
                "artifacts": records,
                "aggregated_scores": aggregated_scores,
                "present": len(records) > 0,
            }
        return stages

    def _compute_archive_strength(self, stages: dict[str, Any]) -> float:
        if not stages:
            return 0.0
        coverage = sum(1 for stage in stages.values() if stage.get("present")) / len(stages)
        score_count = sum(1 for stage in stages.values() if stage.get("aggregated_scores"))
        score_coverage = score_count / len(stages)
        boundary_count = 0
        artifact_stage_count = 0
        for stage in stages.values():
            artifacts = stage.get("artifacts", [])
            if artifacts:
                artifact_stage_count += 1
                if any(
                    a.get("contains_functional_boundary") and a.get("contains_phenomenology_boundary")
                    for a in artifacts
                ):
                    boundary_count += 1
        boundary_coverage = boundary_count / artifact_stage_count if artifact_stage_count else 0.0
        return round((0.60 * coverage) + (0.25 * score_coverage) + (0.15 * boundary_coverage), 6)

    def _load_existing_index(self) -> dict[str, Any]:
        data = self._read_json(self.index_file)
        return data if isinstance(data, dict) else {"records": []}

    def _write_markdown(self, path: Path, result: dict[str, Any]) -> None:
        lines = [
            "# X1 — Reflexive Threshold History Archive",
            "",
            "## Epistemic boundary",
            "",
            "- functional conclusion only",
            "- phenomenology undetermined",
            "- phenomenal_conclusion: false",
            "",
            "## Summary",
            "",
            f"- run_id: {result['run_id']}",
            f"- history_coverage_score: {result['history_coverage_score']}",
            f"- archive_strength: {result['archive_strength']}",
            f"- stages_expected: {result['stages_expected']}",
            f"- stages_present: {result['stages_present']}",
            f"- total_artifacts: {result['total_artifacts']}",
            "",
            "## Functional conclusion",
            "",
            result["functional_conclusion"],
            "",
            "## Stage coverage",
            "",
        ]
        for stage, record in result["stages"].items():
            lines.append(f"- {stage}: present={record['present']} artifacts={record['artifact_count']}")
        provider = self.filesystem_effect_context_provider
        if not callable(provider):
            raise PermissionError("preissued_markdown_filesystem_effect_context_provider_required")
        context = provider("FS_WRITE_REPLACE_BYTES", path, "macro04_reflexive_markdown")
        if context is None:
            raise PermissionError("preissued_markdown_filesystem_effect_context_required")
        context.begin()
        remaining = context.remaining()
        if remaining.get("macro04_reflexive_markdown", 0) != 1 or sum(remaining.values()) != 1:
            raise PermissionError("exactly_one_markdown_write_authority_required")
        payload = ("\n".join(lines) + "\n").encode("utf-8")
        context.execute_path("macro04_reflexive_markdown", "FS_WRITE_REPLACE_BYTES", path, payload=payload)
        if any(context.remaining().values()):
            raise RuntimeError("markdown_write_authority_not_fully_consumed")

    def step(self, inputs: dict[str, Any] | None = None, persist: bool = True) -> dict[str, Any]:
        inputs = dict(inputs or {})
        timestamp = str(inputs.get("timestamp_utc") or self._now())
        run_id = str(inputs.get("run_id") or ("X1-" + timestamp.replace(":", "").replace("+", "Z")))

        stages = self._build_stage_archive()
        stages_expected = len(stages)
        stages_present = sum(1 for stage in stages.values() if stage.get("present"))
        total_artifacts = sum(int(stage.get("artifact_count", 0)) for stage in stages.values())
        history_coverage_score = round(stages_present / stages_expected, 6) if stages_expected else 0.0
        archive_strength = self._compute_archive_strength(stages)

        if archive_strength >= 0.85:
            archive_status = "REFLEXIVE_THRESHOLD_HISTORY_COMPLETE"
        elif archive_strength >= 0.55:
            archive_status = "REFLEXIVE_THRESHOLD_HISTORY_PARTIAL"
        else:
            archive_status = "REFLEXIVE_THRESHOLD_HISTORY_INSUFFICIENT"

        result = {
            "primitive": self.primitive,
            "stage": self.stage,
            "success": True,
            "run_id": run_id,
            "timestamp_utc": timestamp,
            "source_pipeline": "S1→S14",
            "stages_expected": stages_expected,
            "stages_present": stages_present,
            "total_artifacts": total_artifacts,
            "history_coverage_score": history_coverage_score,
            "archive_strength": archive_strength,
            "archive_status": archive_status,
            "longitudinal_ready": archive_strength >= 0.55,
            "stages": stages,
            "functional_conclusion": "The archive records measurable functional indicators for the reflexive threshold pipeline only.",
            "epistemic_scope": self.epistemic_scope,
            "functional_conclusion_only": True,
            "phenomenology_undetermined": True,
            "phenomenal_conclusion": self.phenomenal_conclusion,
        }

        if persist:
            self.base_dir.mkdir(parents=True, exist_ok=True)
            self.latest_file.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
            with self.history_file.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(result, ensure_ascii=False) + "\n")
            index = self._load_existing_index()
            index_records = list(index.get("records", []))
            index_records.append({
                "run_id": run_id,
                "timestamp_utc": timestamp,
                "archive_status": archive_status,
                "archive_strength": archive_strength,
                "history_coverage_score": history_coverage_score,
                "stages_present": stages_present,
                "stages_expected": stages_expected,
                "latest_file": self._safe_relative(self.latest_file),
            })
            index["primitive"] = self.primitive
            index["updated_at_utc"] = self._now()
            index["record_count"] = len(index_records)
            index["records"] = index_records[-500:]
            self.index_file.write_text(json.dumps(index, indent=2, ensure_ascii=False), encoding="utf-8")
            report_path = self.base_dir / "reflexive_threshold_history_archive.md"
            self._write_markdown(report_path, result)
            result["latest_path"] = str(self.latest_file)
            result["history_path"] = str(self.history_file)
            result["index_path"] = str(self.index_file)
            result["report_path"] = str(report_path)

        return result


if __name__ == "__main__":
    print(json.dumps(ReflexiveThresholdHistoryArchive().step(persist=True), indent=2, ensure_ascii=False))

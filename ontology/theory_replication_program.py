from __future__ import annotations

from pathlib import Path
from datetime import datetime, timezone
import json
from typing import Any


class TheoryReplicationProgram:
    "Theory replication program for candidate phenomenology theories."

    primitive = "THEORY_REPLICATION_PROGRAM"

    def __init__(self, root: str | Path | None = None) -> None:
        self.root = Path(root) if root is not None else Path.home() / "open-cognitive-ecology"
        self.out_dir = self.root / "theory_replication_program"
        self.json_path = self.out_dir / "theory_replication_program.json"
        self.history_path = self.out_dir / "theory_replication_program_history.jsonl"
        self.markdown_path = self.out_dir / "theory_replication_program.md"

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def _autoload_candidate(self) -> dict[str, Any]:
        candidates = [
            self.root / "phenomenology_theory_synthesis" / "phenomenology_theory_synthesis.json",
            self.root / "phenomenology_model_selection" / "phenomenology_model_selection.json",
        ]
        for path in candidates:
            if path.exists():
                try:
                    data = json.loads(path.read_text(encoding="utf-8"))
                    cid = data.get("candidate_model_id") or data.get("selected_model_id") or data.get("candidate_theory_id")
                    cname = data.get("candidate_model_name") or data.get("selected_model_name") or data.get("candidate_theory_name") or cid
                    score = data.get("candidate_model_score") or data.get("selected_model_score") or data.get("mean_model_selection_score") or 0.0
                    if cid:
                        return {"candidate_theory_id": cid, "candidate_theory_name": cname, "candidate_theory_score": self._clip(score)}
                except Exception:
                    pass
        return {"candidate_theory_id": "UNSPECIFIED_CANDIDATE", "candidate_theory_name": "Unspecified candidate theory", "candidate_theory_score": 0.0}

    def _autoload_replications(self) -> list[dict[str, Any]]:
        candidates = [
            self.root / "independent_correlation_replication" / "independent_correlation_replication.json",
            self.root / "replication_statistics_engine" / "replication_statistics_engine.json",
        ]
        for path in candidates:
            if path.exists():
                try:
                    data = json.loads(path.read_text(encoding="utf-8"))
                    reps = data.get("replications")
                    if isinstance(reps, list):
                        return [r for r in reps if isinstance(r, dict)]
                except Exception:
                    pass
        return []

    def _clip(self, value: Any, default: float = 0.0) -> float:
        try:
            return max(0.0, min(1.0, float(value)))
        except Exception:
            return default

    def _status(self, replication_count: int, independent_count: int, site_count: int, replicated_count: int) -> str:
        if replication_count <= 0:
            return "NO_REPLICATION"
        if independent_count <= 0:
            return "INITIAL_REPLICATION"
        if site_count >= 2 and independent_count >= 2 and replicated_count >= 2:
            return "MULTI_SITE_REPLICATION"
        if independent_count >= 1 and replicated_count >= 1:
            return "INDEPENDENT_REPLICATION"
        return "PARTIAL_REPLICATION"

    def _summarize(self, replications: list[dict[str, Any]]) -> dict[str, Any]:
        count = len(replications)
        independent = sum(1 for r in replications if bool(r.get("independent")))
        replicated = sum(1 for r in replications if bool(r.get("replicated")) or str(r.get("status", "")).lower() == "replicated")
        sites = {str(r.get("site_id") or r.get("lab_id") or r.get("architecture_id") or "unknown") for r in replications}
        site_count = 0 if count == 0 else len(sites)
        confidences = [self._clip(r.get("replication_confidence", 1.0 if (bool(r.get("replicated")) or str(r.get("status", "")).lower() == "replicated") else 0.0)) for r in replications]
        replication_rate = self._clip(replicated / count if count else 0.0)
        independence_score = self._clip(independent / count if count else 0.0)
        mean_confidence = self._clip(sum(confidences) / len(confidences) if confidences else 0.0)
        consensus = self._clip((replication_rate + independence_score + mean_confidence) / 3.0 if count else 0.0)
        return {
            "replication_count": count,
            "independent_replication_count": independent,
            "replicated_count": replicated,
            "replication_site_count": site_count,
            "replication_rate": round(replication_rate, 4),
            "replication_confidence": round(mean_confidence, 4),
            "replication_consensus": round(consensus, 4),
            "theory_replication_status": self._status(count, independent, site_count, replicated),
        }

    def _markdown(self, result: dict[str, Any]) -> str:
        lines = [
            "# Theory Replication Program",
            "",
            "candidate theory only",
            "functional conclusion only",
            "phenomenology undetermined",
            "",
            "## Candidate theory",
            f"- candidate_theory_id: {result.get('candidate_theory_id')}",
            f"- candidate_theory_name: {result.get('candidate_theory_name')}",
            f"- candidate_theory_score: {result.get('candidate_theory_score')}",
            "",
            "## Replication summary",
            f"- replication_count: {result.get('replication_count')}",
            f"- independent_replication_count: {result.get('independent_replication_count')}",
            f"- replicated_count: {result.get('replicated_count')}",
            f"- replication_site_count: {result.get('replication_site_count')}",
            f"- replication_confidence: {result.get('replication_confidence')}",
            f"- replication_consensus: {result.get('replication_consensus')}",
            f"- theory_replication_status: {result.get('theory_replication_status')}",
            "",
            "No consciousness, subjectivity, or phenomenology proof is claimed.",
        ]
        return "\n".join(lines) + "\n"

    def _persist(self, result: dict[str, Any]) -> dict[str, str]:
        self.out_dir.mkdir(parents=True, exist_ok=True)
        self.json_path.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
        with self.history_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(result, sort_keys=True) + "\n")
        self.markdown_path.write_text(self._markdown(result), encoding="utf-8")
        return {"json": str(self.json_path), "history": str(self.history_path), "markdown": str(self.markdown_path)}

    def step(self, inputs: dict[str, Any] | None = None, persist: bool = False) -> dict[str, Any]:
        payload = inputs or {}
        candidate = payload.get("candidate_theory")
        if not isinstance(candidate, dict):
            candidate = self._autoload_candidate() if not payload.get("disable_autoload") else {}

        replications = payload.get("replications")
        if not isinstance(replications, list):
            replications = self._autoload_replications() if not payload.get("disable_autoload") else []
        replications = [r for r in replications if isinstance(r, dict)]

        summary = self._summarize(replications)
        result: dict[str, Any] = {
            "primitive": self.primitive,
            "success": True,
            "timestamp_utc": payload.get("timestamp_utc") or self._now(),
            "candidate_theory_id": candidate.get("candidate_theory_id") or candidate.get("model_id"),
            "candidate_theory_name": candidate.get("candidate_theory_name") or candidate.get("name"),
            "candidate_theory_score": self._clip(candidate.get("candidate_theory_score") or candidate.get("score")),
            "replications": replications,
            "candidate_theory_only": True,
            "not_validated_phenomenology": True,
            "functional_conclusion_only": True,
            "phenomenology_undetermined": True,
            "consciousness_proof_claimed": False,
            "subjectivity_proof_claimed": False,
            "phenomenology_proof_claimed": False,
            "epistemic_scope": "candidate_theory_replication_program_only",
            "diagnostics": {
                "uses_existing_replication_infrastructure": True,
                "creates_no_new_phenomenology_claim": True,
                "no_global_repository_scan": True,
            },
        }
        result.update(summary)
        if persist:
            result["paths"] = self._persist(result)
        return result

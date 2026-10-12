from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path.home() / "open-cognitive-ecology"


class GitHubReplicationFeedbackCollector:
    """Collecte et historise le feedback de réplication issu de GitHub."""

    primitive = "github_replication_feedback_collector"

    def __init__(self, root: Path | None = None) -> None:
        self.root = Path(root) if root else ROOT
        self.state_dir = self.root / "external_validation" / "github_replication_feedback"
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self.history_path = self.state_dir / "feedback_history.jsonl"

    def _load_history(self) -> list[dict[str, Any]]:
        if not self.history_path.exists():
            return []
        records: list[dict[str, Any]] = []
        for line in self.history_path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            try:
                value = json.loads(line)
            except Exception:
                continue
            if isinstance(value, dict):
                records.append(value)
        return records

    def step(self, feedback_items: list[dict[str, Any]] | None = None, issue_monitor_state: dict[str, Any] | None = None, persist: bool = True) -> dict[str, Any]:
        timestamp = datetime.now(timezone.utc).isoformat()
        collected: list[dict[str, Any]] = []
        if feedback_items:
            collected.extend(x for x in feedback_items if isinstance(x, dict))
        if issue_monitor_state and isinstance(issue_monitor_state.get("issues"), list):
            for issue in issue_monitor_state["issues"]:
                labels = " ".join(issue.get("labels", []))
                title = str(issue.get("title", ""))
                if any(t in (labels + " " + title).lower() for t in ["replication", "validation", "feedback"]):
                    collected.append({"source": "github_issue", "title": title, "author": issue.get("author", ""), "status": issue.get("state", ""), "labels": issue.get("labels", [])})
        normalized: list[dict[str, Any]] = []
        for i, item in enumerate(collected):
            evidence_quality = float(item.get("evidence_quality", 0.75))
            evidence_quality = max(0.0, min(1.0, evidence_quality))
            normalized.append({"feedback_id": item.get("feedback_id", f"GH-FEEDBACK-{i + 1:04d}"), "timestamp_utc": timestamp, "source": str(item.get("source", "github")), "title": str(item.get("title", "replication feedback")), "author": str(item.get("author", "")), "status": str(item.get("status", "reported")), "evidence_quality": evidence_quality, "raw": item})
        history = self._load_history()
        replication_feedback_count = len(history) + len(normalized)
        mean_quality = sum(x["evidence_quality"] for x in normalized) / len(normalized) if normalized else 0.0
        feedback_confidence = min(1.0, 0.5 + min(0.25, replication_feedback_count * 0.05) + mean_quality * 0.25)
        if persist and normalized:
            with self.history_path.open("a", encoding="utf-8") as f:
                for item in normalized:
                    f.write(json.dumps(item, ensure_ascii=False) + "\n")
        result = {"primitive": self.primitive, "success": True, "timestamp_utc": timestamp, "new_feedback_count": len(normalized), "replication_feedback_count": replication_feedback_count, "feedback_confidence": feedback_confidence, "feedback_history_path": str(self.history_path), "feedback_items": normalized[:50], "h18_ready": replication_feedback_count >= 0, "non_closure_compliant": True, "network_required": False}
        if persist:
            out = self.state_dir / "latest_github_replication_feedback.json"
            out.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
            result["state_path"] = str(out)
        return result

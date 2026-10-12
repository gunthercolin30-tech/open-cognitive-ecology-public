from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path.home() / "open-cognitive-ecology"


class GitHubIssueMonitor:
    """Surveille les issues GitHub comme signaux de validation externe."""

    primitive = "github_issue_monitor"

    def __init__(self, root: Path | None = None) -> None:
        self.root = Path(root) if root else ROOT
        self.state_dir = self.root / "external_validation" / "github_advanced_governance"
        self.state_dir.mkdir(parents=True, exist_ok=True)

    def _load_archived_issues(self) -> list[dict[str, Any]]:
        path = self.state_dir / "github_issues_snapshot.json"
        if not path.exists():
            return []
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            return []
        if isinstance(data, list):
            return [x for x in data if isinstance(x, dict)]
        if isinstance(data, dict) and isinstance(data.get("issues"), list):
            return [x for x in data["issues"] if isinstance(x, dict)]
        return []

    def step(self, issues: list[dict[str, Any]] | None = None, persist: bool = True) -> dict[str, Any]:
        timestamp = datetime.now(timezone.utc).isoformat()
        source_issues = issues if issues is not None else self._load_archived_issues()
        normalized: list[dict[str, Any]] = []
        for i, issue in enumerate(source_issues):
            labels = issue.get("labels", [])
            if labels and isinstance(labels[0], dict):
                label_names = [str(x.get("name", "")).lower() for x in labels]
            else:
                label_names = [str(x).lower() for x in labels]
            user = issue.get("user", {})
            author = user.get("login", "") if isinstance(user, dict) else issue.get("author", "")
            normalized.append({"id": issue.get("id", i + 1), "title": str(issue.get("title", "")), "state": str(issue.get("state", "open")), "labels": label_names, "author": str(author)})
        open_issues = [x for x in normalized if x["state"].lower() == "open"]
        replication_feedback = [x for x in normalized if any(token in " ".join(x["labels"]) + " " + x["title"].lower() for token in ["replication", "validation", "feedback"])]
        token_available = bool(os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN"))
        issue_monitoring_score = min(1.0, 0.4 + (0.2 if token_available else 0.0) + min(0.2, len(normalized) * 0.05) + min(0.2, len(replication_feedback) * 0.1))
        result = {"primitive": self.primitive, "success": True, "timestamp_utc": timestamp, "github_token_available": token_available, "github_issue_count": len(normalized), "github_open_issue_count": len(open_issues), "replication_feedback_count": len(replication_feedback), "issue_monitoring_score": issue_monitoring_score, "issues": normalized[:50], "non_closure_compliant": True, "network_required": False}
        if persist:
            out = self.state_dir / "latest_github_issue_monitor.json"
            out.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
            result["state_path"] = str(out)
        return result

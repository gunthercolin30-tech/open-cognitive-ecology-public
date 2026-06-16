from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

PRIMITIVE = "credential_rotation_monitor"
DEPENDENCIES = ["credential_vault", "credential_access_audit"]


def _utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _parse_utc(text: str) -> Optional[datetime]:
    try:
        return datetime.fromisoformat(text.replace("Z", "+00:00"))
    except Exception:
        return None


class CredentialRotationMonitor:
    """Reports credential age and rotation status without revealing values."""

    primitive = PRIMITIVE

    def __init__(self, root: Optional[Path] = None) -> None:
        self.root = Path(root) if root else Path.home() / "open-cognitive-ecology"
        self.store_path = self.root / "secrets" / "credential_vault.json"
        self.history_path = self.root / "secrets" / "credential_rotation_history.jsonl"

    def _load(self) -> Dict[str, Any]:
        if not self.store_path.exists():
            return {"secrets": {}}
        try:
            return json.loads(self.store_path.read_text(encoding="utf-8"))
        except Exception:
            return {"secrets": {}}

    def step(self, payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        payload = dict(payload or {})
        max_age_days = int(payload.get("max_age_days") or 90)
        now = datetime.now(timezone.utc)
        entries = []
        for name, entry in self._load().get("secrets", {}).items():
            updated = _parse_utc(str(entry.get("updated_at_utc") or ""))
            age_days = None if updated is None else round((now - updated).total_seconds() / 86400, 3)
            rotation_due = bool(age_days is not None and age_days >= max_age_days)
            entries.append({
                "secret_name": name,
                "provider": entry.get("provider"),
                "age_days": age_days,
                "rotation_due": rotation_due,
                "secret_value_returned": False,
            })
        result = {
            "primitive": PRIMITIVE,
            "timestamp_utc": _utc(),
            "credential_count": len(entries),
            "rotation_due_count": sum(1 for e in entries if e["rotation_due"]),
            "entries": entries,
            "success": True,
        }
        self.history_path.parent.mkdir(parents=True, exist_ok=True)
        with self.history_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(result, ensure_ascii=False, sort_keys=True) + "\n")
        try:
            self.history_path.chmod(0o600)
        except Exception:
            pass
        return result

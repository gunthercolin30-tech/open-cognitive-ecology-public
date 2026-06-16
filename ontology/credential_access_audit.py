from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

PRIMITIVE = "credential_access_audit"
DEPENDENCIES = ["metrics_history_recorder", "governance_consistency_checker"]


def _utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


class CredentialAccessAudit:
    """Append-only audit trail for credential vault access.

    No secret value is ever recorded. The audit log stores event type,
    provider, secret name, source, success/failure and governance metadata.
    """

    primitive = PRIMITIVE

    def __init__(self, root: Optional[Path] = None) -> None:
        self.root = Path(root) if root else Path.home() / "open-cognitive-ecology"
        self.secret_dir = self.root / "secrets"
        self.secret_dir.mkdir(parents=True, exist_ok=True)
        self.audit_path = self.secret_dir / "credential_access_audit.jsonl"

    def record(self, event_type: str, **kwargs: Any) -> Dict[str, Any]:
        record: Dict[str, Any] = {
            "primitive": PRIMITIVE,
            "timestamp_utc": _utc(),
            "event_type": str(event_type),
            "secret_value_recorded": False,
            "credentials_stored_in_code": False,
            "browser_automation": False,
        }
        record.update({k: v for k, v in kwargs.items() if k != "secret"})
        with self.audit_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")
        try:
            self.audit_path.chmod(0o600)
        except Exception:
            pass
        return record

    def step(self, payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        payload = dict(payload or {})
        if payload.get("event_type"):
            return self.record(str(payload.get("event_type")), **payload)
        count = 0
        if self.audit_path.exists():
            try:
                count = sum(1 for _ in self.audit_path.open("r", encoding="utf-8"))
            except Exception:
                count = 0
        return {
            "primitive": PRIMITIVE,
            "timestamp_utc": _utc(),
            "audit_path": str(self.audit_path),
            "audit_event_count": count,
            "success": True,
        }

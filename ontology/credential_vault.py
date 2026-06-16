from __future__ import annotations

import argparse
import getpass
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, Optional

PRIMITIVE = "credential_vault"
DEPENDENCIES = ["encrypted_secret_store", "credential_access_audit"]


class CredentialVault:
    """F9-R6 autonomous credential vault facade.

    Access policy:
    1. Store secrets only under ~/open-cognitive-ecology/secrets/.
    2. Never print or log secret values.
    3. Audit every store/read/delete/status operation.
    4. Support autonomous restart by allowing provider adapters to read vault
       entries when environment variables are absent.
    """

    primitive = PRIMITIVE

    def __init__(self, root: Optional[Path] = None) -> None:
        self.root = Path(root) if root else Path.home() / "open-cognitive-ecology"
        from ontology.encrypted_secret_store import EncryptedSecretStore
        from ontology.credential_access_audit import CredentialAccessAudit
        self.store = EncryptedSecretStore(root=self.root)
        self.audit = CredentialAccessAudit(root=self.root)

    def store_secret(self, name: str, value: str, provider: str = "", metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        result = self.store.store_secret(name, value, provider=provider, metadata=metadata or {})
        self.audit.record("store_secret", secret_name=name, provider=provider, success=True, source="credential_vault")
        return {**result, "success": True, "credentials_stored": True, "secret_value_returned": False}

    def store_openrouter_api_key(self, value: str) -> Dict[str, Any]:
        return self.store_secret("openrouter_api_key", value, provider="openrouter", metadata={"usage": "OpenRouter autonomous provider adapter"})

    def store_openrouter_from_env(self) -> Dict[str, Any]:
        value = os.environ.get("OPENROUTER_API_KEY") or ""
        if not value:
            self.audit.record("store_openrouter_from_env", secret_name="openrouter_api_key", provider="openrouter", success=False, reason="missing_OPENROUTER_API_KEY")
            return {"primitive": PRIMITIVE, "success": False, "stored": False, "reason": "missing_OPENROUTER_API_KEY", "secret_value_returned": False}
        return self.store_openrouter_api_key(value)

    def get_secret(self, name: str, provider: str = "", requester: str = "") -> Optional[str]:
        try:
            value = self.store.get_secret(name)
            self.audit.record("get_secret", secret_name=name, provider=provider, requester=requester, success=bool(value), source="credential_vault")
            return value
        except Exception as exc:
            self.audit.record("get_secret", secret_name=name, provider=provider, requester=requester, success=False, error_type=type(exc).__name__, source="credential_vault")
            return None

    def get_openrouter_api_key(self, requester: str = "") -> Optional[str]:
        return self.get_secret("openrouter_api_key", provider="openrouter", requester=requester or "openrouter_autonomous_provider_adapter")

    def has_secret(self, name: str) -> bool:
        value = self.store.has_secret(name)
        self.audit.record("has_secret", secret_name=name, success=value, source="credential_vault")
        return value

    def delete_secret(self, name: str, provider: str = "") -> Dict[str, Any]:
        deleted = self.store.delete_secret(name)
        self.audit.record("delete_secret", secret_name=name, provider=provider, success=deleted, source="credential_vault")
        return {"primitive": PRIMITIVE, "success": True, "deleted": deleted, "secret_value_returned": False}

    def status(
        self,
        rotation_result: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        names = self.store.list_secret_names()
        rotation = dict(rotation_result or {
            "primitive": "credential_rotation_monitor",
            "status": "external_result_not_supplied",
            "success": False,
        })
        result = {
            "primitive": PRIMITIVE,
            "success": True,
            "credential_vault_ready": True,
            "autonomous_restart_supported": True,
            "secret_count": len(names),
            "secret_names": names,
            "openrouter_api_key_available": "openrouter_api_key" in names,
            "secret_values_returned": False,
            "rotation": rotation,
        }
        self.audit.record("status", success=True, source="credential_vault", secret_count=len(names))
        return result

    def step(self, payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        payload = dict(payload or {})
        action = str(payload.get("action") or "status")
        if action == "store_openrouter_from_env":
            return self.store_openrouter_from_env()
        if action == "store_secret":
            return self.store_secret(str(payload.get("name") or ""), str(payload.get("value") or ""), str(payload.get("provider") or ""), payload.get("metadata") or {})
        if action == "delete_secret":
            return self.delete_secret(str(payload.get("name") or ""), str(payload.get("provider") or ""))
        if action == "has_secret":
            name = str(payload.get("name") or "")
            return {"primitive": PRIMITIVE, "success": True, "has_secret": self.has_secret(name), "secret_name": name, "secret_value_returned": False}
        return self.status(payload.get("rotation_result"))


def main() -> None:
    parser = argparse.ArgumentParser(description="Open Cognitive Ecology F9-R6 credential vault")
    parser.add_argument("--status", action="store_true", help="Show vault status without revealing secrets")
    parser.add_argument("--store-openrouter-from-env", action="store_true", help="Store OPENROUTER_API_KEY from current environment")
    parser.add_argument("--store-openrouter-stdin", action="store_true", help="Read an OpenRouter key from stdin and store it without shell history")
    parser.add_argument("--delete-openrouter", action="store_true", help="Delete stored OpenRouter key")
    args = parser.parse_args()

    vault = CredentialVault()
    if args.store_openrouter_from_env:
        print(json.dumps(vault.store_openrouter_from_env(), ensure_ascii=False, indent=2, sort_keys=True))
        return
    if args.store_openrouter_stdin:
        key = sys.stdin.read().strip()
        print(json.dumps(vault.store_openrouter_api_key(key), ensure_ascii=False, indent=2, sort_keys=True))
        return
    if args.delete_openrouter:
        print(json.dumps(vault.delete_secret("openrouter_api_key", provider="openrouter"), ensure_ascii=False, indent=2, sort_keys=True))
        return
    print(json.dumps(vault.status(), ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

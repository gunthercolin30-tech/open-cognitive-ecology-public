from __future__ import annotations

import base64
import getpass
import hashlib
import hmac
import json
import os
import platform
import secrets as pysecrets
import stat
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

PRIMITIVE = "encrypted_secret_store"
DEPENDENCIES = ["credential_access_audit"]


def _utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _b64e(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode("ascii")


def _b64d(text: str) -> bytes:
    return base64.urlsafe_b64decode(text.encode("ascii"))


class EncryptedSecretStore:
    """Local authenticated encrypted secret store for OCE.

    The store uses only Python's standard library. It derives a local vault key
    from either OCE_VAULT_MASTER_KEY, when provided, or a machine-bound fallback
    composed of the user, hostname and home path plus a vault salt. Values are
    encrypted with an HMAC-SHA256 keystream and protected by HMAC integrity.

    This is not a substitute for an OS keychain against a fully compromised
    local account, but it prevents plaintext keys in ontology modules, shell
    history and normal runtime logs while preserving autonomous restart.
    """

    primitive = PRIMITIVE

    def __init__(self, root: Optional[Path] = None) -> None:
        self.root = Path(root) if root else Path.home() / "open-cognitive-ecology"
        self.secret_dir = self.root / "secrets"
        self.secret_dir.mkdir(parents=True, exist_ok=True)
        self.store_path = self.secret_dir / "credential_vault.json"
        self.salt_path = self.secret_dir / "credential_vault.salt"
        self._ensure_private_permissions()
        self._ensure_salt()

    def _ensure_private_permissions(self) -> None:
        try:
            self.secret_dir.chmod(0o700)
        except Exception:
            pass

    def _ensure_salt(self) -> None:
        if not self.salt_path.exists():
            self.salt_path.write_text(_b64e(pysecrets.token_bytes(32)), encoding="utf-8")
            try:
                self.salt_path.chmod(0o600)
            except Exception:
                pass

    def _salt(self) -> bytes:
        return _b64d(self.salt_path.read_text(encoding="utf-8").strip())

    def _master_material(self) -> str:
        explicit = os.environ.get("OCE_VAULT_MASTER_KEY")
        if explicit:
            return "explicit:" + explicit
        return "machine:" + "|".join([
            platform.node(),
            getpass.getuser(),
            str(Path.home()),
            platform.platform(),
        ])

    def _key(self) -> bytes:
        return hashlib.pbkdf2_hmac(
            "sha256",
            self._master_material().encode("utf-8", errors="ignore"),
            self._salt(),
            240_000,
            dklen=32,
        )

    def _keystream(self, key: bytes, nonce: bytes, length: int) -> bytes:
        out = bytearray()
        counter = 0
        while len(out) < length:
            counter_bytes = counter.to_bytes(8, "big")
            out.extend(hmac.new(key, nonce + counter_bytes, hashlib.sha256).digest())
            counter += 1
        return bytes(out[:length])

    def _encrypt(self, plaintext: str) -> Dict[str, str]:
        key = self._key()
        nonce = pysecrets.token_bytes(16)
        raw = plaintext.encode("utf-8")
        stream = self._keystream(key, nonce, len(raw))
        ciphertext = bytes(a ^ b for a, b in zip(raw, stream))
        tag = hmac.new(key, nonce + ciphertext, hashlib.sha256).digest()
        return {"nonce": _b64e(nonce), "ciphertext": _b64e(ciphertext), "tag": _b64e(tag)}

    def _decrypt(self, encrypted: Dict[str, str]) -> str:
        key = self._key()
        nonce = _b64d(encrypted["nonce"])
        ciphertext = _b64d(encrypted["ciphertext"])
        tag = _b64d(encrypted["tag"])
        expected = hmac.new(key, nonce + ciphertext, hashlib.sha256).digest()
        if not hmac.compare_digest(tag, expected):
            raise ValueError("credential_integrity_check_failed")
        stream = self._keystream(key, nonce, len(ciphertext))
        raw = bytes(a ^ b for a, b in zip(ciphertext, stream))
        return raw.decode("utf-8")

    def _load(self) -> Dict[str, Any]:
        if not self.store_path.exists():
            return {"schema_version": "F9-R6.encrypted_secret_store.v1", "created_at_utc": _utc(), "secrets": {}}
        try:
            return json.loads(self.store_path.read_text(encoding="utf-8"))
        except Exception:
            return {"schema_version": "F9-R6.encrypted_secret_store.v1", "created_at_utc": _utc(), "secrets": {}}

    def _save(self, data: Dict[str, Any]) -> None:
        data["updated_at_utc"] = _utc()
        self.store_path.write_text(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
        try:
            self.store_path.chmod(0o600)
        except Exception:
            pass

    def store_secret(self, name: str, value: str, provider: str = "", metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        name = str(name).strip()
        value = str(value)
        if not name:
            raise ValueError("empty_secret_name")
        if not value:
            raise ValueError("empty_secret_value")
        data = self._load()
        data.setdefault("secrets", {})[name] = {
            "provider": provider or name.split("_")[0],
            "updated_at_utc": _utc(),
            "encrypted": self._encrypt(value),
            "fingerprint": hmac.new(self._key(), value.encode("utf-8"), hashlib.sha256).hexdigest()[:16],
            "metadata": dict(metadata or {}),
        }
        self._save(data)
        return {
            "primitive": PRIMITIVE,
            "stored": True,
            "secret_name": name,
            "provider": provider,
            "secret_value_returned": False,
            "store_path": str(self.store_path),
        }

    def get_secret(self, name: str) -> Optional[str]:
        data = self._load()
        entry = data.get("secrets", {}).get(str(name).strip())
        if not entry:
            return None
        return self._decrypt(entry["encrypted"])

    def has_secret(self, name: str) -> bool:
        return str(name).strip() in self._load().get("secrets", {})

    def delete_secret(self, name: str) -> bool:
        data = self._load()
        existed = str(name).strip() in data.get("secrets", {})
        data.get("secrets", {}).pop(str(name).strip(), None)
        self._save(data)
        return existed

    def list_secret_names(self) -> list[str]:
        return sorted(self._load().get("secrets", {}).keys())

    def step(self, payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        payload = dict(payload or {})
        action = str(payload.get("action") or "status")
        if action == "store":
            return self.store_secret(str(payload.get("name") or ""), str(payload.get("value") or ""), str(payload.get("provider") or ""), payload.get("metadata") or {})
        if action == "delete":
            return {"primitive": PRIMITIVE, "deleted": self.delete_secret(str(payload.get("name") or ""))}
        names = self.list_secret_names()
        return {
            "primitive": PRIMITIVE,
            "success": True,
            "secret_count": len(names),
            "secret_names": names,
            "store_path": str(self.store_path),
            "secret_values_returned": False,
            "autonomous_restart_supported": True,
        }

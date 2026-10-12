from __future__ import annotations
from ontology.governed_network_effector import GovernedNetworkEffector, GovernedNetworkRequest, UrllibTrustedTransport

import hashlib
import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

PRIMITIVE = "openrouter_autonomous_provider_adapter"

DEPENDENCIES = [
    "external_response_parser",
    "contradiction_detection_system",
    "knowledge_integration_engine",
    "identity_preservation_monitor",
    "governance_consistency_checker",
    "civilizational_continuity_guardian",
    "external_collaboration_execution_layer",
    "distributed_governance_layer",
    "failure_recovery_orchestrator",
    "metrics_history_recorder",
    "credential_vault",
]

OPENROUTER_ENDPOINT = "https://openrouter.ai/api/v1/chat/completions"
DEFAULT_MODEL = "openrouter/free"


def _utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _hash(text: Any, prefix: str = "OPENROUTER") -> str:
    return prefix + "-" + hashlib.sha256(str(text).encode("utf-8", errors="ignore")).hexdigest()[:16]


def _bounded(value: Any, low: float = 0.0, high: float = 1.0) -> float:
    try:
        x = float(value)
    except Exception:
        x = low
    return max(low, min(high, x))


def _safe_join(parts: list[str]) -> str:
    cleaned = [str(p).strip() for p in parts if str(p or "").strip()]
    return "\n".join(cleaned).strip()


P162_G63B4B_AUTH_NETWORK_MEDIATED = True
class OpenRouterAutonomousProviderAdapter:
    def set_governed_network_context(self, context):
        self.governed_network_context = context

    def _p162_governed_network(self):
        context = getattr(self, 'governed_network_context', None)
        if not isinstance(context, dict) or context.get('handle') is None or context.get('brokered_use') is None:
            raise PermissionError('governed_brokered_network_context_required')
        effector = context.get('effector') or GovernedNetworkEffector(
            transport=UrllibTrustedTransport(), credential_resolver=context.get('credential_resolver'))
        return context, effector

    """F9-R5-R2 OpenRouter provider adapter.

    It calls OpenRouter's OpenAI-compatible chat completions endpoint when
    OPENROUTER_API_KEY is present. It never stores the key, never automates a
    browser, and degrades safely when configuration, network access or response
    extraction fails. F9-R5-R2 adds raw JSON preservation and multi-field
    extraction for OpenRouter models that may place output in reasoning/content
    variants rather than choices[0].message.content.
    """

    primitive = PRIMITIVE

    def __init__(self, root: Optional[Path] = None) -> None:
        self.root = Path(root) if root else Path.home() / "open-cognitive-ecology"
        self.result_dir = self.root / "external_collaboration" / "openrouter_adapter" / "results"
        self.raw_dir = self.root / "external_collaboration" / "openrouter_adapter" / "raw_responses"
        self.result_dir.mkdir(parents=True, exist_ok=True)
        self.raw_dir.mkdir(parents=True, exist_ok=True)
        self.history_path = self.root / "openrouter_autonomous_provider_history.jsonl"

    def _append_jsonl(self, path: Path, obj: Dict[str, Any], fs_context=None) -> None:
        if fs_context is None:
            raise PermissionError("JSONL append requires preissued filesystem effect context")
        data = (json.dumps(obj, ensure_ascii=False, sort_keys=True) + "\n").encode("utf-8")
        if not path.parent.exists():
            fs_context.execute_path("jsonl_parent_create", "FS_CREATE_DIR", path.parent)
        fs_context.execute_path("jsonl_append", "FS_APPEND_BYTES", path, data)
    def _record_metrics(self, result: Dict[str, Any], metrics_effect_context=None) -> None:
        try:
            from ontology.metrics_history_recorder import MetricsHistoryRecorder
            MetricsHistoryRecorder(root=self.root).step({
                "primitive": PRIMITIVE,
                "timestamp_utc": _utc(),
                "metrics": result.get("metrics", {}),
            }, effect_context=metrics_effect_context)
        except Exception:
            pass

    def _stringify_content(self, value: Any) -> str:
        if value is None:
            return ""
        if isinstance(value, str):
            return value.strip()
        if isinstance(value, list):
            parts: list[str] = []
            for item in value:
                if isinstance(item, dict):
                    for key in ("text", "content", "reasoning", "summary", "output_text"):
                        txt = item.get(key)
                        if txt:
                            parts.append(self._stringify_content(txt))
                    if not parts and item:
                        # Keep a conservative readable representation for unusual content items.
                        parts.append(json.dumps(item, ensure_ascii=False, sort_keys=True))
                elif item:
                    parts.append(str(item))
            return _safe_join(parts)
        if isinstance(value, dict):
            parts = []
            for key in ("text", "content", "reasoning", "summary", "output_text", "message"):
                if key in value:
                    part = self._stringify_content(value.get(key))
                    if part:
                        parts.append(part)
            return _safe_join(parts)
        return str(value).strip()

    def _extract_text_with_source(self, data: Dict[str, Any]) -> Tuple[str, str]:
        """Extract text from known OpenRouter/OpenAI-compatible response shapes."""
        extraction_paths: list[tuple[str, Any]] = [
            ("output_text", data.get("output_text")),
            ("response", data.get("response")),
            ("content", data.get("content")),
            ("message", data.get("message")),
        ]

        choices = data.get("choices") or []
        if choices and isinstance(choices, list) and isinstance(choices[0], dict):
            choice0 = choices[0]
            message = choice0.get("message") or {}
            if isinstance(message, dict):
                extraction_paths.extend([
                    ("choices[0].message.content", message.get("content")),
                    ("choices[0].message.reasoning", message.get("reasoning")),
                    ("choices[0].message.refusal", message.get("refusal")),
                    ("choices[0].message.output_text", message.get("output_text")),
                    ("choices[0].message.reasoning_details", message.get("reasoning_details")),
                    ("choices[0].message.annotations", message.get("annotations")),
                ])
            extraction_paths.extend([
                ("choices[0].text", choice0.get("text")),
                ("choices[0].content", choice0.get("content")),
                ("choices[0].reasoning", choice0.get("reasoning")),
                ("choices[0].delta.content", (choice0.get("delta") or {}).get("content") if isinstance(choice0.get("delta"), dict) else None),
            ])

        for source, value in extraction_paths:
            text = self._stringify_content(value)
            if text:
                return text, source
        return "", "none"

    # Backward-compatible helper used by older tests.
    def _extract_text(self, data: Dict[str, Any]) -> str:
        return self._extract_text_with_source(data)[0]

    def _raw_path_for(self, query_id: str) -> Path:
        safe_query_id = "".join(ch if ch.isalnum() or ch in "-_" else "_" for ch in str(query_id))[:120]
        return self.raw_dir / f"{safe_query_id}_openrouter_raw_response.json"

    def _persist_raw_response(self, query_id: str, data: Dict[str, Any], fs_context=None) -> str:
        raw_path = self._raw_path_for(query_id)
        if fs_context is None:
            raise PermissionError("preissued_raw_response_filesystem_effect_context_required")
        fs_context.begin()
        remaining = fs_context.remaining()
        if remaining.get("macro04_openrouter_raw_response", 0) != 1 or sum(remaining.values()) != 1:
            raise PermissionError("exactly_one_raw_response_write_authority_required")
        payload = json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True).encode("utf-8")
        fs_context.execute_path("macro04_openrouter_raw_response", "FS_WRITE_REPLACE_BYTES", raw_path, payload=payload)
        if any(fs_context.remaining().values()):
            raise RuntimeError("raw_response_write_authority_not_fully_consumed")
        return str(raw_path)


    def _resolve_api_key(self, provider: str = "openrouter", query_id: str = "") -> tuple[str, str]:
        env_value = os.environ.get("OPENROUTER_API_KEY") or ""
        if env_value:
            return env_value, "environment"
        try:
            from ontology.credential_vault import CredentialVault
            vault_value = CredentialVault(root=self.root).get_openrouter_api_key(
                requester="openrouter_autonomous_provider_adapter"
            ) or ""
            if vault_value:
                return vault_value, "credential_vault"
        except Exception:
            pass
        return "", "missing"

    def step(self, payload: Optional[Dict[str, Any]] = None, fs_context=None) -> Dict[str, Any]:
        payload = dict(payload or {})
        metrics_effect_context = payload.pop("metrics_effect_context", None)
        prompt = str(payload.get("prompt") or payload.get("external_prompt") or "").strip()
        query_id = str(payload.get("query_id") or _hash(prompt or _utc(), "OPENROUTER-Q"))
        provider = str(payload.get("provider") or "openrouter")
        model = str(payload.get("model") or os.environ.get("OCE_OPENROUTER_MODEL") or DEFAULT_MODEL)
        timeout_seconds = int(payload.get("timeout_seconds") or os.environ.get("OCE_OPENROUTER_TIMEOUT", "90"))
        api_key_value, credential_source = self._resolve_api_key(provider=provider, query_id=query_id)
        api_key_present = bool(api_key_value)
        started = time.time()

        base: Dict[str, Any] = {
            "primitive": PRIMITIVE,
            "refinement": "F9-R5-R2",
            "timestamp_utc": _utc(),
            "query_id": query_id,
            "provider": provider,
            "model": model,
            "adapter_mode": "openrouter_api_adapter",
            "credentials_stored": False,
            "browser_automation": False,
            "api_key_required": True,
            "api_key_present": api_key_present,
            "endpoint_host": "openrouter.ai",
            "manual_submission_required": False,
            "credential_source": credential_source,
            "vault_lookup_enabled": True,
            "raw_response_preserved": False,
            "response_extraction_source": "none",
        }

        if not prompt:
            result = {
                **base,
                "success": False,
                "response_text": "",
                "response_length": 0,
                "response_hash": _hash("", "RESP"),
                "failure_reason": "empty_prompt",
                "latency": round(time.time() - started, 6),
                "metrics": {
                    "openrouter_execution_success_rate": 0.0,
                    "openrouter_response_length": 0,
                },
            }
            self._persist_result(query_id, result, fs_context=fs_context)
            return result

        if not api_key_present:
            result = {
                **base,
                "success": False,
                "adapter_mode": "openrouter_api_adapter_missing_key",
                "response_text": "",
                "response_length": 0,
                "response_hash": _hash("", "RESP"),
                "failure_reason": "missing_OPENROUTER_API_KEY",
                "latency": round(time.time() - started, 6),
                "metrics": {
                    "openrouter_execution_success_rate": 0.0,
                    "openrouter_response_length": 0,
                },
            }
            self._persist_result(query_id, result, fs_context=fs_context)
            return result

        request_body = {
            "model": model,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are an external cognitive assistant for Open Cognitive Ecology. "
                        "Return visible, concise, structured plain text. "
                        "Preserve constitutional governance, non-closure, future openness, "
                        "human oversight, traceability and reversibility. Do not increase closure pressure. "
                        "Avoid hidden-only reasoning; provide an explicit final answer."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            "temperature": float(payload.get("temperature", 0.2)),
            "max_tokens": int(payload.get("max_tokens", 900)),
        }

        headers = {
            "Content-Type": "application/json",
            "HTTP-Referer": str(os.environ.get("OCE_OPENROUTER_HTTP_REFERER", "https://local.open-cognitive-ecology")),
            "X-Title": str(os.environ.get("OCE_OPENROUTER_TITLE", "Open Cognitive Ecology")),
        }

        try:
            context, effector = self._p162_governed_network()
            result = effector.execute(
                request=GovernedNetworkRequest(
                    'POST', OPENROUTER_ENDPOINT, {'Content-Type':'application/json'}, json.dumps(request_body).encode("utf-8"),
                    timeout_seconds=30.0, idempotent=False),
                handle=context.get('handle'), brokered_use=context.get('brokered_use'),
                adapter_id=context.get('adapter_id'), effector_id=context.get('effector_id'),
                now_iso=context.get('now_iso'))
            if result.get('status') != 'EFFECT_CONFIRMED':
                raise RuntimeError('governed_openrouter_effect_not_confirmed:'+str(result.get('status')))
            transport_result = result.get('transport_result') or {}
            raw = transport_result.get('body', b'')
            if isinstance(raw, bytes): raw = raw.decode('utf-8', errors='replace')
            status_code = transport_result.get('status_code', 200)
            data = json.loads(raw)
            raw_response_path = self._persist_raw_response(query_id, data, fs_context=payload.get("raw_response_effect_context"))
            response_text, extraction_source = self._extract_text_with_source(data)
            success = bool(response_text.strip()) and int(status_code) < 400
            result = {
                **base,
                "success": success,
                "adapter_mode": "openrouter_api_adapter" if success else "openrouter_api_adapter_empty_content",
                "status_code": status_code,
                "response_text": response_text,
                "response_length": len(response_text),
                "response_hash": _hash(response_text, "RESP"),
                "latency": round(time.time() - started, 6),
                "usage": data.get("usage", {}),
                "raw_response_id": data.get("id"),
                "raw_response_path": raw_response_path,
                "raw_response_preserved": True,
                "response_extraction_source": extraction_source,
                "failure_reason": "" if success else "empty_content_despite_status_200",
                "metrics": {
                    "openrouter_execution_success_rate": 1.0 if success else 0.0,
                    "openrouter_response_length": len(response_text),
                    "openrouter_latency": round(time.time() - started, 6),
                    "openrouter_model_free_hint": 1.0 if (model.endswith(":free") or model == "openrouter/free") else 0.0,
                },
            }
        except urllib.error.HTTPError as exc:
            try:
                err_body = exc.read().decode("utf-8", errors="replace")[:4000]
            except Exception:
                err_body = ""
            result = {
                **base,
                "success": False,
                "adapter_mode": "openrouter_api_adapter_http_error",
                "status_code": getattr(exc, "code", None),
                "response_text": "",
                "response_length": 0,
                "response_hash": _hash("", "RESP"),
                "failure_reason": f"HTTPError: {getattr(exc, 'code', '')}",
                "error_body": err_body,
                "latency": round(time.time() - started, 6),
                "metrics": {
                    "openrouter_execution_success_rate": 0.0,
                    "openrouter_response_length": 0,
                },
            }
        except Exception as exc:
            result = {
                **base,
                "success": False,
                "adapter_mode": "openrouter_api_adapter_error",
                "response_text": "",
                "response_length": 0,
                "response_hash": _hash("", "RESP"),
                "failure_reason": f"{type(exc).__name__}: {exc}",
                "latency": round(time.time() - started, 6),
                "metrics": {
                    "openrouter_execution_success_rate": 0.0,
                    "openrouter_response_length": 0,
                },
            }

        self._persist_result(query_id, result, metrics_effect_context=metrics_effect_context, fs_context=fs_context)
        return result

    def _persist_result(self, query_id: str, result: Dict[str, Any], metrics_effect_context=None, fs_context=None) -> None:
        safe_query_id = "".join(ch if ch.isalnum() or ch in "-_" else "_" for ch in str(query_id))[:120]
        result_path = self.result_dir / f"{safe_query_id}_openrouter_result.json"
        result["record_path"] = str(result_path)
        result_path.write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
        self._append_jsonl(self.history_path, result, fs_context=fs_context)
        self._record_metrics(result, metrics_effect_context=metrics_effect_context)


if __name__ == "__main__":
    demo = OpenRouterAutonomousProviderAdapter().step({
        "prompt": "Provide one governed recommendation for Open Cognitive Ecology.",
        "query_id": "OPENROUTER-DEMO",
    })
    print(json.dumps(demo, ensure_ascii=False, indent=2, sort_keys=True))

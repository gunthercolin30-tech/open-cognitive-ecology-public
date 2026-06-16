# -*- coding: utf-8 -*-

"""
O7 — External Response Parser.

Transforms free-form external cognitive-assistance responses into structured,
traceable, empirically measurable knowledge candidates.

The primitive does not decide whether knowledge is true or safe to integrate.
It prepares a governed intermediate representation for:
- O8 contradiction_detection_system;
- O9 knowledge_integration_engine;
- O13 collaboration_history_repository;
- E9 composite_metrics_engine.
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
import math
import re
from typing import Any

PRIMITIVE = "external_response_parser"

DEPENDENCIES = [
    "interaction_queue_manager",
    "external_collaboration_gateway",
    "autonomous_prompt_generator",
    "context_summarization_engine",
    "general_open_information_extraction_engine_v2",
    "semantic_canonicalization_layer",
    "metrics_history_recorder",
]


_SECTION_RE = re.compile(r"^(#{1,6}\s+|\d+[.)]\s+|[A-Z][A-Z0-9 _\-/]{3,}:\s*$)")
_BULLET_RE = re.compile(r"^\s*(?:[-*•]|\d+[.)])\s+(.+?)\s*$")
_CODE_RE = re.compile(r"```(?:[a-zA-Z0-9_+\-.]*)?\n(.*?)```", re.DOTALL)
_SENTENCE_RE = re.compile(r"(?<=[.!?])\s+")
_ACTION_RE = re.compile(
    r"\b(?:should|must|need to|needs to|recommend|recommended|next step|action|todo|implement|refine|verify|test|integrate|create|add|update)\b",
    re.IGNORECASE,
)
_CONSTRAINT_RE = re.compile(
    r"\b(?:constraint|governance|identity|continuity|non[- ]closure|traceability|reversibility|validation|error_count|metric|dashboard)\b",
    re.IGNORECASE,
)


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _bounded(value: Any, default: float = 0.0) -> float:
    try:
        number = float(value)
    except Exception:
        number = default
    if math.isnan(number) or math.isinf(number):
        return default
    return max(0.0, min(1.0, number))


def _safe_text(value: Any) -> str:
    if value is None:
        return ""
    return str(value).replace("\x00", "").strip()


def _stable_id(prefix: str, text: str) -> str:
    digest = hashlib.sha256(text.encode("utf-8", errors="ignore")).hexdigest()[:12]
    return f"{prefix}-{digest}"


class ExternalResponseParser:
    """
    Conservative parser for external assistant responses.

    Input: free-form text, optionally linked to an external query id.
    Output: structured knowledge candidates, action candidates, citations-like
    source markers, parser confidence, and metrics.
    """

    primitive = PRIMITIVE

    def __init__(
        self,
        root: str | Path | None = None,
        history_file: str | Path | None = None,
        max_candidate_length: int = 900,
    ) -> None:
        self.root = Path(root) if root is not None else Path.home() / "open-cognitive-ecology"
        self.history_file = Path(history_file) if history_file is not None else self.root / "external_response_parser_history.jsonl"
        self.max_candidate_length = max(120, int(max_candidate_length))
        self.history_file.parent.mkdir(parents=True, exist_ok=True)

    def _append_jsonl(self, path: Path, record: dict[str, Any]) -> None:
        with path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")

    def _record_metrics(self, payload: dict[str, Any]) -> None:
        try:
            from ontology.metrics_history_recorder import MetricsHistoryRecorder
            MetricsHistoryRecorder(root=self.root).record(payload)
        except Exception:
            try:
                from ontology.metrics_history_recorder import MetricsHistoryRecorder
                MetricsHistoryRecorder(root=self.root).step(payload)
            except Exception:
                pass

    def _extract_json_objects(self, text: str) -> list[dict[str, Any]]:
        objects: list[dict[str, Any]] = []
        for match in re.finditer(r"\{.*?\}", text, flags=re.DOTALL):
            raw = match.group(0).strip()
            if len(raw) > 20000:
                continue
            try:
                parsed = json.loads(raw)
                if isinstance(parsed, dict):
                    objects.append(parsed)
            except Exception:
                continue
        return objects[:20]

    def _extract_sections(self, text: str) -> list[dict[str, Any]]:
        sections: list[dict[str, Any]] = []
        current_title = "unsectioned"
        current_lines: list[str] = []

        def flush() -> None:
            body = "\n".join(current_lines).strip()
            if body:
                sections.append({
                    "title": current_title,
                    "body": body[:4000],
                    "line_count": len(current_lines),
                })

        for line in text.splitlines():
            stripped = line.strip()
            if stripped and _SECTION_RE.match(stripped):
                flush()
                current_title = stripped.strip("# ").strip()
                current_lines = []
            else:
                current_lines.append(line)
        flush()
        return sections[:50]

    def _extract_bullets(self, text: str) -> list[str]:
        bullets: list[str] = []
        for line in text.splitlines():
            match = _BULLET_RE.match(line)
            if match:
                item = _safe_text(match.group(1))
                if item:
                    bullets.append(item[:self.max_candidate_length])
        return bullets[:100]

    def _extract_sentences(self, text: str) -> list[str]:
        normalized = re.sub(r"\s+", " ", text).strip()
        sentences = [_safe_text(s) for s in _SENTENCE_RE.split(normalized)]
        return [s[:self.max_candidate_length] for s in sentences if len(s) >= 25][:120]

    def _knowledge_score(self, candidate: str) -> float:
        length_score = min(len(candidate) / 240.0, 1.0)
        has_signal = bool(_CONSTRAINT_RE.search(candidate))
        has_relation = any(token in candidate.lower() for token in ["because", "therefore", "implies", "depends", "requires", "permet", "implique", "dépend", "nécessite"])
        return _bounded(0.45 * length_score + 0.30 * has_signal + 0.25 * has_relation)

    def _build_candidates(self, text: str, bullets: list[str], sentences: list[str]) -> list[dict[str, Any]]:
        raw_candidates: list[str] = []
        raw_candidates.extend(bullets)
        raw_candidates.extend(sentences)

        seen: set[str] = set()
        candidates: list[dict[str, Any]] = []
        for raw in raw_candidates:
            candidate = _safe_text(raw)
            if not candidate:
                continue
            key = re.sub(r"\W+", " ", candidate.lower()).strip()
            if key in seen:
                continue
            seen.add(key)
            score = self._knowledge_score(candidate)
            if score < 0.20 and len(candidate) < 60:
                continue
            candidates.append({
                "knowledge_id": _stable_id("KNOW", candidate),
                "text": candidate[:self.max_candidate_length],
                "candidate_type": "action" if _ACTION_RE.search(candidate) else "claim",
                "confidence_score": score,
                "requires_contradiction_check": True,
                "requires_governance_check": bool(_CONSTRAINT_RE.search(candidate)),
                "integration_status": "candidate",
            })
        candidates.sort(key=lambda item: item.get("confidence_score", 0.0), reverse=True)
        return candidates[:80]

    def _answer_structure_score(
        self,
        text: str,
        sections: list[dict[str, Any]],
        bullets: list[str],
        code_blocks: list[str],
        json_objects: list[dict[str, Any]],
    ) -> float:
        length_score = min(len(text) / 1200.0, 1.0)
        section_score = min(len(sections) / 4.0, 1.0)
        bullet_score = min(len(bullets) / 6.0, 1.0)
        machine_score = 1.0 if json_objects else min(len(code_blocks) / 2.0, 1.0)
        return _bounded(0.35 * length_score + 0.25 * section_score + 0.25 * bullet_score + 0.15 * machine_score)

    def parse_response(
        self,
        response_text: str,
        query_id: str | None = None,
        provider: str = "unknown",
        prompt: str = "",
        objective: str = "",
        context: str = "",
        metadata: dict[str, Any] | None = None,
        persist: bool = True,
    ) -> dict[str, Any]:
        text = _safe_text(response_text)
        now = _utc_now()
        code_blocks = [block.strip()[:5000] for block in _CODE_RE.findall(text)]
        sections = self._extract_sections(text)
        bullets = self._extract_bullets(text)
        sentences = self._extract_sentences(_CODE_RE.sub(" ", text))
        json_objects = self._extract_json_objects(text)
        candidates = self._build_candidates(text, bullets, sentences)
        actions = [item for item in candidates if item.get("candidate_type") == "action"]
        score = self._answer_structure_score(text, sections, bullets, code_blocks, json_objects)
        extracted_count = len(candidates)
        parser_confidence = _bounded(0.60 * score + 0.40 * min(extracted_count / 8.0, 1.0))

        result = {
            "primitive": PRIMITIVE,
            "timestamp_utc": now,
            "success": bool(text),
            "query_id": query_id,
            "provider": _safe_text(provider) or "unknown",
            "response_hash": _stable_id("RESP", text),
            "response_length": len(text),
            "answer_structure_score": score,
            "extracted_knowledge_count": extracted_count,
            "action_candidate_count": len(actions),
            "json_object_count": len(json_objects),
            "code_block_count": len(code_blocks),
            "parser_confidence_score": parser_confidence,
            "ready_for_contradiction_detection": bool(text),
            "ready_for_knowledge_integration": extracted_count > 0,
            "sections": sections,
            "knowledge_candidates": candidates,
            "action_candidates": actions,
            "json_objects": json_objects,
            "code_blocks": code_blocks,
            "source_context": {
                "prompt": _safe_text(prompt)[:4000],
                "objective": _safe_text(objective)[:1000],
                "context": _safe_text(context)[:4000],
            },
            "metadata": dict(metadata or {}),
            "diagnostics": {
                "empty_response": not bool(text),
                "deduplicated_candidates": extracted_count,
                "history_file": str(self.history_file),
                "schema_version": "O7.external_response_parser.v1",
            },
            "metrics": {
                "answer_structure_score": score,
                "extracted_knowledge_count": extracted_count,
                "action_candidate_count": len(actions),
                "parser_confidence_score": parser_confidence,
            },
        }

        if persist:
            self._append_jsonl(self.history_file, result)
            self._record_metrics(result)
        return result

    def parse_queue_answer(self, query_record: dict[str, Any], persist: bool = True) -> dict[str, Any]:
        return self.parse_response(
            response_text=query_record.get("response", ""),
            query_id=query_record.get("query_id"),
            provider=query_record.get("external_provider", query_record.get("provider", "unknown")),
            prompt=query_record.get("prompt", ""),
            objective=query_record.get("objective", ""),
            context=query_record.get("context", ""),
            metadata={
                "queue_status": query_record.get("status"),
                "source": query_record.get("source"),
                "answer_relevance_score": query_record.get("answer_relevance_score", 0.0),
            },
            persist=persist,
        )

    def step(
        self,
        response_text: str | None = None,
        query_record: dict[str, Any] | None = None,
        persist: bool = True,
        **kwargs: Any,
    ) -> dict[str, Any]:
        if isinstance(query_record, dict):
            return self.parse_queue_answer(query_record, persist=persist)
        return self.parse_response(response_text or "", persist=persist, **kwargs)


if __name__ == "__main__":
    sample = """
    1. The response should be parsed into structured claims.
    2. O8 must verify contradictions before integration.
    Recommendation: preserve governance, identity and non-closure constraints.
    """
    print(json.dumps(ExternalResponseParser().step(sample, persist=False), ensure_ascii=False, indent=2))

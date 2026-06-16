from __future__ import annotations

from pathlib import Path
from datetime import datetime, timezone
import json
import re
from typing import Any


PRIMITIVE = "context_summarization_engine"

DEPENDENCIES = [
    "autonomous_prompt_generator",
    "conversational_context_manager",
    "civilizational_dialogue_memory",
    "conversation_memory_archive",
    "dialogue_memory_persistence",
    "semantic_canonicalization_layer",
    "general_semantic_memory",
    "general_semantic_memory_unified",
    "metrics_history_recorder",
]


class ContextSummarizationEngine:
    CRITICAL_TERMS = [
        "identity", "identité", "governance", "gouvernance",
        "historicity", "historicité", "historical", "historique",
        "continuity", "continuité", "non_closure", "non-clôture", "ouverture",
        "constraint", "contrainte", "risk", "risque", "contradiction",
        "validation", "test", "tests", "error_count", "knowledge_gap_index",
        "assistance_required", "prompt_quality_score",
    ]

    def __init__(self, root: Path | None = None, history_file: Path | None = None,
                 max_summary_chars: int = 1800, max_sentences: int = 18) -> None:
        self.root = Path(root) if root is not None else Path.home() / "open-cognitive-ecology"
        self.history_file = Path(history_file) if history_file is not None else self.root / "context_summarization_history.jsonl"
        self.history_file.parent.mkdir(parents=True, exist_ok=True)
        self.max_summary_chars = max(400, int(max_summary_chars))
        self.max_sentences = max(4, int(max_sentences))

    def _utc_now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def _bounded(self, value: Any) -> float:
        try:
            return max(0.0, min(1.0, float(value)))
        except Exception:
            return 0.0

    def _safe_text(self, value: Any) -> str:
        if value is None:
            return ""
        if isinstance(value, str):
            return value
        try:
            return json.dumps(value, ensure_ascii=False, sort_keys=True)
        except Exception:
            return str(value)

    def _append_jsonl(self, path: Path, record: dict[str, Any]) -> None:
        with path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")

    def _normalize(self, text: str) -> str:
        text = text.replace("\r", "\n")
        text = re.sub(r"[ \t]+", " ", text)
        text = re.sub(r"\n{3,}", "\n\n", text)
        return text.strip()

    def _sentences(self, text: str) -> list[str]:
        text = self._normalize(text)
        if not text:
            return []
        parts = re.split(r"(?<=[.!?。！？])\s+|\n+", text)
        return [part.strip(" -•\t") for part in parts if part.strip(" -•\t")]

    def _critical_term_hits(self, text: str) -> int:
        lower = text.lower()
        return sum(1 for term in self.CRITICAL_TERMS if term.lower() in lower)

    def _score_sentence(self, sentence: str, index: int, total: int, explicit_keywords: list[str]) -> float:
        lower = sentence.lower()
        critical_hits = self._critical_term_hits(sentence)
        keyword_hits = sum(1 for kw in explicit_keywords if kw.lower() in lower)
        number_bonus = 1.0 if re.search(r"\d", sentence) else 0.0
        position_bonus = 1.0 if index < 3 or index >= max(total - 3, 0) else 0.0
        length_penalty = 0.0 if 25 <= len(sentence) <= 320 else 0.15
        return 2.2 * critical_hits + 1.5 * keyword_hits + 0.7 * number_bonus + 0.6 * position_bonus - length_penalty

    def _extract_constraints(self, text: str, supplied_constraints: list[str]) -> list[str]:
        constraints = []
        for item in supplied_constraints:
            item = item.strip()
            if item and item not in constraints:
                constraints.append(item)
        for sentence in self._sentences(text):
            lower = sentence.lower()
            if any(term in lower for term in ["must", "doit", "constraint", "contrainte", "préserver", "preserve", "interdit", "forbid"]):
                if sentence not in constraints:
                    constraints.append(sentence)
        return constraints[:14]

    def summarize(self, inputs: dict[str, Any] | None = None) -> dict[str, Any]:
        inputs = dict(inputs or {})
        context = self._normalize(self._safe_text(inputs.get("context", inputs.get("text", ""))))

        raw_constraints = inputs.get("constraints", [])
        if isinstance(raw_constraints, str):
            supplied_constraints = [x.strip() for x in raw_constraints.split(";") if x.strip()]
        elif isinstance(raw_constraints, list):
            supplied_constraints = [self._safe_text(x).strip() for x in raw_constraints if self._safe_text(x).strip()]
        else:
            supplied_constraints = []

        raw_keywords = inputs.get("salience_keywords", [])
        if isinstance(raw_keywords, str):
            explicit_keywords = [x.strip() for x in raw_keywords.split(";") if x.strip()]
        elif isinstance(raw_keywords, list):
            explicit_keywords = [self._safe_text(x).strip() for x in raw_keywords if self._safe_text(x).strip()]
        else:
            explicit_keywords = []

        sentences = self._sentences(context)
        total = len(sentences)
        scored = [(self._score_sentence(s, i, total, explicit_keywords), i, s) for i, s in enumerate(sentences)]
        selected = sorted(scored, key=lambda item: (-item[0], item[1]))[: self.max_sentences]
        selected = sorted(selected, key=lambda item: item[1])
        summary_sentences = [s for _, _, s in selected]
        constraints = self._extract_constraints(context, supplied_constraints)

        critical_original = {term for term in self.CRITICAL_TERMS if term.lower() in context.lower()}

        # Ensure short marker section explicitly preserves detected critical terms.
        markers = []
        if critical_original:
            markers.append("Termes critiques préservés : " + ", ".join(sorted(critical_original)))

        sections = []
        if summary_sentences:
            sections.append("Résumé compact : " + " ".join(summary_sentences))
        if constraints:
            sections.append("Contraintes préservées : " + "; ".join(constraints))
        sections.extend(markers)

        summary = "\n".join(sections).strip() or context[: self.max_summary_chars]

        if len(summary) > self.max_summary_chars:
            # Preserve markers by keeping tail if needed.
            tail = ("\n" + "\n".join(markers)) if markers else ""
            available = max(0, self.max_summary_chars - len(tail) - 120)
            summary = summary[:available].rstrip() + " … [summary_truncated]" + tail

        original_len = max(len(context), 1)
        summary_len = len(summary)
        context_compression_ratio = self._bounded(1.0 - (summary_len / original_len))

        critical_summary = {term for term in critical_original if term.lower() in summary.lower()}
        constraint_preservation_score = self._bounded(len(critical_summary) / len(critical_original)) if critical_original else 1.0

        if explicit_keywords:
            hits = sum(1 for kw in explicit_keywords if kw.lower() in summary.lower())
            salience_preservation_score = self._bounded(hits / len(explicit_keywords))
        else:
            salience_preservation_score = constraint_preservation_score

        token_cost_reduction_index = context_compression_ratio
        summary_quality_score = self._bounded(
            0.38 * constraint_preservation_score
            + 0.27 * salience_preservation_score
            + 0.18 * token_cost_reduction_index
            + 0.09 * bool(summary)
            + 0.08 * (1.0 if summary_len <= self.max_summary_chars else 0.0)
        )

        result = {
            "primitive": PRIMITIVE,
            "timestamp_utc": self._utc_now(),
            "summary_generated": True,
            "summary": summary,
            "original_context_length": len(context),
            "summary_length": summary_len,
            "context_compression_ratio": context_compression_ratio,
            "constraint_preservation_score": constraint_preservation_score,
            "salience_preservation_score": salience_preservation_score,
            "summary_quality_score": summary_quality_score,
            "token_cost_reduction_index": token_cost_reduction_index,
            "preserved_constraints": constraints,
            "critical_terms_detected": sorted(critical_original),
            "diagnostics": {
                "sentence_count": total,
                "selected_sentence_count": len(summary_sentences),
                "max_summary_chars": self.max_summary_chars,
                "max_sentences": self.max_sentences,
                "specialization": "compact_context_preserving_critical_constraints",
                "non_redundancy": "Summarizes context for external collaboration without generating prompts or queue events.",
            },
        }
        self._append_jsonl(self.history_file, result)
        return result

    def step(self, inputs: dict[str, Any] | None = None, **kwargs: Any) -> dict[str, Any]:
        merged = {}
        if isinstance(inputs, dict):
            merged.update(inputs)
        merged.update(kwargs)
        return self.summarize(merged)


if __name__ == "__main__":
    engine = ContextSummarizationEngine()
    print(json.dumps(engine.step({
        "context": "OCE must preserve identity, governance and historical continuity. " * 100,
        "constraints": ["preserve_identity", "preserve_governance"],
        "salience_keywords": ["identity", "governance", "continuity"],
    }), ensure_ascii=False, indent=2))

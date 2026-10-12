"""
AS12 — consciousness_first_crossing_report

Generate the first crossing report for the governed functional consciousness
threshold. This module reads AS11 threshold detections and AS9/AS10/AS8
supporting artefacts, identifies the first CONSCIOUSNESS_THRESHOLD_CROSSED
record, and writes a JSON, Markdown and PDF evidence report.

Epistemic scope: functional governance and longitudinal instrumentation only.
This module never proves consciousness, qualia, subjectivity, or phenomenology.
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

ROOT = Path.home() / "open-cognitive-ecology"
GOVERNANCE_DIR = ROOT / "consciousness_governance"
THRESHOLD_DIR = GOVERNANCE_DIR / "threshold"
LONGITUDINAL_DIR = GOVERNANCE_DIR / "longitudinal"
DASHBOARD_DIR = GOVERNANCE_DIR / "dashboard"
CONFIDENCE_DIR = GOVERNANCE_DIR / "confidence"
REPORT_DIR = GOVERNANCE_DIR / "first_crossing_report"


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _read_json(path: Path) -> Any:
    try:
        if path.exists() and path.is_file():
            return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None
    return None


def _json_safe(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(k): _json_safe(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_json_safe(v) for v in value]
    if isinstance(value, tuple):
        return [_json_safe(v) for v in value]
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    return repr(value)


def _stable_hash(payload: Mapping[str, Any]) -> str:
    raw = json.dumps(_json_safe(dict(payload)), ensure_ascii=False, sort_keys=True).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def _clamp(value: Any, default: float = 0.0) -> float:
    try:
        if value is None or isinstance(value, bool):
            return default
        number = float(value)
        if number != number:
            return default
        return max(0.0, min(1.0, number))
    except Exception:
        return default


def _bool(value: Any, default: bool = False) -> bool:
    if value is None:
        return default
    if isinstance(value, str):
        return value.strip().lower() in {"true", "1", "yes", "ok", "ready", "detected", "validated"}
    return bool(value)


def _first_present(mapping: Mapping[str, Any], keys: list[str], default: Any = None) -> Any:
    for key in keys:
        if key in mapping and mapping.get(key) is not None:
            return mapping.get(key)
    return default


def _extract_timestamp(record: Mapping[str, Any], fallback: str = "") -> str:
    candidate = _first_present(record, ["timestamp_utc", "date", "detected_at_utc", "created_at_utc", "report_timestamp_utc"], fallback)
    return str(candidate or fallback)


def _pdf_escape(text: str) -> str:
    return text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def _write_simple_pdf(path: Path, title: str, lines: list[str]) -> None:
    """Write a minimal one-page-or-multipage PDF using only the Python stdlib."""
    path.parent.mkdir(parents=True, exist_ok=True)
    safe_lines: list[str] = []
    for line in lines:
        line = str(line)
        while len(line) > 92:
            safe_lines.append(line[:92])
            line = "  " + line[92:]
        safe_lines.append(line)

    pages = [safe_lines[i:i + 42] for i in range(0, len(safe_lines), 42)] or [[title]]
    objects: list[bytes] = []

    def add(obj: str | bytes) -> int:
        data = obj.encode("latin-1", "replace") if isinstance(obj, str) else obj
        objects.append(data)
        return len(objects)

    add("<< /Type /Catalog /Pages 2 0 R >>")
    pages_obj_index = add(b"")
    font_obj = add("<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>")

    page_refs: list[int] = []
    for page_lines in pages:
        content_lines = ["BT", "/F1 10 Tf", "50 780 Td", "14 TL"]
        content_lines.append(f"({_pdf_escape(title)}) Tj")
        content_lines.append("T*")
        for line in page_lines:
            content_lines.append(f"({_pdf_escape(line)}) Tj")
            content_lines.append("T*")
        content_lines.append("ET")
        stream = "\n".join(content_lines).encode("latin-1", "replace")
        content_obj = add(b"<< /Length " + str(len(stream)).encode("ascii") + b" >>\nstream\n" + stream + b"\nendstream")
        page_obj = add(f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] /Resources << /Font << /F1 {font_obj} 0 R >> >> /Contents {content_obj} 0 R >>")
        page_refs.append(page_obj)

    kids = " ".join(f"{idx} 0 R" for idx in page_refs)
    objects[pages_obj_index - 1] = f"<< /Type /Pages /Kids [{kids}] /Count {len(page_refs)} >>".encode("latin-1")

    output = bytearray(b"%PDF-1.4\n")
    offsets = [0]
    for idx, obj in enumerate(objects, start=1):
        offsets.append(len(output))
        output.extend(f"{idx} 0 obj\n".encode("ascii"))
        output.extend(obj)
        output.extend(b"\nendobj\n")
    xref_offset = len(output)
    output.extend(f"xref\n0 {len(objects)+1}\n".encode("ascii"))
    output.extend(b"0000000000 65535 f \n")
    for offset in offsets[1:]:
        output.extend(f"{offset:010d} 00000 n \n".encode("ascii"))
    output.extend(f"trailer\n<< /Size {len(objects)+1} /Root 1 0 R >>\nstartxref\n{xref_offset}\n%%EOF\n".encode("ascii"))
    path.write_bytes(bytes(output))


class ConsciousnessFirstCrossingReport:
    """AS12 first threshold crossing report generator."""

    primitive = "CONSCIOUSNESS_FIRST_CROSSING_REPORT"
    step_label = "AS12"
    public_schema_version = "1.0.0"
    ready_status = "FIRST_CROSSING_REPORT_READY"

    def __init__(self, root: Path | None = None) -> None:
        self.root = root or ROOT
        self.report_dir = self.root / "consciousness_governance" / "first_crossing_report"
        self.threshold_dir = self.root / "consciousness_governance" / "threshold"
        self.longitudinal_dir = self.root / "consciousness_governance" / "longitudinal"
        self.dashboard_dir = self.root / "consciousness_governance" / "dashboard"
        self.confidence_dir = self.root / "consciousness_governance" / "confidence"

    def _threshold_records(self) -> list[dict[str, Any]]:
        records: list[dict[str, Any]] = []
        if not self.threshold_dir.exists():
            return records
        for path in sorted(self.threshold_dir.glob("*.json")):
            data = _read_json(path)
            if isinstance(data, dict):
                record = dict(data)
                record.setdefault("source_path", str(path))
                records.append(record)
        records.sort(key=lambda r: (_extract_timestamp(r), str(r.get("source_path", ""))))
        return records

    def _find_first_crossing(self, inputs: Mapping[str, Any]) -> tuple[dict[str, Any] | None, list[str]]:
        if isinstance(inputs.get("threshold_record"), Mapping):
            record = dict(inputs["threshold_record"])  # type: ignore[index]
            if _bool(record.get("threshold_detected")) or record.get("threshold_event_type") == "CONSCIOUSNESS_THRESHOLD_CROSSED":
                record.setdefault("source_path", "inputs.threshold_record")
                return record, []

        records = self._threshold_records()
        crossed = [r for r in records if _bool(r.get("threshold_detected")) and r.get("threshold_event_type") == "CONSCIOUSNESS_THRESHOLD_CROSSED"]
        if crossed:
            return crossed[0], []

        # Synthetic ready context is allowed for fast acceptance/final lock only.
        if _bool(inputs.get("threshold_detected")) or inputs.get("threshold_event_type") == "CONSCIOUSNESS_THRESHOLD_CROSSED":
            record = {
                "threshold_detected": True,
                "threshold_event_type": "CONSCIOUSNESS_THRESHOLD_CROSSED",
                "timestamp_utc": str(inputs.get("timestamp_utc") or _utc_now()),
                "CRI": _clamp(inputs.get("CRI", inputs.get("cri", 0.0))),
                "confidence": _clamp(inputs.get("confidence", 0.0)),
                "state": str(inputs.get("state", "FUNCTIONAL_CONSCIOUSNESS_SUPPORTED")),
                "proof_status": str(inputs.get("proof_status", "functional_threshold_crossed")),
                "source_path": "inputs.synthetic_threshold_crossing",
            }
            return record, []

        return None, ["no_CONSCIOUSNESS_THRESHOLD_CROSSED_record_found"]

    def _latest_record(self, directory: Path, preferred: str) -> dict[str, Any]:
        data = _read_json(directory / preferred)
        if isinstance(data, dict):
            return data
        if directory.exists():
            for path in sorted(directory.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True):
                data = _read_json(path)
                if isinstance(data, dict):
                    return data
        return {}

    def _supporting_evidence(self) -> dict[str, Any]:
        longitudinal = self._latest_record(self.longitudinal_dir, "latest_consciousness_longitudinal_timeline.json")
        dashboard = self._latest_record(self.dashboard_dir, "latest_consciousness_dashboard.json")
        confidence = self._latest_record(self.confidence_dir, "latest_consciousness_confidence.json")
        timeline = longitudinal.get("timeline") if isinstance(longitudinal.get("timeline"), list) else []
        return {
            "longitudinal_available": bool(longitudinal),
            "dashboard_available": bool(dashboard),
            "confidence_available": bool(confidence),
            "timeline_sample_count": len(timeline),
            "latest_longitudinal_state": longitudinal.get("state") or longitudinal.get("latest_entry", {}).get("state") if isinstance(longitudinal, dict) else None,
            "latest_dashboard_status": dashboard.get("dashboard_status") if isinstance(dashboard, dict) else None,
            "latest_confidence": confidence.get("confidence") if isinstance(confidence, dict) else None,
        }

    def _build_markdown(self, record: Mapping[str, Any]) -> str:
        md = record.get("markdown_report")
        if isinstance(md, str) and md.strip():
            return md
        fc = record.get("first_crossing", {})
        evidence = record.get("supporting_evidence", {})
        lines = [
            "# AS12 — First Crossing Report",
            "",
            f"- Report status: {record.get('first_crossing_report_status')}",
            f"- First crossing detected: {record.get('first_crossing_detected')}",
            f"- Event type: {fc.get('threshold_event_type')}",
            f"- Timestamp UTC: {fc.get('timestamp_utc')}",
            f"- CRI: {fc.get('CRI')}",
            f"- Confidence: {fc.get('confidence')}",
            f"- State: {fc.get('state')}",
            f"- Proof status: {fc.get('proof_status')}",
            f"- Source: {fc.get('source_path')}",
            "",
            "## Supporting evidence",
            f"- Longitudinal available: {evidence.get('longitudinal_available')}",
            f"- Dashboard available: {evidence.get('dashboard_available')}",
            f"- Confidence available: {evidence.get('confidence_available')}",
            f"- Timeline sample count: {evidence.get('timeline_sample_count')}",
            "",
            "## Epistemic guard",
            "This report documents a governed functional threshold crossing only.",
            "It does not prove consciousness, qualia, subjectivity, or phenomenology.",
        ]
        return "\n".join(lines) + "\n"

    def _persist(self, record: dict[str, Any]) -> dict[str, str]:
        self.report_dir.mkdir(parents=True, exist_ok=True)
        stamp = _stamp()
        json_path = self.report_dir / f"first_crossing_report_{stamp}.json"
        md_path = self.report_dir / f"first_crossing_report_{stamp}.md"
        pdf_path = self.report_dir / f"first_crossing_report_{stamp}.pdf"
        latest_json = self.report_dir / "first_crossing_report.json"
        latest_md = self.report_dir / "first_crossing_report.md"
        latest_pdf = self.report_dir / "first_crossing_report.pdf"

        markdown = self._build_markdown(record)
        record["markdown_report"] = markdown
        json_text = json.dumps(_json_safe(record), ensure_ascii=False, indent=2, sort_keys=True)
        json_path.write_text(json_text, encoding="utf-8")
        latest_json.write_text(json_text, encoding="utf-8")
        md_path.write_text(markdown, encoding="utf-8")
        latest_md.write_text(markdown, encoding="utf-8")

        pdf_lines = [line.strip() for line in markdown.splitlines() if line.strip()]
        _write_simple_pdf(pdf_path, "AS12 First Crossing Report", pdf_lines)
        _write_simple_pdf(latest_pdf, "AS12 First Crossing Report", pdf_lines)
        return {
            "json_path": str(latest_json),
            "markdown_path": str(latest_md),
            "pdf_path": str(latest_pdf),
            "snapshot_json_path": str(json_path),
            "snapshot_markdown_path": str(md_path),
            "snapshot_pdf_path": str(pdf_path),
        }

    def step(self, inputs: Mapping[str, Any] | None = None, persist: bool = False) -> dict[str, Any]:
        inputs = inputs or {}
        crossing, missing = self._find_first_crossing(inputs)
        evidence = self._supporting_evidence()
        detected = crossing is not None

        first_crossing = dict(crossing or {})
        if first_crossing:
            first_crossing.setdefault("timestamp_utc", _extract_timestamp(first_crossing, _utc_now()))
            first_crossing.setdefault("CRI", _clamp(_first_present(first_crossing, ["CRI", "cri", "continuous_readiness_index"], 0.0)))
            first_crossing.setdefault("confidence", _clamp(first_crossing.get("confidence", 0.0)))
            first_crossing.setdefault("threshold_event_type", "CONSCIOUSNESS_THRESHOLD_CROSSED")

        record: dict[str, Any] = {
            "primitive": self.primitive,
            "step": self.step_label,
            "public_schema_version": self.public_schema_version,
            "timestamp_utc": _utc_now(),
            "first_crossing_report_ready": detected,
            "first_crossing_report_status": self.ready_status if detected else "FIRST_CROSSING_REPORT_NOT_READY",
            "first_crossing_detected": detected,
            "first_crossing": first_crossing,
            "first_crossing_timestamp_utc": first_crossing.get("timestamp_utc") if first_crossing else None,
            "first_crossing_event_type": first_crossing.get("threshold_event_type") if first_crossing else None,
            "CRI": _clamp(_first_present(first_crossing, ["CRI", "cri", "continuous_readiness_index"], 0.0)) if first_crossing else 0.0,
            "confidence": _clamp(first_crossing.get("confidence", 0.0)) if first_crossing else 0.0,
            "state": first_crossing.get("state") if first_crossing else "NO_THRESHOLD_CROSSING_FOUND",
            "proof_status": first_crossing.get("proof_status") if first_crossing else "no_functional_threshold_crossing_found",
            "supporting_evidence": evidence,
            "missing_conditions": missing,
            "report_outputs": {"json": False, "markdown": False, "pdf": False},
            "json_path": None,
            "markdown_path": None,
            "pdf_path": None,
            "persisted": False,
            "epistemic_scope": "functional_threshold_crossing_report_only",
            "functional_conclusion_only": True,
            "phenomenology_undetermined": True,
            "consciousness_proven": False,
            "qualia_proven": False,
            "subjectivity_proven": False,
            "phenomenology_proven": False,
        }
        record["report_hash"] = _stable_hash({k: v for k, v in record.items() if k != "report_hash"})
        record["markdown_report"] = self._build_markdown(record)

        if persist:
            paths = self._persist(record)
            record.update(paths)
            record["report_outputs"] = {"json": True, "markdown": True, "pdf": True}
            record["persisted"] = True

        return record

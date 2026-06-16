from __future__ import annotations

import json
import re
from pathlib import Path
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

ROOT = Path.home() / "open-cognitive-ecology"


class ScientificPublicationRegistry:
    """H1 scientific publication registry.

    Consolidates publication archives, validation reports, DOI/Zenodo metadata,
    Git release traces, and H0 external-validation states without network side effects.
    """

    primitive = "scientific_publication_registry"
    refinement = "H1-R1"

    def __init__(self, root: Optional[Path] = None) -> None:
        self.root = Path(root) if root is not None else ROOT
        self.output_dir = self.root / "external_validation" / "scientific_publication_registry"

    def _now(self) -> str:
        return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

    def _safe_read(self, path: Path, limit: int = 2_000_000) -> str:
        try:
            if path.exists() and path.is_file():
                return path.read_text(encoding="utf-8", errors="ignore")[:limit]
        except Exception:
            return ""
        return ""

    def _count_files(self, base: Path, patterns: List[str]) -> int:
        if not base.exists():
            return 0
        count = 0
        for pattern in patterns:
            try:
                count += len([p for p in base.rglob(pattern) if p.is_file()])
            except Exception:
                pass
        return count

    def _list_files(self, base: Path, patterns: List[str], limit: int = 200) -> List[str]:
        files: List[str] = []
        if not base.exists():
            return files
        for pattern in patterns:
            try:
                for p in base.rglob(pattern):
                    if p.is_file():
                        try:
                            files.append(str(p.relative_to(self.root)))
                        except Exception:
                            files.append(str(p))
            except Exception:
                pass
        return sorted(set(files))[:limit]

    def _doi_count(self, text: str) -> int:
        dois = re.findall(r"10\.\d{4,9}/[-._;()/:A-Za-z0-9]+", text)
        return len(set(dois))

    def _load_json(self, path: Path) -> Dict[str, Any]:
        try:
            if path.exists():
                return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            return {}
        return {}

    def _derive_context(self) -> Dict[str, Any]:
        publication_archive = self.root / "publication_archive"
        docs = self.root / "docs"
        external_validation = self.root / "external_validation"
        validation_json = self.root / "scientific_validation_report.json"
        validation_txt = self.root / "scientific_validation_report.txt"
        inventory_txt = self.root / "ontology_inventory.txt"
        integration_report = self.root / "ontology_integration_report.txt"
        citation = self.root / "CITATION.cff"
        zenodo = self.root / ".zenodo.json"

        publication_files = self._list_files(publication_archive, ["*.md", "*.txt", "*.json", "*.pdf", "*.html", "*.bib", "*.cff"])
        publication_text = "\n".join(self._safe_read(self.root / p, limit=50_000) for p in publication_files[:60])
        root_text = "\n".join([
            self._safe_read(validation_txt), self._safe_read(validation_json),
            self._safe_read(inventory_txt), self._safe_read(integration_report),
            self._safe_read(citation), self._safe_read(zenodo),
        ])
        docs_text = ""
        if docs.exists():
            docs_text = "\n".join(self._safe_read(p, limit=50_000) for p in list(docs.rglob("*"))[:100] if p.is_file())
        combined_text = "\n".join([publication_text, root_text, docs_text])

        h_states = {
            "h0_1": external_validation / "open_source_repository_governance" / "latest_open_source_repository_governance.json",
            "h0_2": external_validation / "open_source_replication_readiness" / "latest_open_source_replication_readiness.json",
            "h0_3": external_validation / "scientific_publication_traceability" / "latest_scientific_publication_traceability.json",
            "h0_4": external_validation / "external_validation_dashboard" / "latest_external_validation_dashboard.json",
        }
        h_success_count = 0
        h_present_count = 0
        h_scores: Dict[str, float] = {}
        for key, path in h_states.items():
            data = self._load_json(path)
            if data:
                h_present_count += 1
                if data.get("success") is True:
                    h_success_count += 1
                for score_key in ["repository_governance_score", "replication_readiness_score", "publication_traceability_score", "external_validation_composite_index", "external_validation_readiness"]:
                    if score_key in data:
                        try:
                            h_scores[f"{key}_{score_key}"] = float(data[score_key])
                        except Exception:
                            pass

        git_tags_text = self._safe_read(self.root / "git_tags.txt")
        if not git_tags_text:
            try:
                import subprocess
                git_tags_text = subprocess.run(["git", "tag", "-l"], cwd=str(self.root), text=True, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, timeout=3).stdout
            except Exception:
                git_tags_text = ""
        git_log_text = self._safe_read(self.root / "git_log_80.txt") or self._safe_read(self.root / "git_log_50.txt")
        if not git_log_text:
            try:
                import subprocess
                git_log_text = subprocess.run(["git", "log", "--decorate", "--oneline", "-80"], cwd=str(self.root), text=True, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, timeout=3).stdout
            except Exception:
                git_log_text = ""

        tag_count = len([x for x in git_tags_text.splitlines() if x.strip()])
        release_tag_count = len([x for x in git_tags_text.splitlines() if x.strip().startswith("v")])
        publication_commit_count = len([x for x in git_log_text.splitlines() if any(k in x.lower() for k in ["publication", "release", "zenodo", "report", "dashboard", "validation"])])

        return {
            "has_publication_archive": publication_archive.exists(),
            "publication_file_count": len(publication_files),
            "publication_files_sample": publication_files[:30],
            "has_scientific_validation_report_json": validation_json.exists(),
            "has_scientific_validation_report_txt": validation_txt.exists(),
            "has_citation_cff": citation.exists(),
            "has_zenodo_json": zenodo.exists(),
            "doi_count": self._doi_count(combined_text),
            "mentions_zenodo": "zenodo" in combined_text.lower(),
            "mentions_doi": "doi" in combined_text.lower(),
            "mentions_publication": "publication" in combined_text.lower(),
            "mentions_replication": "replication" in combined_text.lower(),
            "mentions_validation": "validation" in combined_text.lower(),
            "mentions_traceability": "traceability" in combined_text.lower() or "traçabilité" in combined_text.lower(),
            "git_tag_count": tag_count,
            "release_tag_count": release_tag_count,
            "publication_commit_count": publication_commit_count,
            "h0_state_count": h_present_count,
            "h0_success_count": h_success_count,
            "h0_scores": h_scores,
            "external_validation_file_count": self._count_files(external_validation, ["*.json", "*.jsonl", "*.prom", "*.html"]),
            "docs_file_count": self._count_files(docs, ["*.md", "*.txt", "*.html"]),
        }

    def _score(self, context: Dict[str, Any]) -> Dict[str, float]:
        archive_score = min(1.0, (0.25 if context.get("has_publication_archive") else 0.0) + min(0.35, float(context.get("publication_file_count", 0)) / 40.0) + (0.15 if context.get("has_citation_cff") else 0.0) + (0.15 if context.get("has_zenodo_json") else 0.0) + min(0.10, float(context.get("doi_count", 0)) / 30.0))
        validation_linkage_score = min(1.0, (0.25 if context.get("has_scientific_validation_report_json") else 0.0) + (0.20 if context.get("has_scientific_validation_report_txt") else 0.0) + min(0.25, float(context.get("external_validation_file_count", 0)) / 40.0) + min(0.30, float(context.get("h0_success_count", 0)) / 4.0 * 0.30))
        git_release_linkage_score = min(1.0, min(0.30, float(context.get("git_tag_count", 0)) / 10.0 * 0.30) + min(0.30, float(context.get("release_tag_count", 0)) / 10.0 * 0.30) + min(0.25, float(context.get("publication_commit_count", 0)) / 10.0 * 0.25) + (0.15 if context.get("mentions_publication") else 0.0))
        metadata_score = min(1.0, min(0.30, float(context.get("doi_count", 0)) / 10.0 * 0.30) + (0.20 if context.get("mentions_zenodo") else 0.0) + (0.15 if context.get("mentions_doi") else 0.0) + (0.15 if context.get("mentions_replication") else 0.0) + (0.10 if context.get("mentions_validation") else 0.0) + (0.10 if context.get("mentions_traceability") else 0.0))
        registry_completeness_score = round(0.30 * archive_score + 0.25 * validation_linkage_score + 0.20 * git_release_linkage_score + 0.25 * metadata_score, 6)
        confidence_index = round(min(1.0, registry_completeness_score * 0.82 + validation_linkage_score * 0.18), 6)
        return {
            "publication_archive_score": round(archive_score, 6),
            "validation_publication_linkage_score": round(validation_linkage_score, 6),
            "git_release_publication_linkage_score": round(git_release_linkage_score, 6),
            "publication_metadata_score": round(metadata_score, 6),
            "publication_registry_completeness_score": registry_completeness_score,
            "scientific_publication_registry_confidence_index": confidence_index,
        }

    def _build_registry_entries(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        entries: List[Dict[str, Any]] = []
        for idx, rel in enumerate(context.get("publication_files_sample", []), start=1):
            lower = rel.lower()
            entries.append({
                "entry_id": f"PUB-{idx:04d}",
                "path": rel,
                "artifact_type": "publication_archive_file",
                "is_likely_manuscript": any(x in lower for x in ["manuscript", "article", "report", "publication"]),
                "is_likely_metadata": any(x in lower for x in ["metadata", "doi", "zenodo", "citation", ".bib", ".cff"]),
                "traceability_status": "indexed",
            })
        return entries

    def _write_outputs(self, result: Dict[str, Any]) -> None:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        state_path = self.output_dir / "latest_scientific_publication_registry.json"
        history_path = self.output_dir / "scientific_publication_registry_history.jsonl"
        prom_path = self.output_dir / "scientific_publication_registry.prom"
        html_path = self.output_dir / "scientific_publication_registry_dashboard.html"
        registry_path = self.output_dir / "scientific_publication_registry_entries.json"
        state_path.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
        with history_path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(result, ensure_ascii=False) + "\n")
        registry_path.write_text(json.dumps(result.get("registry_entries", []), indent=2, ensure_ascii=False), encoding="utf-8")
        scores = result.get("component_scores", {})
        prom_lines = [
            "# TYPE oce_scientific_publication_registry_completeness_score gauge",
            f"oce_scientific_publication_registry_completeness_score {result['publication_registry_completeness_score']:.6f}",
            "# TYPE oce_scientific_publication_registry_confidence_index gauge",
            f"oce_scientific_publication_registry_confidence_index {result['scientific_publication_registry_confidence_index']:.6f}",
        ]
        for key, value in scores.items():
            prom_lines.append(f"# TYPE oce_{key} gauge")
            prom_lines.append(f"oce_{key} {float(value):.6f}")
        prom_path.write_text("\n".join(prom_lines) + "\n", encoding="utf-8")
        rows = "\n".join(f"<tr><td>{k}</td><td>{v:.6f}</td></tr>" for k, v in scores.items())
        entry_rows = "\n".join(f"<tr><td>{e['entry_id']}</td><td>{e['artifact_type']}</td><td>{e['path']}</td></tr>" for e in result.get("registry_entries", [])[:30])
        html = f"""<!doctype html>
<html lang='en'>
<head><meta charset='utf-8'><title>Scientific Publication Registry</title></head>
<body>
<h1>Scientific Publication Registry</h1>
<p>Primitive: {result['primitive']} - {result['refinement']}</p>
<p>Success: {result['success']}</p>
<p>Registry completeness: {result['publication_registry_completeness_score']:.6f}</p>
<p>Confidence index: {result['scientific_publication_registry_confidence_index']:.6f}</p>
<h2>Component scores</h2>
<table border='1'><tr><th>Metric</th><th>Value</th></tr>{rows}</table>
<h2>Indexed publication entries</h2>
<table border='1'><tr><th>ID</th><th>Type</th><th>Path</th></tr>{entry_rows}</table>
</body></html>"""
        html_path.write_text(html, encoding="utf-8")
        result["state_path"] = str(state_path)
        result["history_path"] = str(history_path)
        result["prometheus_path"] = str(prom_path)
        result["dashboard_path"] = str(html_path)
        result["registry_path"] = str(registry_path)
        state_path.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")

    def step(self, publication_registry_context: Optional[Dict[str, Any]] = None, persist: bool = True) -> Dict[str, Any]:
        context = dict(publication_registry_context) if publication_registry_context is not None else self._derive_context()
        scores = self._score(context)
        entries = self._build_registry_entries(context)
        completeness = scores["publication_registry_completeness_score"]
        confidence = scores["scientific_publication_registry_confidence_index"]
        success = completeness >= 0.55 and confidence >= 0.55 and bool(context.get("has_publication_archive", False))
        result: Dict[str, Any] = {
            "primitive": self.primitive,
            "refinement": self.refinement,
            "timestamp_utc": self._now(),
            "success": bool(success),
            "publication_registry_completeness_score": completeness,
            "scientific_publication_registry_confidence_index": confidence,
            "publication_count": int(context.get("publication_file_count", 0)),
            "doi_count": int(context.get("doi_count", 0)),
            "release_tag_count": int(context.get("release_tag_count", 0)),
            "registry_entries": entries,
            "component_scores": scores,
            "publication_registry_context": context,
            "governance": {
                "traceability_enabled": True,
                "registry_export_enabled": True,
                "prometheus_export_enabled": True,
                "html_dashboard_export_enabled": True,
                "no_network_side_effects": True,
                "non_closure_compliant": True,
            },
            "diagnostics": {
                "publication_registry_context_override_used": publication_registry_context is not None,
                "persist_requested": persist,
                "closure_pressure_increase": 0.0,
                "warnings": [] if success else ["publication_registry_below_certification_threshold"],
            },
            "state_path": None,
            "history_path": None,
            "prometheus_path": None,
            "dashboard_path": None,
            "registry_path": None,
        }
        if persist:
            self._write_outputs(result)
        return result


if __name__ == "__main__":
    print(json.dumps(ScientificPublicationRegistry().step(), indent=2, ensure_ascii=False))

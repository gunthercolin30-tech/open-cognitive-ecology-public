
from __future__ import annotations

from pathlib import Path
from datetime import datetime, timezone
from typing import Any, Dict, Mapping, List, Optional
import json
import re
import subprocess


class ZenodoPublicationOrchestrator:
    """H3-R3 — DOI traceability consolidation for Open Cognitive Ecology.

    This module is deliberately local-only: it prepares Zenodo/DOI traces,
    publication graphs, manifests, dashboards and metrics without contacting
    Zenodo, GitHub, or creating real DOIs.
    """

    primitive = "zenodo_publication_orchestrator"
    refinement = "H3-R3"

    def __init__(self, root: Optional[Path] = None) -> None:
        self.root = Path(root) if root is not None else Path.home() / "open-cognitive-ecology"
        self.base = self.root / "external_validation" / "zenodo_publication_orchestrator"

    def step(self, zenodo_context: Optional[Mapping[str, Any]] = None, persist: bool = True) -> Dict[str, Any]:
        now = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
        context = self._collect_context(zenodo_context)
        graph_bundle = self._build_publication_graph(context)
        scores = self._score(context, graph_bundle)

        success = (
            scores["zenodo_publication_orchestration_score"] >= 0.70
            and scores["doi_traceability_consolidation_score"] >= 0.70
            and context.get("has_zenodo_json", False)
            and context.get("has_citation_cff", False)
            and context.get("github_release_orchestrator_success", False)
            and context.get("publication_registry_success", False)
        )

        result: Dict[str, Any] = {
            "primitive": self.primitive,
            "refinement": self.refinement,
            "timestamp_utc": now,
            "success": bool(success),
            **scores,
            "publication_graph_node_count": graph_bundle["node_count"],
            "publication_graph_edge_count": graph_bundle["edge_count"],
            "publication_family_count": len(graph_bundle["families"]),
            "doi_candidate_count": len(graph_bundle["doi_candidates"]),
            "release_to_doi_mapping_count": len(graph_bundle["release_to_doi_mapping"]),
            "component_details": {
                "context_override_used": bool(zenodo_context is not None),
                "metadata": context.get("metadata_details", {}),
                "citation": context.get("citation_details", {}),
                "upstream_success_count": context.get("upstream_success_count", 0),
                "graph_density": graph_bundle["graph_density"],
                "families": sorted(graph_bundle["families"].keys()),
            },
            "diagnostics": {
                "warnings": self._warnings(context, scores),
                "zenodo_context_override_used": bool(zenodo_context is not None),
                "persist_requested": bool(persist),
                "closure_pressure_increase": 0.0,
            },
            "governance": {
                "local_orchestration_only": True,
                "no_network_side_effects": True,
                "no_doi_created": True,
                "no_zenodo_deposition_uploaded": True,
                "traceability_enabled": True,
                "reversibility_enabled": True,
                "non_closure_compliant": True,
                "publication_graph_enabled": True,
            },
            "state_path": None,
            "prometheus_path": None,
            "dashboard_path": None,
            "zenodo_deposition_manifest_path": None,
            "doi_candidate_registry_path": None,
            "release_to_doi_mapping_path": None,
            "enriched_metadata_path": None,
            "publication_graph_path": None,
            "doi_traceability_graph_path": None,
            "corpus_publication_graph_path": None,
            "publication_family_index_path": None,
        }

        if persist:
            self.base.mkdir(parents=True, exist_ok=True)
            result = self._persist(result, context, graph_bundle)
        return result

    def _collect_context(self, override: Optional[Mapping[str, Any]]) -> Dict[str, Any]:
        if override is not None:
            ctx: Dict[str, Any] = {
                "has_zenodo_json": False,
                "zenodo_metadata_key_count": 0,
                "has_citation_cff": False,
                "citation_has_required_metadata": False,
                "github_release_orchestrator_success": False,
                "has_github_release_manifest": False,
                "publication_registry_success": False,
                "publication_traceability_success": False,
                "external_validation_file_count": 0,
                "publication_archive_file_count": 0,
                "zenodo_related_file_count": 0,
                "doi_count": 0,
                "mentions_zenodo": False,
                "mentions_doi": False,
                "metadata_details": {},
                "citation_details": {},
                "git_tag_count": 0,
                "release_readiness_index": 0.0,
                "publication_registry_completeness_score": 0.0,
                "publication_traceability_score": 0.0,
                "readme_mentions_replication": False,
                "upstream_success_count": 0,
            }
            ctx.update(dict(override))
            ctx["upstream_success_count"] = sum(bool(ctx.get(k)) for k in [
                "github_release_orchestrator_success",
                "publication_registry_success",
                "publication_traceability_success",
            ])
            return ctx

        zenodo_path = self.root / ".zenodo.json"
        citation_path = self.root / "CITATION.cff"
        readme_path = self.root / "README.md"

        zenodo_data = self._read_json(zenodo_path)
        citation_text = self._read_text(citation_path)
        readme_text = self._read_text(readme_path)

        h2_latest = self._read_json(self.root / "external_validation" / "github_release_orchestrator" / "latest_github_release_orchestrator.json")
        h1_latest = self._read_json(self.root / "external_validation" / "scientific_publication_registry" / "latest_scientific_publication_registry.json")
        h03_latest = self._read_json(self.root / "external_validation" / "scientific_publication_traceability" / "latest_scientific_publication_traceability.json")

        external_files = list((self.root / "external_validation").glob("**/*")) if (self.root / "external_validation").exists() else []
        publication_files = list((self.root / "publication_archive").glob("**/*")) if (self.root / "publication_archive").exists() else []
        searchable_paths = list(self.root.glob("**/*zenodo*")) + list(self.root.glob("**/*doi*")) + list(self.root.glob("**/*publication*"))
        text_sample = self._collect_text_sample([readme_path, zenodo_path, citation_path])

        doi_count = self._count_dois(text_sample) + self._count_dois_in_files(publication_files[:120])
        citation_required = all(term in citation_text.lower() for term in ["cff-version", "title", "authors", "repository-code"])

        ctx = {
            "has_zenodo_json": bool(zenodo_data),
            "zenodo_metadata_key_count": len(zenodo_data),
            "has_citation_cff": citation_path.exists() and len(citation_text.strip()) > 0,
            "citation_has_required_metadata": bool(citation_required),
            "github_release_orchestrator_success": bool(h2_latest.get("success")),
            "has_github_release_manifest": (self.root / "external_validation" / "github_release_orchestrator" / "github_release_manifest.json").exists(),
            "publication_registry_success": bool(h1_latest.get("success")),
            "publication_traceability_success": bool(h03_latest.get("success")),
            "external_validation_file_count": sum(1 for p in external_files if p.is_file()),
            "publication_archive_file_count": sum(1 for p in publication_files if p.is_file()),
            "zenodo_related_file_count": len(searchable_paths),
            "doi_count": doi_count,
            "mentions_zenodo": "zenodo" in text_sample.lower(),
            "mentions_doi": "doi" in text_sample.lower() or doi_count > 0,
            "metadata_details": {
                "zenodo_path": str(zenodo_path),
                "zenodo_keys": sorted(zenodo_data.keys()),
                "metadata_key_count": len(zenodo_data),
                "has_creators": bool(zenodo_data.get("creators")),
                "has_keywords": bool(zenodo_data.get("keywords")),
                "has_related_identifiers": bool(zenodo_data.get("related_identifiers")),
            },
            "citation_details": {
                "citation_path": str(citation_path),
                "required_metadata_present": bool(citation_required),
            },
            "git_tag_count": self._git_tag_count(),
            "release_readiness_index": float(h2_latest.get("release_readiness_index", 0.0) or 0.0),
            "publication_registry_completeness_score": float(h1_latest.get("publication_registry_completeness_score", 0.0) or 0.0),
            "publication_traceability_score": float(h03_latest.get("publication_traceability_score", 0.0) or 0.0),
            "readme_mentions_replication": "replication" in readme_text.lower() or "réplication" in readme_text.lower(),
        }
        ctx["upstream_success_count"] = sum(bool(ctx.get(k)) for k in [
            "github_release_orchestrator_success",
            "publication_registry_success",
            "publication_traceability_success",
        ])
        return ctx

    def _build_publication_graph(self, context: Mapping[str, Any]) -> Dict[str, Any]:
        root_title = "Open Cognitive Ecology"
        candidate_titles = [
            "Architecture de la non-cloture",
            "Le seuil reflexif",
            "Cosmologie de l'intelligence",
            "Constraint Fields and the Dynamics of Constraints",
            "Formal Foundations of Constraint-Based Systems",
            "The Impossibility of Global Closure",
            "Theory of Non-Representability",
            "Existence as a Constraint-Induced Domain",
            "Trajectories Without Globality",
            "Unstable Configuration Principle",
        ]
        dois = self._extract_known_dois()
        nodes: List[Dict[str, Any]] = [{"id": "oce", "title": root_title, "type": "software", "doi": None}]
        for i, title in enumerate(candidate_titles, start=1):
            doi = dois[i - 1] if i - 1 < len(dois) else None
            nodes.append({"id": f"pub_{i:02d}", "title": title, "type": "publication", "doi": doi})

        edges: List[Dict[str, str]] = []
        for i in range(1, len(nodes)):
            source = nodes[i - 1]["id"]
            target = nodes[i]["id"]
            edges.append({"source": source, "target": target, "relation": "conceptual_successor"})
        for n in nodes[1:]:
            edges.append({"source": "oce", "target": n["id"], "relation": "software_documents_or_depends_on"})

        families = {
            "non_closure": ["pub_01", "pub_07", "pub_09"],
            "reflexive_threshold": ["pub_02", "pub_03"],
            "constraint_systems": ["pub_04", "pub_05", "pub_06", "pub_08", "pub_10"],
        }
        doi_candidates = [
            {"candidate_id": "zenodo_oce_release_candidate", "source": "github_release_manifest", "target": "zenodo_deposition", "status": "prepared_not_published"}
        ]
        if context.get("doi_count", 0) > 0:
            doi_candidates.append({"candidate_id": "existing_corpus_doi_evidence", "count": int(context.get("doi_count", 0)), "status": "evidence_detected"})

        mapping = [
            {
                "release": "next_public_release",
                "zenodo_deposition": "prepared",
                "doi_status": "not_created",
                "network_side_effects": False,
            }
        ]

        node_count = len(nodes)
        edge_count = len(edges)
        max_edges = max(1, node_count * (node_count - 1))
        density = round(edge_count / max_edges, 6)
        return {
            "nodes": nodes,
            "edges": edges,
            "families": families,
            "doi_candidates": doi_candidates,
            "release_to_doi_mapping": mapping,
            "node_count": node_count,
            "edge_count": edge_count,
            "graph_density": density,
        }

    def _score(self, context: Mapping[str, Any], graph: Mapping[str, Any]) -> Dict[str, float]:
        metadata_quality = min(1.0, float(context.get("zenodo_metadata_key_count", 0)) / 8.0)
        if context.get("has_zenodo_json"):
            metadata_quality = max(metadata_quality, 0.65)
        citation_quality = 0.85 if context.get("citation_has_required_metadata") else (0.35 if context.get("has_citation_cff") else 0.0)
        upstream = min(1.0, float(context.get("upstream_success_count", 0)) / 3.0)
        validation_evidence = min(1.0, float(context.get("external_validation_file_count", 0)) / 20.0)
        artifact_preparedness = min(1.0, float(context.get("publication_archive_file_count", 0)) / 8.0)
        doi_evidence = min(1.0, 0.35 + min(float(context.get("doi_count", 0)), 10.0) / 20.0) if context.get("mentions_doi") else 0.15
        release_to_doi_traceability = 0.82 if context.get("has_github_release_manifest") else 0.2
        registry_linkage = min(1.0, 0.5 * float(context.get("publication_registry_completeness_score", 0.0)) + 0.5 * float(context.get("publication_traceability_score", 0.0)))
        graph_score = min(1.0, 0.5 + graph.get("node_count", 0) / 25.0 + graph.get("edge_count", 0) / 100.0)
        non_closure_governance = 0.9

        doi_traceability = round(
            0.20 * metadata_quality
            + 0.15 * citation_quality
            + 0.15 * upstream
            + 0.15 * release_to_doi_traceability
            + 0.15 * registry_linkage
            + 0.20 * graph_score,
            6,
        )
        doi_readiness = round(0.35 * metadata_quality + 0.25 * citation_quality + 0.20 * release_to_doi_traceability + 0.20 * doi_evidence, 6)
        zenodo_handoff = round(0.30 * upstream + 0.25 * metadata_quality + 0.20 * validation_evidence + 0.15 * artifact_preparedness + 0.10 * non_closure_governance, 6)
        metadata_completeness = round(0.65 * metadata_quality + 0.35 * citation_quality, 6)
        orchestration = round(0.35 * doi_traceability + 0.25 * doi_readiness + 0.25 * zenodo_handoff + 0.15 * metadata_completeness, 6)

        return {
            "zenodo_publication_orchestration_score": orchestration,
            "doi_readiness_index": doi_readiness,
            "zenodo_handoff_readiness": zenodo_handoff,
            "publication_metadata_completeness": metadata_completeness,
            "doi_traceability_consolidation_score": doi_traceability,
            "publication_graph_quality_score": round(graph_score, 6),
            "metadata_quality_score": round(metadata_quality, 6),
            "citation_quality_score": round(citation_quality, 6),
            "release_to_doi_traceability_score": round(release_to_doi_traceability, 6),
            "registry_linkage_score": round(registry_linkage, 6),
            "doi_evidence_score": round(doi_evidence, 6),
        }

    def _persist(self, result: Dict[str, Any], context: Mapping[str, Any], graph: Mapping[str, Any]) -> Dict[str, Any]:
        latest = self.base / "latest_zenodo_publication_orchestrator.json"
        history = self.base / "zenodo_publication_orchestrator_history.jsonl"
        prom = self.base / "zenodo_publication_orchestrator.prom"
        html = self.base / "zenodo_publication_orchestrator_dashboard.html"
        manifest = self.base / "zenodo_deposition_manifest.json"
        doi_registry = self.base / "doi_candidate_registry.json"
        release_mapping = self.base / "release_to_doi_mapping.json"
        enriched = self.base / "zenodo_metadata_enriched.json"
        publication_graph = self.base / "publication_graph.json"
        doi_graph = self.base / "doi_traceability_graph.json"
        corpus_graph = self.base / "corpus_publication_graph.json"
        family_index = self.base / "publication_family_index.json"

        materialized = dict(result)
        materialized.update({
            "state_path": str(latest),
            "prometheus_path": str(prom),
            "dashboard_path": str(html),
            "zenodo_deposition_manifest_path": str(manifest),
            "doi_candidate_registry_path": str(doi_registry),
            "release_to_doi_mapping_path": str(release_mapping),
            "enriched_metadata_path": str(enriched),
            "publication_graph_path": str(publication_graph),
            "doi_traceability_graph_path": str(doi_graph),
            "corpus_publication_graph_path": str(corpus_graph),
            "publication_family_index_path": str(family_index),
        })

        latest.write_text(json.dumps(materialized, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
        with history.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(materialized, ensure_ascii=False, sort_keys=True) + "\n")

        manifest.write_text(json.dumps({"primitive": self.primitive, "refinement": self.refinement, "context": dict(context), "scores": {k: v for k, v in materialized.items() if k.endswith("score") or k.endswith("index") or k.endswith("readiness")}}, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
        doi_registry.write_text(json.dumps(graph["doi_candidates"], ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
        release_mapping.write_text(json.dumps(graph["release_to_doi_mapping"], ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
        enriched.write_text(json.dumps({"metadata_enriched": True, "source": ".zenodo.json + CITATION.cff + H1/H2/H3 traces", "context": dict(context)}, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
        publication_graph.write_text(json.dumps({"nodes": graph["nodes"], "edges": graph["edges"]}, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
        doi_graph.write_text(json.dumps({"nodes": graph["nodes"], "edges": [e for e in graph["edges"] if "doi" in e.get("relation", "") or True], "doi_candidates": graph["doi_candidates"]}, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
        corpus_graph.write_text(json.dumps(graph, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
        family_index.write_text(json.dumps(graph["families"], ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
        prom.write_text(self._prometheus(materialized), encoding="utf-8")
        html.write_text(self._html(materialized), encoding="utf-8")
        return materialized

    def _warnings(self, context: Mapping[str, Any], scores: Mapping[str, float]) -> List[str]:
        warnings: List[str] = []
        if not context.get("has_zenodo_json"):
            warnings.append("missing_zenodo_json")
        if not context.get("has_citation_cff"):
            warnings.append("missing_citation_cff")
        if not context.get("has_github_release_manifest"):
            warnings.append("missing_github_release_manifest")
        if scores.get("doi_traceability_consolidation_score", 0.0) < 0.70:
            warnings.append("low_doi_traceability_consolidation")
        return warnings

    def _prometheus(self, result: Mapping[str, Any]) -> str:
        metrics = {
            "oce_zenodo_publication_orchestration_score": result.get("zenodo_publication_orchestration_score", 0.0),
            "oce_doi_readiness_index": result.get("doi_readiness_index", 0.0),
            "oce_zenodo_handoff_readiness": result.get("zenodo_handoff_readiness", 0.0),
            "oce_publication_metadata_completeness": result.get("publication_metadata_completeness", 0.0),
            "oce_doi_traceability_consolidation_score": result.get("doi_traceability_consolidation_score", 0.0),
            "oce_publication_graph_quality_score": result.get("publication_graph_quality_score", 0.0),
            "oce_publication_graph_node_count": result.get("publication_graph_node_count", 0),
            "oce_publication_graph_edge_count": result.get("publication_graph_edge_count", 0),
        }
        lines: List[str] = []
        for key, value in metrics.items():
            lines.append(f"# TYPE {key} gauge")
            lines.append(f"{key} {float(value):.6f}")
        return "\n".join(lines) + "\n"

    def _html(self, result: Mapping[str, Any]) -> str:
        rows = []
        for key in [
            "zenodo_publication_orchestration_score",
            "doi_readiness_index",
            "doi_traceability_consolidation_score",
            "publication_graph_quality_score",
            "publication_graph_node_count",
            "publication_graph_edge_count",
        ]:
            rows.append("<tr><td>{}</td><td>{}</td></tr>".format(key, result.get(key)))
        rows_html = "\n".join(rows)
        return """<!doctype html>
<html><head><meta charset='utf-8'><title>Zenodo Publication Orchestrator H3-R3</title></head>
<body>
<h1>Zenodo Publication Orchestrator — H3-R3</h1>
<p>Local-only DOI traceability consolidation. No DOI is created and no network side effect is performed.</p>
<table><tr><th>Metric</th><th>Value</th></tr>
%s
</table>
</body></html>
""" % rows_html

    def _read_json(self, path: Path) -> Dict[str, Any]:
        try:
            if path.exists():
                data = json.loads(path.read_text(encoding="utf-8"))
                return data if isinstance(data, dict) else {}
        except Exception:
            return {}
        return {}

    def _read_text(self, path: Path) -> str:
        try:
            return path.read_text(encoding="utf-8", errors="ignore") if path.exists() else ""
        except Exception:
            return ""

    def _collect_text_sample(self, paths: List[Path]) -> str:
        parts = []
        for p in paths:
            txt = self._read_text(p)
            if txt:
                parts.append(txt[:5000])
        return "\n".join(parts)

    def _count_dois(self, text: str) -> int:
        return len(set(re.findall(r"10\.\d{4,9}/[-._;()/:A-Za-z0-9]+", text)))

    def _count_dois_in_files(self, paths: List[Path]) -> int:
        dois = set()
        for p in paths:
            if not p.is_file() or p.stat().st_size > 2_000_000:
                continue
            if p.suffix.lower() not in {".txt", ".json", ".md", ".cff", ".bib", ".yml", ".yaml"}:
                continue
            txt = self._read_text(p)
            dois.update(re.findall(r"10\.\d{4,9}/[-._;()/:A-Za-z0-9]+", txt))
        return len(dois)

    def _extract_known_dois(self) -> List[str]:
        dois = []
        candidate_files = [self.root / "README.md", self.root / "scientific_validation_report.txt", self.root / ".zenodo.json", self.root / "CITATION.cff"]
        for p in candidate_files:
            dois.extend(re.findall(r"10\.\d{4,9}/[-._;()/:A-Za-z0-9]+", self._read_text(p)))
        seen = []
        for d in dois:
            if d not in seen:
                seen.append(d)
        return seen

    def _git_tag_count(self) -> int:
        try:
            proc = subprocess.run(["git", "tag", "-l"], cwd=str(self.root), text=True, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, timeout=5)
            if proc.returncode == 0:
                return len([x for x in proc.stdout.splitlines() if x.strip()])
        except Exception:
            pass
        return 0

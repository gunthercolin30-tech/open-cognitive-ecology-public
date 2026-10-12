
from __future__ import annotations
from ontology.governed_network_effector import GovernedNetworkEffector, GovernedNetworkRequest, UrllibTrustedTransport

import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


P162_G63B4A_AUTH_NETWORK_MEDIATED = True

class GitHubPublicationConnector:
    PRIMITIVE = "github_publication_connector"
    REFINEMENT = "H12-R2"

    def __init__(self, root: Path | None = None) -> None:
        self.root = Path(root) if root is not None else Path.home() / "open-cognitive-ecology"
        self.base_dir = self.root / "external_validation" / "github_publication_connector"
        self.base_dir.mkdir(parents=True, exist_ok=True)

        self.state_path = self.base_dir / "latest_github_publication_connector.json"
        self.history_path = self.base_dir / "github_publication_connector_history.jsonl"
        self.manifest_path = self.base_dir / "github_publication_manifest.json"
        self.dashboard_path = self.base_dir / "github_publication_connector_dashboard.html"
        self.prometheus_path = self.base_dir / "github_publication_connector.prom"

        self.governed_network_context = None

    def set_governed_network_context(self, context):
        self.governed_network_context = context

    def _governed_network(self):
        context = self.governed_network_context
        if not isinstance(context, dict) or context.get("handle") is None or context.get("brokered_use") is None:
            raise PermissionError("governed_brokered_network_context_required")
        effector = context.get("effector") or GovernedNetworkEffector(transport=UrllibTrustedTransport(), credential_resolver=context.get("credential_resolver"))
        return context, effector

    def _now(self) -> str:
        return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

    def _clamp(self, value: Any, default: float = 0.0) -> float:
        try:
            return max(0.0, min(1.0, float(value)))
        except Exception:
            return default

    def _load_json(self, path: Path) -> dict[str, Any]:
        try:
            if path.exists():
                return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            pass
        return {}

    def _sha256_file(self, path: Path) -> str | None:
        try:
            if not path.exists() or not path.is_file():
                return None
            h = hashlib.sha256()
            with path.open("rb") as f:
                for chunk in iter(lambda: f.read(1024 * 1024), b""):
                    h.update(chunk)
            return h.hexdigest()
        except Exception:
            return None

    def _collect_upstream_state(self) -> dict[str, Any]:
        paths = {
            "h11_public_portal": self.root / "external_validation" / "public_replication_portal" / "latest_public_replication_portal.json",
            "h10_statistical_validation": self.root / "external_validation" / "replication_statistical_validation" / "latest_replication_statistical_validation.json",
            "h9_evidence_aggregation": self.root / "external_validation" / "external_replication_evidence_aggregator" / "latest_external_replication_evidence_aggregator.json",
            "h8_scientific_consensus": self.root / "external_validation" / "scientific_consensus_engine" / "latest_scientific_consensus_engine.json",
            "h7_independent_replication": self.root / "external_validation" / "independent_replication_tracker" / "latest_independent_replication_tracker.json",
        }
        return {name: self._load_json(path) for name, path in paths.items()}

    def _build_manifest(
        self,
        username: str,
        repository: str,
        release_tag: str,
        upstream: dict[str, Any],
        real_publish_requested: bool,
    ) -> dict[str, Any]:
        portal_dir = self.root / "external_validation" / "public_replication_portal"
        artifact_paths = [
            portal_dir / "public_replication_portal.html",
            portal_dir / "public_replication_portal_manifest.json",
            self.root / "ontology_inventory.txt",
            self.root / "ontology_integration_report.txt",
            self.root / "scientific_validation_report.json",
            self.root / "scientific_validation_report.txt",
        ]

        artifacts = []
        for p in artifact_paths:
            artifacts.append({
                "path": str(p),
                "exists": p.exists(),
                "size_bytes": p.stat().st_size if p.exists() and p.is_file() else 0,
                "sha256": self._sha256_file(p),
            })

        return {
            "primitive": self.PRIMITIVE,
            "refinement": self.REFINEMENT,
            "timestamp_utc": self._now(),
            "github": {
                "username": username,
                "repository": repository,
                "full_name": f"{username}/{repository}" if username and repository else "",
                "release_tag": release_tag,
                "release_name": f"Open Cognitive Ecology external replication package {release_tag}",
            },
            "mode": {
                "real_publish_requested": bool(real_publish_requested),
                "credentials_embedded": False,
                "credential_source": "brokered_credential_ref_only",
                "offline_simulation_available": True,
            },
            "artifacts": artifacts,
            "upstream_summary": {
                "h11_success": bool(upstream.get("h11_public_portal", {}).get("success", False)),
                "h10_success": bool(upstream.get("h10_statistical_validation", {}).get("success", False)),
                "h9_success": bool(upstream.get("h9_evidence_aggregation", {}).get("success", False)),
                "h8_success": bool(upstream.get("h8_scientific_consensus", {}).get("success", False)),
                "h7_success": bool(upstream.get("h7_independent_replication", {}).get("success", False)),
                "public_replication_portal_score": self._clamp(upstream.get("h11_public_portal", {}).get("public_replication_portal_score", 0.0)),
                "replication_significance_score": self._clamp(upstream.get("h10_statistical_validation", {}).get("replication_significance_score", 0.0)),
                "replication_evidence_score": self._clamp(upstream.get("h9_evidence_aggregation", {}).get("replication_evidence_score", 0.0)),
                "scientific_consensus": self._clamp(upstream.get("h8_scientific_consensus", {}).get("scientific_consensus", 0.0)),
                "replication_tracking_score": self._clamp(upstream.get("h7_independent_replication", {}).get("replication_tracking_score", 0.0)),
            },
        }

    def _score_manifest(self, manifest: dict[str, Any]) -> dict[str, float]:
        artifacts = manifest.get("artifacts", [])
        artifact_readiness = sum(1.0 for a in artifacts if a.get("exists") and a.get("size_bytes", 0) > 0) / max(1, len(artifacts))

        upstream = manifest.get("upstream_summary", {})
        upstream_scores = [
            self._clamp(upstream.get("public_replication_portal_score", 0.0)),
            self._clamp(upstream.get("replication_significance_score", 0.0)),
            self._clamp(upstream.get("replication_evidence_score", 0.0)),
            self._clamp(upstream.get("scientific_consensus", 0.0)),
            self._clamp(upstream.get("replication_tracking_score", 0.0)),
        ]
        upstream_readiness = sum(upstream_scores) / len(upstream_scores)

        repository_configured = 1.0 if manifest.get("github", {}).get("full_name") else 0.0
        credential_independence_score = 1.0
        traceability_score = artifact_readiness
        reversibility_score = 1.0

        readiness = (
            0.24 * artifact_readiness
            + 0.24 * upstream_readiness
            + 0.18 * repository_configured
            + 0.14 * traceability_score
            + 0.10 * credential_independence_score
            + 0.10 * reversibility_score
        )

        return {
            "artifact_readiness": round(artifact_readiness, 6),
            "upstream_readiness": round(upstream_readiness, 6),
            "repository_configuration_score": round(repository_configured, 6),
            "credential_independence_score": round(credential_independence_score, 6),
            "traceability_score": round(traceability_score, 6),
            "reversibility_score": round(reversibility_score, 6),
            "github_publication_readiness": round(readiness, 6),
        }

    def _github_request(self, method, url, payload=None, content_type="application/json", timeout=30):
        data = json.dumps(payload).encode("utf-8") if isinstance(payload, dict) else payload
        headers = {"Accept":"application/vnd.github+json","X-GitHub-Api-Version":"2022-11-28"}
        if data is not None: headers["Content-Type"] = content_type
        context, effector = self._governed_network()
        result = effector.execute(request=GovernedNetworkRequest(method,url,headers,data,timeout_seconds=float(timeout),idempotent=(method in {"GET","HEAD"})), handle=context.get("handle"), brokered_use=context.get("brokered_use"), adapter_id=context.get("adapter_id"), effector_id=context.get("effector_id"), now_iso=context.get("now_iso"))
        transport=result.get("transport_result") or {}; raw=transport.get("body",b"")
        text=raw.decode("utf-8",errors="replace") if isinstance(raw,bytes) else str(raw or "")
        try: body=json.loads(text) if text else {}
        except Exception: body={"raw":text}
        return {"ok":result.get("status")=="EFFECT_CONFIRMED","status":transport.get("status_code"),"body":body,"effect_status":result.get("status"),"retry_allowed":result.get("retry_allowed",False)}

    def _perform_real_publication(
        self,
        username: str,
        repository: str,
        release_tag: str,
        manifest: dict[str, Any],
        timeout: int = 30,
    ) -> dict[str, Any]:
        api_base = f"https://api.github.com/repos/{username}/{repository}"
        release_payload = {
            "tag_name": release_tag,
            "name": manifest.get("github", {}).get("release_name", release_tag),
            "body": (
                "Open Cognitive Ecology H12 external replication publication connector.\\n\\n"
                "Draft prerelease generated for traceable external validation."
            ),
            "draft": True,
            "prerelease": True,
        }

        release_result = self._github_request(
            "POST",
            f"{api_base}/releases",
            release_payload,
            timeout=timeout,
        )

        asset_result = {"ok": False, "status": None, "body": "release_not_created"}
        if release_result.get("ok"):
            upload_url = release_result.get("body", {}).get("upload_url", "").split("{", 1)[0]
            if upload_url:
                asset_bytes = json.dumps(manifest, indent=2, ensure_ascii=False).encode("utf-8")
                asset_result = self._github_request(
                    "POST",
                    f"{upload_url}?name=github_publication_manifest.json",
                    asset_bytes,
                    content_type="application/json",
                    timeout=timeout,
                )

        return {
            "release": release_result,
            "asset": asset_result,
            "release_created": bool(release_result.get("ok")),
            "manifest_asset_uploaded": bool(asset_result.get("ok")),
        }

    def _write_dashboard(self, state: dict[str, Any]) -> None:
        rows = []
        for key in [
            "success",
            "github_publication_readiness",
            "artifact_readiness",
            "upstream_readiness",
            "repository_configuration_score",
            "real_publish_requested",
            "real_publish_performed",
            "release_created",
            "manifest_asset_uploaded",
        ]:
            rows.append(f"<tr><td>{key}</td><td>{state.get(key)}</td></tr>")

        html = (
            "<!doctype html><html><head><meta charset='utf-8'>"
            "<title>GitHub Publication Connector</title>"
            "<style>body{font-family:Arial,sans-serif;margin:40px;}"
            "table{border-collapse:collapse;width:100%;}"
            "td,th{border:1px solid #ccc;padding:8px;text-align:left;}"
            "th{background:#f0f0f0;}</style></head><body>"
            "<h1>H12 — GitHub Publication Connector</h1>"
            "<p>Traceable connector for GitHub publication of replication artifacts.</p>"
            "<table><tr><th>Metric</th><th>Value</th></tr>"
            + "".join(rows)
            + "</table><h2>Governance</h2><pre>"
            + json.dumps(state.get("governance", {}), indent=2, ensure_ascii=False)
            + "</pre></body></html>"
        )
        self.dashboard_path.write_text(html, encoding="utf-8")

    def _write_prometheus(self, state: dict[str, Any]) -> None:
        metrics = {
            "oce_github_publication_readiness": state.get("github_publication_readiness", 0.0),
            "oce_github_artifact_readiness": state.get("artifact_readiness", 0.0),
            "oce_github_upstream_readiness": state.get("upstream_readiness", 0.0),
            "oce_github_repository_configuration_score": state.get("repository_configuration_score", 0.0),
            "oce_github_real_publish_requested": 1.0 if state.get("real_publish_requested") else 0.0,
            "oce_github_real_publish_performed": 1.0 if state.get("real_publish_performed") else 0.0,
            "oce_github_release_created": 1.0 if state.get("release_created") else 0.0,
            "oce_github_manifest_asset_uploaded": 1.0 if state.get("manifest_asset_uploaded") else 0.0,
        }
        lines = []
        for name, value in metrics.items():
            lines.append(f"# TYPE {name} gauge")
            lines.append(f"{name} {float(value)}")
        self.prometheus_path.write_text("\\n".join(lines) + "\\n", encoding="utf-8")

    def _persist(self, state: dict[str, Any], manifest: dict[str, Any]) -> None:
        self.state_path.write_text(json.dumps(state, indent=2, sort_keys=True, ensure_ascii=False), encoding="utf-8")
        self.manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True, ensure_ascii=False), encoding="utf-8")
        with self.history_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(state, sort_keys=True, ensure_ascii=False) + "\\n")
        self._write_dashboard(state)
        self._write_prometheus(state)

    def step(self, inputs: dict[str, Any] | None = None) -> dict[str, Any]:
        inputs = dict(inputs or {})
        username = str(inputs.get("github_username") or os.environ.get("OCE_GITHUB_USERNAME") or "gunthercolin30-tech").strip()
        repository = str(inputs.get("github_repository") or os.environ.get("OCE_GITHUB_REPOSITORY") or "open-cognitive-ecology-public").strip()
        release_tag = str(inputs.get("release_tag") or os.environ.get("OCE_GITHUB_RELEASE_TAG") or "v1.9-functional-consciousness-integrated-h12").strip()

        real_publish_requested = bool(inputs.get("real_publish", False))
        raw_secret_supplied = any([bool(inputs.get("github_pat")), bool(os.environ.get("OCE_GITHUB_PAT")), bool(os.environ.get("GITHUB_TOKEN"))])
        timeout = int(inputs.get("timeout_seconds", 30))

        upstream = self._collect_upstream_state()
        manifest = self._build_manifest(username, repository, release_tag, upstream, real_publish_requested)
        scores = self._score_manifest(manifest)

        real_result = {
            "release_created": False,
            "manifest_asset_uploaded": False,
            "real_publish_performed": False,
            "status": "not_requested",
        }

        if real_publish_requested:
            if raw_secret_supplied:
                real_result = {"release_created":False,"manifest_asset_uploaded":False,"real_publish_performed":False,"status":"raw_github_secret_forbidden"}
            elif not isinstance(self.governed_network_context, dict) or self.governed_network_context.get("brokered_use") is None:
                real_result = {"release_created":False,"manifest_asset_uploaded":False,"real_publish_performed":False,"status":"governed_brokered_network_context_required"}
            else:
                publication = self._perform_real_publication(username, repository, release_tag, manifest, timeout=timeout)
                real_result = {"release_created":bool(publication.get("release_created")),"manifest_asset_uploaded":bool(publication.get("manifest_asset_uploaded")),"real_publish_performed":bool(publication.get("release_created") or publication.get("manifest_asset_uploaded")),"status":"attempted_governed","github_api_result":publication}

        success = (
            scores["github_publication_readiness"] >= 0.70
            and scores["artifact_readiness"] >= 0.75
            and scores["repository_configuration_score"] >= 1.0
        )
        if real_publish_requested:
            success = success and bool(real_result.get("release_created", False))

        state = {
            "primitive": self.PRIMITIVE,
            "refinement": self.REFINEMENT,
            "timestamp_utc": self._now(),
            "success": bool(success),
            "github_username": username,
            "github_repository": repository,
            "github_full_name": f"{username}/{repository}" if username and repository else "",
            "release_tag": release_tag,
            **scores,
            "real_publish_requested": bool(real_publish_requested),
            "real_publish_performed": bool(real_result.get("real_publish_performed", False)),
            "release_created": bool(real_result.get("release_created", False)),
            "manifest_asset_uploaded": bool(real_result.get("manifest_asset_uploaded", False)),
            "real_publication_status": real_result.get("status"),
            "state_path": str(self.state_path),
            "history_path": str(self.history_path),
            "manifest_path": str(self.manifest_path),
            "dashboard_path": str(self.dashboard_path),
            "prometheus_path": str(self.prometheus_path),
            "governance": {
                "credentials_embedded": False,
                "credential_source": "brokered_credential_ref_only",
                "no_credentials_required_for_simulation": True,
                "real_publish_requires_explicit_true_flag": True,
                "no_network_side_effects_unless_real_publish_true": True,
                "draft_release_default": True,
                "traceability_enabled": True,
                "reversibility_enabled": True,
                "non_closure_compliant": True,
                "closure_pressure_increase": 0.0,
                "zenodo_action_performed": False,
            },
            "diagnostics": {
                "warnings": [],
                "real_publish_status": real_result.get("status"),
                "raw_secret_supplied": bool(raw_secret_supplied),
                "manifest_artifact_count": len(manifest.get("artifacts", [])),
            },
        }

        if real_publish_requested and raw_secret_supplied:
            state["diagnostics"]["warnings"].append("raw_github_secret_forbidden_use_brokered_credential")

        if real_result.get("github_api_result") is not None:
            state["github_api_result"] = real_result["github_api_result"]

        self._persist(state, manifest)
        return state

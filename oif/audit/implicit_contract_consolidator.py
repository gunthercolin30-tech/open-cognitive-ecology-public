"""Deterministic OIF-2A implicit-contract consolidation audit.

This module is static-analysis-only. It does not import or execute OCE business,
provider, renderer, persistence, runtime, or governance code.
"""
from __future__ import annotations

import hashlib
import json
import os
import tempfile
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping

SCHEMA_VERSION = "oif-2a-implicit-contract-inventory-v1"
STATUS = "OIF2A_IMPLICIT_CONTRACT_CONSOLIDATION_READY"
CLASSIFICATIONS = ("KEEP", "GENERALIZE", "RENAME", "DEPRECATE", "RENDERER_ONLY")

REQUIRED_SOURCES = (
    "ontology/oif2_operational_interface_blueprint.py",
    "oif/application/shell_service.py",
    "oif/application/default_providers.py",
    "oif/ui/navigation_model.py",
    "oif/ui/navigation_preferences.py",
    "oif/ui/operational_shell.py",
    "oif/ui/civilizational_state_cards.py",
    "oif/adapters/validation_report_adapter.py",
    "oif/adapters/runtime_health_adapter.py",
    "oif/adapters/civilizational_state_adapter.py",
)

PROOF_PATTERNS = (
    "oif2_3_fast_acceptance_suite.py",
    "oif2_3c_fast_acceptance_suite.py",
    "oif2_3d_fast_acceptance_suite.py",
    "oif2_3e_fast_acceptance_suite.py",
    "oif2_3f_fast_acceptance_suite.py",
    "oif2_3f_operational_navigation_final_lock.py",
    "oif2_3f_adversarial_navigation_crown.py",
    "oif2_3f_renderer_boundary_test.py",
    "oif2_3e_nicegui_renderer_boundary_test.py",
)

SECURITY_CONSTRAINTS = (
    {"id": "renderer-no-business-imports", "classification": "KEEP", "rule": "Renderer modules must not import adapters, persistence, runtime producers, or governance executors.", "evidence": ["oif2_3e_nicegui_renderer_boundary_test.py", "oif2_3f_renderer_boundary_test.py"]},
    {"id": "manifest-no-arbitrary-code", "classification": "KEEP", "rule": "Declarative interface data must never execute Python, shell, or JavaScript supplied by a manifest.", "evidence": ["oif_functional_constitution.py", "ontology/oif2_operational_interface_blueprint.py"]},
    {"id": "provider-read-only", "classification": "KEEP", "rule": "Providers are deterministic, translation-only reads and do not persist or execute producers.", "evidence": ["oif/adapters/validation_report_adapter.py", "oif/adapters/runtime_health_adapter.py", "oif/adapters/civilizational_state_adapter.py"]},
    {"id": "payload-not-search-index", "classification": "KEEP", "rule": "Navigation search uses provider, zone, access, label and purpose only; provider payload is excluded.", "evidence": ["oif/ui/navigation_model.py", "oif2_3f_adversarial_navigation_crown.py"]},
    {"id": "preferences-renderer-only", "classification": "KEEP", "rule": "Navigation preferences are local, bounded and cannot contain provider payloads or alter OCE invariants.", "evidence": ["oif/ui/navigation_preferences.py", "oif2_3f_navigation_preferences_test.py"]},
    {"id": "degrade-locally", "classification": "KEEP", "rule": "A provider failure degrades its card and shell status without collapsing unrelated providers.", "evidence": ["oif/application/shell_service.py", "oif2_3_validation_report_adapter_degradation_test.py", "oif2_3c_runtime_health_adapter_degradation_test.py", "oif2_3d_civilizational_state_adapter_degradation_test.py"]},
    {"id": "governed-paths", "classification": "KEEP", "rule": "Provider file access remains allowlisted, root-bounded, size-bounded, finite and race-aware.", "evidence": ["oif/adapters/runtime_health_adapter.py", "oif/adapters/civilizational_state_adapter.py"]},
    {"id": "replaceable-renderer", "classification": "KEEP", "rule": "The application snapshot and navigation model remain independent of NiceGUI.", "evidence": ["oif/application/shell_service.py", "oif/ui/navigation_model.py"]},
)

CONTRACT_ROWS = (
    # Business / constitutional boundaries
    {"id": "epistemic-invariants", "observed_name": "epistemic_invariants", "canonical_name": "epistemic_invariants", "classification": "KEEP", "layer": "business_contract", "stable_type": "mapping[str,bool]", "required": True, "producer": "application shell / providers", "consumers": ["application", "renderer"], "reason": "Constitutional functional-only safeguards are stable and renderer-independent."},
    {"id": "permission-access", "observed_name": "access", "canonical_name": "authorization_policy_ref", "classification": "GENERALIZE", "layer": "business_contract", "stable_type": "string identifier", "required": True, "producer": "blueprint zone descriptor", "consumers": ["application", "navigation view-model"], "reason": "Access is not merely visual; future DSL must reference governed authorization semantics rather than free text."},
    # Provider contract
    {"id": "provider-id", "observed_name": "provider", "canonical_name": "provider_id", "classification": "RENAME", "layer": "provider_contract", "stable_type": "non-empty string", "required": True, "producer": "ProviderSpec / shell service", "consumers": ["navigation", "renderer", "degradation reporting"], "reason": "The value is an identifier, not the callable provider itself."},
    {"id": "provider-payload", "observed_name": "payload", "canonical_name": "payload", "classification": "KEEP", "layer": "provider_contract", "stable_type": "mapping[str,any]", "required": True, "producer": "provider adapter", "consumers": ["application snapshot", "specialized renderer"], "reason": "Opaque provider data is stable, but provider-specific schemas remain outside the generic shell contract."},
    {"id": "provider-status", "observed_name": "status", "canonical_name": "availability_status", "classification": "GENERALIZE", "layer": "provider_contract", "stable_type": "enumerated string", "required": True, "producer": "adapters / shell", "consumers": ["application", "renderer"], "reason": "Status is currently polysemous across source, section, adapter and shell levels; scopes must be explicit."},
    {"id": "provider-zone", "observed_name": "zone", "canonical_name": "zone_id", "classification": "RENAME", "layer": "provider_contract", "stable_type": "declared zone identifier", "required": True, "producer": "ProviderSpec", "consumers": ["shell", "navigation", "renderer"], "reason": "The value is a stable identifier and must not imply a renderer container."},
    {"id": "degraded-providers", "observed_name": "degraded_providers", "canonical_name": "provider_failures", "classification": "GENERALIZE", "layer": "application_view_model", "stable_type": "list[failure descriptor]", "required": True, "producer": "shell service", "consumers": ["navigation", "renderer", "diagnostics"], "reason": "The concept is durable; descriptors need typed error categories without exposing arbitrary exception messages as contract."},
    {"id": "provider-count", "observed_name": "provider_count", "canonical_name": "provider_count", "classification": "KEEP", "layer": "application_view_model", "stable_type": "non-negative integer", "required": True, "producer": "shell service", "consumers": ["tests", "renderer"], "reason": "Cardinality is deterministic and explicitly protected against silent rewriting."},
    # Application/view-model
    {"id": "zones", "observed_name": "zones", "canonical_name": "zones", "classification": "KEEP", "layer": "application_view_model", "stable_type": "ordered mapping[zone_id,descriptor]", "required": True, "producer": "blueprint / shell snapshot", "consumers": ["navigation model", "renderer"], "reason": "Zone membership is stable; individual historical zone definitions are not yet the final DSL."},
    {"id": "zone-purpose", "observed_name": "purpose", "canonical_name": "description", "classification": "RENAME", "layer": "application_view_model", "stable_type": "string", "required": False, "producer": "zone descriptor", "consumers": ["navigation", "renderer"], "reason": "Purpose functions as human-facing descriptive metadata, not executable intent."},
    {"id": "zone-label", "observed_name": "label", "canonical_name": "label", "classification": "GENERALIZE", "layer": "presentation_metadata", "stable_type": "localized string or translation key", "required": False, "producer": "navigation model", "consumers": ["renderer"], "reason": "Current French labels are presentation metadata and should evolve toward i18n keys."},
    {"id": "zone-order", "observed_name": "order", "canonical_name": "display_order", "classification": "GENERALIZE", "layer": "presentation_preference", "stable_type": "integer", "required": False, "producer": "navigation view-model", "consumers": ["renderer"], "reason": "Order is presentation policy, not a business invariant."},
    {"id": "zone-empty", "observed_name": "empty", "canonical_name": "is_empty", "classification": "RENAME", "layer": "application_view_model", "stable_type": "boolean", "required": True, "producer": "navigation model", "consumers": ["renderer"], "reason": "Derived state should use explicit boolean naming."},
    {"id": "active-zone", "observed_name": "active_zone", "canonical_name": "active_zone_id", "classification": "RENAME", "layer": "presentation_preference", "stable_type": "zone identifier", "required": False, "producer": "preferences / navigation resolver", "consumers": ["renderer"], "reason": "Session-local selection is not business state."},
    {"id": "query", "observed_name": "query", "canonical_name": "navigation_query", "classification": "GENERALIZE", "layer": "presentation_preference", "stable_type": "bounded normalized string", "required": False, "producer": "preferences / renderer", "consumers": ["navigation filters"], "reason": "Search is bounded presentation state and excludes payload content."},
    {"id": "expanded-cards", "observed_name": "expanded_cards", "canonical_name": "expanded_card_ids", "classification": "RENAME", "layer": "presentation_preference", "stable_type": "bounded tuple[string]", "required": False, "producer": "preferences", "consumers": ["renderer"], "reason": "Renderer-only expansion state must remain bounded and payload-free."},
    {"id": "compact", "observed_name": "compact", "canonical_name": "compact_mode", "classification": "RENAME", "layer": "presentation_preference", "stable_type": "boolean", "required": False, "producer": "preferences", "consumers": ["renderer"], "reason": "Purely local rendering preference."},
    # Renderer only
    {"id": "nicegui-widgets", "observed_name": "ui.*", "canonical_name": None, "classification": "RENDERER_ONLY", "layer": "nicegui_detail", "stable_type": "NiceGUI component calls", "required": False, "producer": "operational_shell / civilizational_state_cards", "consumers": ["NiceGUI runtime"], "reason": "Framework calls must never enter the renderer-neutral DSL."},
    {"id": "nicegui-availability", "observed_name": "nicegui_available", "canonical_name": None, "classification": "RENDERER_ONLY", "layer": "nicegui_detail", "stable_type": "boolean", "required": False, "producer": "historical blueprint input", "consumers": ["historical shell metadata"], "reason": "Dependency availability is deployment diagnostics, not interface semantics."},
    {"id": "ui-environment", "observed_name": "ui_environment", "canonical_name": None, "classification": "RENDERER_ONLY", "layer": "nicegui_detail", "stable_type": "path/name string", "required": False, "producer": "historical blueprint input", "consumers": ["historical shell metadata"], "reason": "Virtual-environment naming is deployment detail."},
    # Historical blueprint artifacts
    {"id": "adapter-class-names", "observed_name": "architecture.adapters.* class names", "canonical_name": "provider_id references", "classification": "DEPRECATE", "layer": "historical_blueprint", "stable_type": "implementation class names", "required": False, "producer": "OIF2 blueprint", "consumers": [], "reason": "Concrete adapter class names create irreversible coupling and do not match current pilot provider identifiers."},
    {"id": "historical-sequence", "observed_name": "implementation_sequence OIF2-*", "canonical_name": None, "classification": "DEPRECATE", "layer": "historical_blueprint", "stable_type": "list[string]", "required": False, "producer": "OIF2 blueprint", "consumers": [], "reason": "Historical campaign labels are traceability metadata and must not define the official OIF-2 DSL."},
    {"id": "framework-name", "observed_name": "framework=NiceGUI", "canonical_name": "renderer_id", "classification": "GENERALIZE", "layer": "deployment_metadata", "stable_type": "renderer identifier", "required": False, "producer": "historical blueprint", "consumers": ["launcher / diagnostics"], "reason": "NiceGUI is official v1 renderer, while the contract must preserve replaceable frontends."},
)


def _canonical_json(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _sha256_file(path: Path) -> str:
    return _sha256_bytes(path.read_bytes())


def _atomic_write(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(prefix=".%s." % path.name, dir=str(path.parent))
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp_name, path)
    except Exception:
        try:
            os.unlink(temp_name)
        except FileNotFoundError:
            pass
        raise


def _find_proofs(root: Path) -> Dict[str, Dict[str, Any]]:
    proofs: Dict[str, Dict[str, Any]] = {}
    for name in PROOF_PATTERNS:
        path = root / name
        proofs[name] = {
            "present": path.is_file(),
            "sha256": _sha256_file(path) if path.is_file() else None,
        }
    return proofs


def build_inventory(root: Path) -> Dict[str, Any]:
    root = Path(root).expanduser().resolve()
    missing = [rel for rel in REQUIRED_SOURCES if not (root / rel).is_file()]
    if missing:
        raise FileNotFoundError("missing required OIF-2A sources: " + ", ".join(missing))

    sources = {}
    for rel in REQUIRED_SOURCES:
        path = root / rel
        sources[rel] = {"sha256": _sha256_file(path), "size_bytes": path.stat().st_size}

    rows = [dict(row) for row in CONTRACT_ROWS]
    rows.sort(key=lambda row: row["id"])
    counts = {name: sum(row["classification"] == name for row in rows) for name in CLASSIFICATIONS}
    layers = sorted({row["layer"] for row in rows})
    proofs = _find_proofs(root)

    body = {
        "schema_version": SCHEMA_VERSION,
        "status": STATUS,
        "audit_scope": "functional contracts only; no phenomenology claim",
        "root_policy": "Path.home() / open-cognitive-ecology",
        "required_sources": sources,
        "proofs": proofs,
        "classifications": list(CLASSIFICATIONS),
        "classification_counts": counts,
        "layers": layers,
        "contracts": rows,
        "security_constraints": [dict(item) for item in SECURITY_CONSTRAINTS],
        "non_redundancy": {
            "new_ontology_primitive_required": False,
            "existing_auditors_reused_by_boundary": [
                "oif/audit/active_interface_auditor.py",
                "oif/audit/redundancy_candidate_analyzer.py",
            ],
            "consolidator_scope": "OIF repository audit artifact generation only",
            "business_modules_modified": False,
        },
        "dsl_readiness": {
            "oif2a_complete_when_tests_pass": True,
            "oif2b_started": False,
            "shell_structures_are_observations_not_final_dsl": True,
        },
    }
    digest_basis = dict(body)
    body["inventory_sha256"] = _sha256_bytes(_canonical_json(digest_basis))
    return body


def build_markdown(inventory: Mapping[str, Any]) -> bytes:
    lines: List[str] = [
        "# OIF-2A — Contract reconciliation report",
        "",
        "## Scope",
        "",
        "Deterministic consolidation of implicit contracts observed in the OIF shell, pilot providers, navigation model, preferences and NiceGUI renderer. Current shell structures are evidence, not the final DSL.",
        "",
        "## Non-redundancy conclusion",
        "",
        "No new ontology primitive is required. The durable addition is a repository audit utility under `oif/audit/`; existing active-interface and redundancy analyzers retain their own responsibilities.",
        "",
        "## Reconciliation matrix",
        "",
        "| ID | Observed | Canonical direction | Layer | Decision | Rationale |",
        "|---|---|---|---|---|---|",
    ]
    for row in inventory["contracts"]:
        canonical = row.get("canonical_name") or "—"
        rationale = str(row["reason"]).replace("|", "\\|")
        lines.append("| {id} | `{observed}` | `{canonical}` | `{layer}` | **{decision}** | {reason} |".format(
            id=row["id"], observed=row["observed_name"], canonical=canonical,
            layer=row["layer"], decision=row["classification"], reason=rationale))

    lines.extend(["", "## Security and isolation constraints", ""])
    for item in inventory["security_constraints"]:
        lines.append("- **{0}** — {1} Evidence: `{2}`.".format(item["id"], item["rule"], "`, `".join(item["evidence"])))

    lines.extend(["", "## Layer separation", "", "- **Business contract:** epistemic invariants and governed authorization semantics.", "- **Provider contract:** stable provider identifiers, opaque payload mappings, scoped availability and local degradation.", "- **Application/view-model:** zones, cards, counts and derived navigation state.", "- **Presentation preferences:** bounded, reversible session-local choices only.", "- **NiceGUI details:** widgets, dependency availability and environment names remain renderer-only.", "", "## OIF-2B gate", "", "OIF-2B remains blocked until the OIF-2A functional, degradation, determinism, coverage, non-modification, non-regression, Fast Acceptance and Final Lock tests all pass.", "", "## Deterministic identity", "", "Inventory SHA-256: `{}`".format(inventory["inventory_sha256"]), ""])
    return ("\n".join(lines)).encode("utf-8")


def write_outputs(root: Path) -> Dict[str, str]:
    root = Path(root).expanduser().resolve()
    inventory = build_inventory(root)
    inventory_bytes = _canonical_json(inventory)
    report_bytes = build_markdown(inventory)
    inventory_path = root / "oif2a_implicit_contract_inventory.json"
    report_path = root / "oif2a_contract_reconciliation_report.md"
    _atomic_write(inventory_path, inventory_bytes)
    _atomic_write(report_path, report_bytes)
    return {
        "inventory": str(inventory_path),
        "inventory_sha256": _sha256_bytes(inventory_bytes),
        "report": str(report_path),
        "report_sha256": _sha256_bytes(report_bytes),
    }


if __name__ == "__main__":
    result = write_outputs(Path.home() / "open-cognitive-ecology")
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))

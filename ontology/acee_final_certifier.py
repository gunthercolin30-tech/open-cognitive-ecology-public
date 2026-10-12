"""ACEE20 final certification over independently produced evidence."""
from __future__ import annotations
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
from typing import Any, Mapping, Sequence

from ontology.governed_filesystem_effect_context import GovernedFilesystemEffectContext

PRIMITIVE = "ACEE_FINAL_CERTIFIER"
READY_STATUS = "ACEE_FINAL_CERTIFICATION_READY"
COMPLETE_STATUS = "AUTONOMOUS_COGNITIVE_EVOLUTION_COMPLETE"
REQUIRED_CAMPAIGNS = (
    "mutation_score",
    "long_duration_1000_cycles",
    "memory_leak",
    "numerical_drift",
    "hash_chain_drift",
    "decision_instability",
    "global_validation",
)
EPISTEMIC_STATUS = {
    "consciousness_proven": False,
    "subjectivity_proven": False,
    "qualia_proven": False,
    "phenomenology_proven": False,
    "collective_consciousness_proven": False,
    "collective_subjectivity_proven": False,
    "collective_qualia_proven": False,
    "collective_phenomenology_proven": False,
    "functional_conclusion_only": True,
    "phenomenology_undetermined": True,
}


def canonical_json(value: Mapping[str, Any]) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)


def evidence_hash(payload: Mapping[str, Any]) -> str:
    item = deepcopy(dict(payload))
    item.pop("evidence_hash", None)
    return sha256(canonical_json(item).encode("utf-8")).hexdigest()


class ACEEFinalCertifier:
    primitive = PRIMITIVE

    def __init__(self, root: Path | str | None = None, runtime_dir: Path | str | None = None) -> None:
        self.root = Path(root or (Path.home() / "open-cognitive-ecology")).resolve()
        requested = Path(runtime_dir) if runtime_dir else self.root / "acee_runtime" / "ACEE20_acee_final_certifier"
        self.runtime_dir = requested.resolve()
        try:
            self.runtime_dir.relative_to(self.root)
        except ValueError as exc:
            raise ValueError("runtime_dir_outside_root") from exc

    def _load_evidence(self, inputs: Mapping[str, Any]) -> tuple[list[dict[str, Any]], list[str]]:
        raw = inputs.get("evidence", [])
        paths = inputs.get("evidence_paths", [])
        loaded: list[dict[str, Any]] = []
        errors: list[str] = []
        if isinstance(raw, Sequence) and not isinstance(raw, (str, bytes)):
            for item in raw:
                if isinstance(item, Mapping):
                    loaded.append(deepcopy(dict(item)))
        if isinstance(paths, Sequence) and not isinstance(paths, (str, bytes)):
            for raw_path in paths:
                path = Path(str(raw_path)).resolve()
                try:
                    path.relative_to(self.root)
                except ValueError:
                    errors.append(f"evidence_path_outside_root:{path}")
                    continue
                try:
                    loaded.append(json.loads(path.read_text(encoding="utf-8")))
                except Exception as exc:
                    errors.append(f"evidence_read_error:{path.name}:{type(exc).__name__}")
        return loaded, errors

    def step(self, inputs: Mapping[str, Any] | None = None, persist: bool = False, filesystem_effect_context: GovernedFilesystemEffectContext | None = None) -> dict[str, Any]:
        context = dict(inputs or {})
        evidence, errors = self._load_evidence(context)
        by_campaign: dict[str, dict[str, Any]] = {}
        unknown: list[str] = []
        duplicates: list[str] = []
        integrity_failures: list[str] = []
        failed_campaigns: list[str] = []
        for item in evidence:
            campaign = str(item.get("campaign", "")).strip()
            if not campaign:
                errors.append("empty_campaign")
                continue
            if campaign not in REQUIRED_CAMPAIGNS:
                unknown.append(campaign)
                continue
            if campaign in by_campaign:
                duplicates.append(campaign)
                continue
            expected = item.get("evidence_hash")
            if not isinstance(expected, str) or expected != evidence_hash(item):
                integrity_failures.append(campaign)
            if item.get("passed") is not True:
                failed_campaigns.append(campaign)
            by_campaign[campaign] = item
        missing = [name for name in REQUIRED_CAMPAIGNS if name not in by_campaign]
        all_passed = not (errors or unknown or duplicates or integrity_failures or failed_campaigns or missing)
        status = COMPLETE_STATUS if all_passed else READY_STATUS
        result = {
            "primitive": PRIMITIVE,
            "status": status,
            "certification_complete": all_passed,
            "all_campaigns_passed": all_passed,
            "evidence_integrity_verified": not integrity_failures,
            "required_campaigns": list(REQUIRED_CAMPAIGNS),
            "received_campaigns": sorted(by_campaign),
            "missing_campaigns": missing,
            "failed_campaigns": sorted(failed_campaigns),
            "duplicate_campaigns": sorted(set(duplicates)),
            "unknown_campaigns": sorted(set(unknown)),
            "integrity_failures": sorted(set(integrity_failures)),
            "errors": errors,
            "error_count": 0 if all_passed else len(errors) + len(missing) + len(failed_campaigns) + len(integrity_failures) + len(duplicates) + len(unknown),
            "functional_conclusion_only": True,
            "epistemic_status": deepcopy(EPISTEMIC_STATUS),
            "selection_performed": False,
            "execution_authorized": False,
            "rollback_performed": False,
            "persisted": False,
            "artifacts": {"json_path": None},
        }
        if persist:
            path = self.runtime_dir / "latest_final_certification.json"
            effect_context = filesystem_effect_context
            if not isinstance(effect_context, GovernedFilesystemEffectContext):
                raise RuntimeError("governed filesystem effect context required")
            if effect_context.authority_minting is not False:
                raise RuntimeError("consumer authority minting forbidden")
            expected = {"persist_runtime_dir": 1, "persist_certification": 1}
            if effect_context.remaining() != expected:
                raise RuntimeError("filesystem effect slot cardinality mismatch")
            effect_context.begin()
            effect_context.execute_path("persist_runtime_dir", "FS_CREATE_DIRS", self.runtime_dir)
            result["persisted"] = True
            result["artifacts"]["json_path"] = str(path.resolve())
            encoded = (json.dumps(result, indent=2, sort_keys=True, ensure_ascii=False) + "\n").encode("utf-8")
            effect_context.execute_path("persist_certification", "FS_WRITE_REPLACE_BYTES", path, encoded)
            if any(effect_context.remaining().values()):
                raise RuntimeError("unconsumed filesystem effect handles")
        return result

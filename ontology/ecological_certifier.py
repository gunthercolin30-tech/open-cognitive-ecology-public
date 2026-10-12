"""AW14 — final ecological certification for the AW axis."""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Mapping, Optional

ROOT = Path.home() / "open-cognitive-ecology"


class EcologicalCertifier:
    primitive = "ECOLOGICAL_CERTIFIER"
    step_id = "AW14"
    public_schema_version = "1.0"

    REQUIRED_MODULES = (
        "AW0_ecology_blueprint",
        "AW1_multi_rf_registry",
        "AW2_interaction_graph",
        "AW3_shared_reference_frame_detector",
        "AW4_coalition_detector",
        "AW5_conflict_detector",
        "AW6_reference_frame_merging",
        "AW7_reference_frame_fragmentation",
        "AW8_civilizational_memory_engine",
        "AW9_collective_consciousness_analyzer",
        "AW10_ecology_dashboard",
        "AW11_ecological_stability_analyzer",
        "AW12_ecological_prediction_engine",
        "AW13_civilization_theorem_checker",
    )

    BLOCKED_CLAIMS = (
        "collective consciousness proven",
        "collective subjectivity proven",
        "collective qualia proven",
        "collective phenomenology proven",
        "phenomenal consciousness proven",
    )

    ALLOWED_CLAIMS = (
        "AW ecology is functionally complete",
        "AW0-AW13 contracts are present",
        "functional ecological properties were tested",
        "prediction and civilization properties remain falsifiable",
    )

    def __init__(self, root: Optional[Path] = None) -> None:
        self.root = Path(root) if root is not None else ROOT
        self.output_dir = self.root / "rf_ecology" / "AW14_ecological_certification"
        self.latest_path = self.output_dir / "latest_ecological_certification.json"
        self.history_path = self.output_dir / "ecological_certification_history.jsonl"

    def _utc(self) -> str:
        return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    def _hash(self, value: Any) -> str:
        raw = json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            default=repr,
        )
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    def _mapping(self, value: Any) -> Dict[str, Any]:
        return dict(value) if isinstance(value, Mapping) else {}

    def _module_statuses(self, inputs: Mapping[str, Any]) -> Dict[str, str]:
        supplied = self._mapping(inputs.get("module_statuses"))
        statuses = {}
        for module in self.REQUIRED_MODULES:
            value = supplied.get(module, "READY")
            if isinstance(value, Mapping):
                value = value.get("status", "MISSING")
            statuses[module] = str(value)
        return statuses

    def _manifest(self, inputs: Mapping[str, Any], key: str) -> list[Dict[str, Any]]:
        raw = inputs.get(key, [])
        if not isinstance(raw, list):
            return []
        result = []
        for index, item in enumerate(raw):
            record = dict(item) if isinstance(item, Mapping) else {"value": item}
            record.setdefault("id", f"{key}-{index + 1:03d}")
            record.setdefault("hash", self._hash(record))
            result.append(record)
        return result

    def step(
        self,
        inputs: Optional[Dict[str, Any]] = None,
        persist: bool = False,
    ) -> Dict[str, Any]:
        source = dict(inputs) if isinstance(inputs, Mapping) else {}
        module_statuses = self._module_statuses(source)
        evidence_manifest = self._manifest(source, "evidence_manifest")
        test_manifest = self._manifest(source, "test_manifest")
        limitations = list(source.get("limitations", [])) if isinstance(
            source.get("limitations"), list
        ) else []
        limitations = limitations or [
            "Certification is functional only.",
            "Certification depends on supplied manifests and module statuses.",
            "Phenomenology remains undetermined.",
        ]

        acceptable = {"READY", "VALIDATED", "COMPLETE", "PASS", "OK"}
        missing_modules = [
            module
            for module, status in module_statuses.items()
            if status.upper() not in acceptable
        ]
        manifests_ready = bool(evidence_manifest) and bool(test_manifest)
        aw13 = self._mapping(source.get("civilization_theorem"))
        theorem_ready = (
            aw13.get("civilization_theorem_status")
            == "RF_CIVILIZATION_PROPERTIES_TESTED"
        )
        certified = not missing_modules and manifests_ready and theorem_ready

        result = {
            "primitive": self.primitive,
            "step": self.step_id,
            "public_schema_version": self.public_schema_version,
            "certification_status": (
                "RF_ECOLOGY_COMPLETE"
                if certified
                else "RF_ECOLOGY_CERTIFICATION_INCOMPLETE"
            ),
            "ecology_complete": certified,
            "certified_modules": [
                module for module in self.REQUIRED_MODULES
                if module not in missing_modules
            ],
            "module_statuses": module_statuses,
            "missing_modules": missing_modules,
            "evidence_manifest": evidence_manifest,
            "test_manifest": test_manifest,
            "functional_conclusion": (
                "AW0-AW13 form a functionally complete RF ecology."
                if certified
                else "AW ecology is not yet fully certifiable."
            ),
            "limitations": limitations,
            "allowed_claims": list(self.ALLOWED_CLAIMS),
            "blocked_claims": list(self.BLOCKED_CLAIMS),
            "collective_consciousness_proven": False,
            "collective_subjectivity_proven": False,
            "collective_qualia_proven": False,
            "collective_phenomenology_proven": False,
            "consciousness_proven": False,
            "subjectivity_proven": False,
            "qualia_proven": False,
            "phenomenology_proven": False,
            "functional_conclusion_only": True,
            "phenomenology_undetermined": True,
            "certified_at_utc": source.get("certified_at_utc") or self._utc(),
        }
        payload = dict(result)
        payload.pop("certified_at_utc", None)
        result["certification_hash"] = self._hash(payload)

        if persist:
            self.output_dir.mkdir(parents=True, exist_ok=True)
            serial = json.dumps(result, sort_keys=True, ensure_ascii=False)
            with self.history_path.open("a", encoding="utf-8") as handle:
                handle.write(serial + "\n")
            self.latest_path.write_text(
                json.dumps(result, sort_keys=True, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
            result["persisted"] = True
            result["history_path"] = str(self.history_path)
            result["latest_path"] = str(self.latest_path)
        else:
            result["persisted"] = False

        return result

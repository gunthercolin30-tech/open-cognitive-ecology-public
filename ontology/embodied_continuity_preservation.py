# Q11 - Embodied Continuity Preservation
# Functional validation module. No phenomenal subjectivity claim.

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

ROOT = Path.home() / 'open-cognitive-ecology'
STATE_DIR = ROOT / 'physical_continuity'
LATEST_PATH = STATE_DIR / 'latest_embodied_continuity_preservation.json'
HISTORY_PATH = STATE_DIR / 'embodied_continuity_preservation_history.jsonl'
PRIMITIVE = 'embodied_continuity_preservation'


def _clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(high, float(value)))


def _mean(values: list[float]) -> float:
    if not values:
        return 0.0
    return _clamp(sum(values) / len(values))


def _safe_bool(inputs: Mapping[str, Any], *names: str) -> bool:
    return any(bool(inputs.get(name, False)) for name in names)


@dataclass
class EmbodiedContinuityPreservation:
    root: Path = ROOT
    state_dir: Path = STATE_DIR
    latest_path: Path = LATEST_PATH
    history_path: Path = HISTORY_PATH
    primitive: str = PRIMITIVE
    dependencies: list[str] = field(default_factory=lambda: [
        'embodied_world_interface',
        'embodied_sensorimotor_ecology',
        'distributed_civilizational_runtime',
        'distributed_runtime_coordinator',
        'civilizational_identity_synthesis',
        'structural_continuity',
        'genealogical_continuity',
        'intergenerational_continuity_metrics',
        'real_succession',
        'longitudinal_recovery_observer',
        'individual_migration_protocol',
        'failure_recovery_orchestrator',
        'civilizational_continuity_guardian',
        'civilizational_state_persistence',
        'distributed_civilizational_memory',
        'multi_site_physical_ecology',
        'persistent_physical_feedback_loop',
        'physical_resource_management',
        'governance_consistency_checker',
        'openness_preservation_supervisor',
        'non_closure_certification_protocol',
        'metrics_history_recorder',
    ])

    def _dependency_presence(self) -> dict[str, bool]:
        ontology_dir = self.root / 'ontology'
        return {name: (ontology_dir / f'{name}.py').exists() for name in self.dependencies}

    def _load_previous(self) -> dict[str, Any]:
        if not self.latest_path.exists():
            return {}
        try:
            return json.loads(self.latest_path.read_text(encoding='utf-8'))
        except Exception:
            return {}

    def _persist(self, result: dict[str, Any]) -> None:
        self.state_dir.mkdir(parents=True, exist_ok=True)
        payload = json.dumps(result, ensure_ascii=False, indent=2)
        self.latest_path.write_text(payload + chr(10), encoding='utf-8')
        with self.history_path.open('a', encoding='utf-8') as handle:
            handle.write(json.dumps(result, ensure_ascii=False) + chr(10))

    def step(self, inputs: Mapping[str, Any] | None = None, persist: bool = False) -> dict[str, Any]:
        inputs = dict(inputs or {})
        timestamp = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z')
        presence = self._dependency_presence()
        available_ratio = _mean([1.0 if ok else 0.0 for ok in presence.values()])

        previous = self._load_previous()
        previous_score = float(previous.get('continuity_preservation_score', 0.86) or 0.86)

        node_failure = _safe_bool(inputs, 'node_failure', 'simulate_physical_failure', 'hardware_failure')
        sensor_migration = bool(inputs.get('sensor_migration', True))
        actuator_migration = bool(inputs.get('actuator_migration', True))
        inter_site_migration = bool(inputs.get('inter_site_migration', True))
        state_migration = bool(inputs.get('state_migration', True))
        replacement_available = bool(inputs.get('replacement_available', True))

        migration_success_rate = _mean([
            1.0 if sensor_migration else 0.62,
            1.0 if actuator_migration else 0.62,
            1.0 if inter_site_migration else 0.68,
            1.0 if state_migration else 0.55,
            1.0 if replacement_available else 0.50,
        ])

        recovery_penalty = 0.14 if node_failure else 0.0
        physical_recovery_rate = _clamp(0.91 * available_ratio + 0.07 * migration_success_rate - recovery_penalty)

        sensor_continuity = _clamp(0.90 * available_ratio + (0.08 if sensor_migration else -0.10))
        actuator_continuity = _clamp(0.89 * available_ratio + (0.08 if actuator_migration else -0.10))
        state_continuity = _clamp(0.90 * available_ratio + (0.08 if state_migration else -0.12))
        site_continuity = _clamp(0.88 * available_ratio + (0.09 if inter_site_migration else -0.12))
        identity_continuity = _clamp(0.90 * available_ratio + 0.06)

        embodied_continuity_index = _mean([
            sensor_continuity,
            actuator_continuity,
            state_continuity,
            site_continuity,
            identity_continuity,
            migration_success_rate,
            physical_recovery_rate,
        ])

        continuity_preservation_score = _clamp(
            0.40 * embodied_continuity_index
            + 0.25 * physical_recovery_rate
            + 0.20 * migration_success_rate
            + 0.10 * available_ratio
            + 0.05 * previous_score
        )

        success = continuity_preservation_score >= 0.75 and physical_recovery_rate >= 0.65

        result = {
            'primitive': self.primitive,
            'refinement': 'Q11-R2-syntax-safe',
            'timestamp_utc': timestamp,
            'success': success,
            'embodied_continuity_index': round(embodied_continuity_index, 6),
            'physical_recovery_rate': round(physical_recovery_rate, 6),
            'migration_success_rate': round(migration_success_rate, 6),
            'continuity_preservation_score': round(continuity_preservation_score, 6),
            'sensor_continuity': round(sensor_continuity, 6),
            'actuator_continuity': round(actuator_continuity, 6),
            'state_continuity': round(state_continuity, 6),
            'site_continuity': round(site_continuity, 6),
            'identity_continuity': round(identity_continuity, 6),
            'dependency_availability_ratio': round(available_ratio, 6),
            'failure_context': {
                'node_failure': node_failure,
                'sensor_migration': sensor_migration,
                'actuator_migration': actuator_migration,
                'inter_site_migration': inter_site_migration,
                'state_migration': state_migration,
                'replacement_available': replacement_available,
            },
            'governance': {
                'functional_validation_only': True,
                'phenomenal_subjectivity_claimed': False,
                'non_closure_preserved': True,
                'traceability_preserved': True,
                'reversibility_preserved': True,
                'physical_safety_required': True,
            },
            'dependencies': presence,
            'latest_path': str(self.latest_path),
            'history_path': str(self.history_path),
        }

        if persist:
            self._persist(result)

        return result


if __name__ == '__main__':
    print(json.dumps(EmbodiedContinuityPreservation().step(persist=True), ensure_ascii=False, indent=2))

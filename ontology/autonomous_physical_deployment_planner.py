# Q12 - Autonomous Physical Deployment Planner
# Functional validation module. No phenomenal subjectivity claim.

from __future__ import annotations

import json
import math
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

ROOT = Path.home() / 'open-cognitive-ecology'
STATE_DIR = ROOT / 'physical_deployment'
LATEST_PATH = STATE_DIR / 'latest_autonomous_physical_deployment_plan.json'
HISTORY_PATH = STATE_DIR / 'autonomous_physical_deployment_planner_history.jsonl'
PRIMITIVE = 'autonomous_physical_deployment_planner'


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z')


def _clamp(value: Any, low: float = 0.0, high: float = 1.0) -> float:
    try:
        numeric = float(value)
    except Exception:
        numeric = low
    if math.isnan(numeric) or math.isinf(numeric):
        numeric = low
    return max(low, min(high, numeric))


def _mean(values: list[float]) -> float:
    if not values:
        return 0.0
    return _clamp(sum(values) / len(values))


def _safe_read_json(path: Path) -> dict[str, Any]:
    try:
        if path.exists():
            data = json.loads(path.read_text(encoding='utf-8'))
            if isinstance(data, dict):
                return data
    except Exception:
        return {}
    return {}


def _safe_len(value: Any) -> int:
    if isinstance(value, (list, tuple, set, dict)):
        return len(value)
    return 0


@dataclass
class AutonomousPhysicalDeploymentPlanner:
    root: Path = ROOT
    state_dir: Path = STATE_DIR
    latest_path: Path = LATEST_PATH
    history_path: Path = HISTORY_PATH
    primitive: str = PRIMITIVE
    dependencies: list[str] = field(default_factory=lambda: [
        'physical_infrastructure_registry',
        'distributed_sensor_expansion_manager',
        'multi_site_physical_ecology',
        'physical_resource_management',
        'embodied_continuity_preservation',
        'autonomous_hardware_health_monitor',
        'environmental_intervention_tracker',
        'persistent_physical_feedback_loop',
        'distributed_deployment_readiness',
        'node_capability_registry',
        'community_node_onboarding',
        'governance_consistency_checker',
        'openness_preservation_supervisor',
        'non_closure_certification_protocol',
        'metrics_history_recorder',
    ])

    def _dependency_presence(self) -> dict[str, bool]:
        ontology_dir = self.root / 'ontology'
        return {name: (ontology_dir / f'{name}.py').exists() for name in self.dependencies}

    def _load_context(self) -> dict[str, dict[str, Any]]:
        return {
            'q1_infrastructure': _safe_read_json(self.root / 'physical_ecology' / 'latest_physical_infrastructure_registry.json'),
            'q2_health': _safe_read_json(self.root / 'physical_ecology' / 'latest_hardware_health_monitor.json'),
            'q3_sensor_expansion': _safe_read_json(self.root / 'physical_sensors' / 'latest_distributed_sensor_expansion_manager.json'),
            'q7_interventions': _safe_read_json(self.root / 'physical_interventions' / 'latest_environmental_intervention_tracker.json'),
            'q8_feedback': _safe_read_json(self.root / 'physical_feedback' / 'latest_persistent_physical_feedback_loop.json'),
            'q9_multisite': _safe_read_json(self.root / 'physical_multisite' / 'latest_multi_site_physical_ecology.json'),
            'q10_resources': _safe_read_json(self.root / 'physical_resources' / 'latest_physical_resource_management.json'),
            'q11_continuity': _safe_read_json(self.root / 'physical_continuity' / 'latest_embodied_continuity_preservation.json'),
            'previous_plan': _safe_read_json(self.latest_path),
        }

    def _normalize_inputs(self, inputs: Mapping[str, Any] | None) -> dict[str, Any]:
        if isinstance(inputs, Mapping):
            return dict(inputs)
        return {}

    def _candidate_sites(self, inputs: dict[str, Any], context: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
        raw_sites = inputs.get('candidate_sites')
        if isinstance(raw_sites, list) and raw_sites:
            sites = []
            for index, item in enumerate(raw_sites, start=1):
                if isinstance(item, Mapping):
                    site = dict(item)
                else:
                    site = {'site_id': str(item)}
                site.setdefault('site_id', f'site_{index}')
                sites.append(site)
            return sites

        multisite = context.get('q9_multisite', {})
        known_count = int(_clamp(multisite.get('physical_site_count', 1), 0, 999)) or 1
        return [
            {
                'site_id': 'edge_sensor_site_A',
                'coverage_gain': 0.78,
                'resource_cost': 0.34,
                'continuity_gain': 0.72,
                'governance_risk': 0.10,
                'physical_accessibility': 0.83,
            },
            {
                'site_id': 'edge_actuator_site_B',
                'coverage_gain': 0.72,
                'resource_cost': 0.39,
                'continuity_gain': 0.76,
                'governance_risk': 0.12,
                'physical_accessibility': 0.80,
            },
            {
                'site_id': f'redundant_continuity_site_{known_count + 1}',
                'coverage_gain': 0.68,
                'resource_cost': 0.28,
                'continuity_gain': 0.84,
                'governance_risk': 0.08,
                'physical_accessibility': 0.74,
            },
        ]

    def _score_site(self, site: Mapping[str, Any], resource_resilience: float, continuity_score: float) -> dict[str, Any]:
        coverage_gain = _clamp(site.get('coverage_gain', 0.60))
        resource_cost = _clamp(site.get('resource_cost', 0.35))
        continuity_gain = _clamp(site.get('continuity_gain', 0.65))
        governance_risk = _clamp(site.get('governance_risk', 0.10))
        physical_accessibility = _clamp(site.get('physical_accessibility', 0.75))
        resource_fit = _clamp(resource_resilience * (1.0 - 0.65 * resource_cost))
        continuity_fit = _clamp(0.55 * continuity_score + 0.45 * continuity_gain)
        score = _clamp(
            0.28 * coverage_gain
            + 0.24 * resource_fit
            + 0.22 * continuity_fit
            + 0.16 * physical_accessibility
            + 0.10 * (1.0 - governance_risk)
        )
        return {
            'site_id': str(site.get('site_id', 'unnamed_site')),
            'coverage_gain': round(coverage_gain, 6),
            'resource_cost': round(resource_cost, 6),
            'continuity_gain': round(continuity_gain, 6),
            'governance_risk': round(governance_risk, 6),
            'physical_accessibility': round(physical_accessibility, 6),
            'resource_fit': round(resource_fit, 6),
            'continuity_fit': round(continuity_fit, 6),
            'priority_score': round(score, 6),
        }

    def _recommend_hardware(self, readiness: float, opportunity: float, inputs: dict[str, Any]) -> list[dict[str, Any]]:
        budget_mode = str(inputs.get('budget_mode', 'conservative'))
        base = [
            {
                'component': 'redundant_sensor_node',
                'purpose': 'increase perception continuity and site coverage',
                'priority': 'high' if opportunity >= 0.65 else 'medium',
                'governance_note': 'prefer reversible, low-power and replaceable hardware',
            },
            {
                'component': 'actuator_safety_interlock',
                'purpose': 'preserve physical action under safety supervision',
                'priority': 'high' if readiness >= 0.70 else 'medium',
                'governance_note': 'physical actuation must remain bounded and auditable',
            },
            {
                'component': 'external_storage_or_backup_node',
                'purpose': 'protect embodied state continuity during hardware change',
                'priority': 'medium',
                'governance_note': 'avoid local disk pressure until durable external storage is reliable',
            },
        ]
        if budget_mode == 'minimal':
            return base[:2]
        return base

    def _persist(self, result: dict[str, Any]) -> None:
        self.state_dir.mkdir(parents=True, exist_ok=True)
        payload = json.dumps(result, ensure_ascii=False, indent=2)
        self.latest_path.write_text(payload + chr(10), encoding='utf-8')
        with self.history_path.open('a', encoding='utf-8') as handle:
            handle.write(json.dumps(result, ensure_ascii=False) + chr(10))

    def step(self, inputs: Mapping[str, Any] | None = None, persist: bool = False) -> dict[str, Any]:
        inputs = self._normalize_inputs(inputs)
        timestamp = _utc_now()
        context = self._load_context()
        presence = self._dependency_presence()
        dependency_availability = _mean([1.0 if available else 0.0 for available in presence.values()])

        q1 = context.get('q1_infrastructure', {})
        q2 = context.get('q2_health', {})
        q3 = context.get('q3_sensor_expansion', {})
        q8 = context.get('q8_feedback', {})
        q9 = context.get('q9_multisite', {})
        q10 = context.get('q10_resources', {})
        q11 = context.get('q11_continuity', {})

        hardware_health = _clamp(inputs.get('hardware_health_index', q2.get('hardware_health_index', 0.82)))
        infrastructure_readiness = _clamp(inputs.get('infrastructure_readiness_index', q1.get('infrastructure_readiness_index', q1.get('physical_infrastructure_index', 0.78))))
        sensor_expansion_readiness = _clamp(inputs.get('sensor_expansion_readiness', q3.get('sensor_expansion_readiness', q3.get('sensor_network_readiness_index', 0.76))))
        feedback_stability = _clamp(inputs.get('feedback_stability_index', q8.get('feedback_stability_index', 0.78)))
        multi_site_readiness = _clamp(inputs.get('multi_site_readiness_index', q9.get('multi_site_readiness_index', 0.72)))
        resource_resilience = _clamp(inputs.get('resource_resilience_score', q10.get('resource_resilience_score', 0.74)))
        resource_pressure = _clamp(inputs.get('resource_pressure_index', q10.get('resource_pressure_index', 0.34)))
        continuity_score = _clamp(inputs.get('continuity_preservation_score', q11.get('continuity_preservation_score', 0.83)))

        planning_constraints = []
        if resource_pressure >= 0.75 or bool(inputs.get('resource_constrained', False)):
            planning_constraints.append('resource_constrained_expansion')
        if hardware_health < 0.55:
            planning_constraints.append('hardware_health_below_expansion_threshold')
        if continuity_score < 0.65:
            planning_constraints.append('continuity_reinforcement_required_before_expansion')
        if bool(inputs.get('unsafe_physical_context', False)):
            planning_constraints.append('physical_safety_review_required')

        deployment_readiness_score = _clamp(
            0.18 * infrastructure_readiness
            + 0.16 * hardware_health
            + 0.15 * sensor_expansion_readiness
            + 0.14 * multi_site_readiness
            + 0.15 * resource_resilience
            + 0.14 * continuity_score
            + 0.08 * dependency_availability
            - 0.10 * resource_pressure
        )

        candidates = self._candidate_sites(inputs, context)
        ranked_sites = sorted(
            [self._score_site(site, resource_resilience, continuity_score) for site in candidates],
            key=lambda item: item['priority_score'],
            reverse=True,
        )
        top_site_score = _clamp(ranked_sites[0]['priority_score'] if ranked_sites else 0.0)
        recommended_site = ranked_sites[0]['site_id'] if ranked_sites else None

        existing_sites = max(1, int(q9.get('physical_site_count', inputs.get('physical_site_count', 1)) or 1))
        existing_nodes = max(1, int(q1.get('physical_node_count', inputs.get('physical_node_count', 1)) or 1))
        coverage_gap = _clamp(1.0 - _clamp((existing_sites + existing_nodes) / 8.0))
        expansion_opportunity_index = _clamp(
            0.32 * coverage_gap
            + 0.26 * top_site_score
            + 0.18 * sensor_expansion_readiness
            + 0.14 * (1.0 - resource_pressure)
            + 0.10 * continuity_score
        )

        physical_ecology_growth_score = _clamp(
            0.38 * deployment_readiness_score
            + 0.34 * expansion_opportunity_index
            + 0.16 * multi_site_readiness
            + 0.12 * feedback_stability
        )

        expansion_authorized = (
            deployment_readiness_score >= 0.65
            and physical_ecology_growth_score >= 0.62
            and 'physical_safety_review_required' not in planning_constraints
        )

        deployment_phase = 'expand' if expansion_authorized else 'prepare_and_stabilize'
        if resource_pressure >= 0.85:
            deployment_phase = 'defer_expansion_resource_pressure'
        if continuity_score < 0.60:
            deployment_phase = 'reinforce_continuity_before_expansion'

        result = {
            'primitive': self.primitive,
            'refinement': 'Q12-R1',
            'timestamp_utc': timestamp,
            'success': True,
            'deployment_readiness_score': round(deployment_readiness_score, 6),
            'expansion_opportunity_index': round(expansion_opportunity_index, 6),
            'physical_ecology_growth_score': round(physical_ecology_growth_score, 6),
            'recommended_site': recommended_site,
            'ranked_sites': ranked_sites,
            'hardware_recommendations': self._recommend_hardware(deployment_readiness_score, expansion_opportunity_index, inputs),
            'deployment_phase': deployment_phase,
            'expansion_authorized': bool(expansion_authorized),
            'planning_constraints': planning_constraints,
            'diagnostics': {
                'dependency_availability': round(dependency_availability, 6),
                'hardware_health_index': round(hardware_health, 6),
                'infrastructure_readiness_index': round(infrastructure_readiness, 6),
                'sensor_expansion_readiness': round(sensor_expansion_readiness, 6),
                'feedback_stability_index': round(feedback_stability, 6),
                'multi_site_readiness_index': round(multi_site_readiness, 6),
                'resource_resilience_score': round(resource_resilience, 6),
                'resource_pressure_index': round(resource_pressure, 6),
                'continuity_preservation_score': round(continuity_score, 6),
                'candidate_site_count': _safe_len(ranked_sites),
            },
            'governance': {
                'functional_validation_only': True,
                'phenomenal_subjectivity_claimed': False,
                'non_closure_preserved': True,
                'human_review_required_for_real_actuation_or_purchase': True,
                'reversibility_required': True,
                'local_storage_quota_required_until_external_storage_reliable': True,
            },
            'dependencies': presence,
            'latest_path': str(self.latest_path),
            'history_path': str(self.history_path),
        }

        if persist:
            self._persist(result)

        return result

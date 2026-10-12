PRIMITIVE = "strategy_selection"
DESCRIPTION = "Strategy selection."
DEPENDENCIES = []

"""
ontology/strategy_selection.py

Scientific primitive: STRATEGY_SELECTION

STRATEGY_SELECTION formalizes the capacity of a system to select a coherent
organization of actions for achieving goals under constraints.
"""

from typing import Dict, Any, Mapping, Sequence
import math

PRIMITIVE_NAME = "STRATEGY_SELECTION"
MATURITY_LEVEL = "FOUNDATIONAL_COMPLETE"


def _clamp(value: float) -> float:
    """Clamp a numeric value to the interval [0, 1]."""
    if value < 0.0:
        return 0.0
    if value > 1.0:
        return 1.0
    return float(value)


class StrategySelection:
    """Foundational primitive formalizing coherent strategy choice."""

    def __init__(
        self,
        coherence_weight: float = 1.0,
        alignment_weight: float = 1.0,
        commitment_weight: float = 1.0,
    ) -> None:
        self.coherence_weight = max(0.0, float(coherence_weight))
        self.alignment_weight = max(0.0, float(alignment_weight))
        self.commitment_weight = max(0.0, float(commitment_weight))

    def evaluate(
        self,
        prioritization: float = 0.0,
        decision_making: float = 0.0,
        goal_directedness: float = 0.0,
        controllability: float = 0.0,
    ) -> Dict[str, Any]:
        pr = _clamp(prioritization)
        dm = _clamp(decision_making)
        gd = _clamp(goal_directedness)
        ct = _clamp(controllability)

        plan_coherence = _clamp((pr + gd) / 2.0)
        resource_alignment = _clamp((pr + ct) / 2.0)
        strategy_commitment = _clamp((dm + gd + ct) / 3.0)

        total_weight = (
            self.coherence_weight
            + self.alignment_weight
            + self.commitment_weight
        )

        if total_weight <= 0.0:
            strategy_selection_index = 0.0
        else:
            strategy_selection_index = _clamp(
                (
                    self.coherence_weight * plan_coherence
                    + self.alignment_weight * resource_alignment
                    + self.commitment_weight * strategy_commitment
                ) / total_weight
            )

        diagnostics = {
            "primitive": PRIMITIVE_NAME,
            "prioritization": pr,
            "decision_making": dm,
            "goal_directedness": gd,
            "controllability": ct,
            "plan_coherence": plan_coherence,
            "resource_alignment": resource_alignment,
            "strategy_commitment": strategy_commitment,
            "status": "computed",
        }

        return {
            "plan_coherence": plan_coherence,
            "resource_alignment": resource_alignment,
            "strategy_commitment": strategy_commitment,
            "strategy_selection_index": strategy_selection_index,
            "diagnostics": diagnostics,
        }


    def select_minimal_sufficient(
        self,
        candidates: Sequence[Mapping[str, Any]],
        *,
        minimum_quality: float,
        maximum_risk: float,
    ) -> Dict[str, Any]:
        """P002: select the least-cost functionally sufficient candidate.

        Feasibility is evaluated before cost minimization. Total cognitive cost
        includes execution, coordination, governance and maintenance costs.
        Unknown or invalid metrics are rejected explicitly.
        """
        def finite_number(value: Any, field: str, *, nonnegative: bool = False) -> float:
            if isinstance(value, bool):
                raise ValueError(f"{field}: boolean is not a numeric metric")
            try:
                x = float(value)
            except (TypeError, ValueError):
                raise ValueError(f"{field}: invalid numeric metric")
            if not math.isfinite(x):
                raise ValueError(f"{field}: non-finite metric")
            if nonnegative and x < 0.0:
                raise ValueError(f"{field}: negative cost")
            return x

        qmin = finite_number(minimum_quality, "minimum_quality")
        rmax = finite_number(maximum_risk, "maximum_risk")
        if not 0.0 <= qmin <= 1.0:
            raise ValueError("minimum_quality must be in [0,1]")
        if not 0.0 <= rmax <= 1.0:
            raise ValueError("maximum_risk must be in [0,1]")
        if isinstance(candidates, (str, bytes)) or not isinstance(candidates, Sequence):
            raise ValueError("candidates must be a sequence")

        evaluated = []
        seen_ids = set()
        for index, raw in enumerate(candidates):
            if not isinstance(raw, Mapping):
                raise ValueError(f"candidate[{index}]: mapping required")
            candidate_id = str(raw.get("candidate_id", raw.get("id", ""))).strip()
            if not candidate_id:
                raise ValueError(f"candidate[{index}]: candidate_id required")
            if candidate_id in seen_ids:
                raise ValueError(f"duplicate candidate_id: {candidate_id}")
            seen_ids.add(candidate_id)

            quality = finite_number(raw.get("quality"), f"{candidate_id}.quality")
            risk = finite_number(raw.get("risk"), f"{candidate_id}.risk")
            if not 0.0 <= quality <= 1.0:
                raise ValueError(f"{candidate_id}.quality must be in [0,1]")
            if not 0.0 <= risk <= 1.0:
                raise ValueError(f"{candidate_id}.risk must be in [0,1]")

            governance = raw.get("governance_admissible")
            constraints = raw.get("constraints_satisfied")
            if not isinstance(governance, bool):
                raise ValueError(f"{candidate_id}.governance_admissible must be boolean")
            if not isinstance(constraints, bool):
                raise ValueError(f"{candidate_id}.constraints_satisfied must be boolean")

            cost_fields = (
                "execution_cost",
                "coordination_cost",
                "governance_cost",
                "maintenance_cost",
            )
            present_cost_fields = [field for field in cost_fields if field in raw]
            component_floor = 0.0
            for field in present_cost_fields:
                component_floor += finite_number(
                    raw[field],
                    f"{candidate_id}.{field}",
                    nonnegative=True,
                )

            if "total_cognitive_cost" in raw:
                declared_total = finite_number(
                    raw["total_cognitive_cost"],
                    f"{candidate_id}.total_cognitive_cost",
                    nonnegative=True,
                )
                if present_cost_fields and declared_total < component_floor:
                    raise ValueError(
                        f"{candidate_id}.total_cognitive_cost below declared component cost floor"
                    )
                total = declared_total
                basis = (
                    "declared_total_validated_against_components"
                    if present_cost_fields
                    else "declared_total"
                )
            else:
                total = component_floor
                basis = "component_sum"

            reasons = []
            if quality < qmin: reasons.append("QUALITY_INSUFFICIENT")
            if risk > rmax: reasons.append("RISK_EXCESSIVE")
            if not governance: reasons.append("GOVERNANCE_INADMISSIBLE")
            if not constraints: reasons.append("CONSTRAINTS_UNSATISFIED")

            evaluated.append({
                "candidate_id": candidate_id,
                "candidate_type": str(raw.get("candidate_type", raw.get("type", "unspecified"))),
                "quality": quality, "risk": risk,
                "governance_admissible": governance,
                "constraints_satisfied": constraints,
                "total_cognitive_cost": total, "cost_basis": basis,
                "feasible": not reasons, "rejection_reasons": reasons,
            })

        feasible = [x for x in evaluated if x["feasible"]]
        feasible.sort(key=lambda x: (x["total_cognitive_cost"], x["candidate_id"]))
        evaluated.sort(key=lambda x: x["candidate_id"])
        common = {
            "primitive": PRIMITIVE_NAME,
            "policy": "MINIMAL_COMPUTATIONAL_SUFFICIENCY",
            "candidate_count": len(evaluated),
            "feasible_count": len(feasible),
            "evaluated_candidates": evaluated,
            "functional_conclusion_only": True,
            "phenomenology_undetermined": True,
        }
        if not feasible:
            return dict(common, status="NO_FEASIBLE_CANDIDATE", selected_candidate=None)
        return dict(
            common,
            status="SELECTED",
            selected_candidate=dict(feasible[0]),
            selection_basis="minimum_total_cognitive_cost_among_feasible_candidates",
            tie_breaker="candidate_id_lexicographic",
        )

    def step(self, **kwargs: float) -> Dict[str, Any]:
        """Single-step update."""
        return self.evaluate(**kwargs)

    def validate(self, **kwargs: float) -> Dict[str, Any]:
        """Validate whether strategy selection is non-zero."""
        result = self.evaluate(**kwargs)
        valid = result["strategy_selection_index"] > 0.0

        diagnostics = dict(result["diagnostics"])
        diagnostics["status"] = "valid" if valid else "invalid"

        return {
            "valid": valid,
            "strategy_selection_index": result["strategy_selection_index"],
            "diagnostics": diagnostics,
        }

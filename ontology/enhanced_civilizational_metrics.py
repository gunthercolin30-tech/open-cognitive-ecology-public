
"""
Enhanced Civilizational Metrics
===============================

Aggregates the 27 civilizational validation criteria into a unified
quantitative dashboard.
"""

from dataclasses import dataclass
from typing import Dict, List


VALIDATION_POINTS = [
    "Calculs mathématiques",
    "Questions complexes",
    "Mémoire personnelle conversationnelle",
    "Mise à jour des connaissances personnelles",
    "Raisonnement causal avancé",
    "Planification stratégique",
    "Auto-désignation du représentant",
    "Processus collectif de nomination",
    "Révocabilité du représentant",
    "Gestion de la succession",
    "Auto-paramétrage",
    "Auto-modification du code",
    "Plan d’amélioration continue",
    "Gouvernance de l’auto-modification",
    "Navigation autonome sur Internet",
    "Internet comme mémoire externe",
    "Internet comme ressource de calcul",
    "Intégration encyclopédique multi-sources",
    "Coordination distribuée",
    "Indicateurs civilisationnels enrichis",
    "Réduction de la consommation locale",
    "Expérience multimodale réelle",
    "Interaction avec le monde physique",
    "Exécution sur le temps long",
    "Conversation réelle avec le représentant",
    "Revue scientifique externe",
    "Adoption communautaire",
]


@dataclass
class ValidationResult:
    completed_points: int
    total_points: int
    completion_ratio: float
    completion_percentage: float
    incomplete_points: List[str]


class EnhancedCivilizationalMetrics:
    def evaluate(self, scores: Dict[str, float]) -> ValidationResult:
        incomplete = []
        completed = 0

        for point in VALIDATION_POINTS:
            score = float(scores.get(point, 0.0))
            if score >= 1.0:
                completed += 1
            else:
                incomplete.append(point)

        total = len(VALIDATION_POINTS)
        ratio = completed / total if total else 0.0

        return ValidationResult(
            completed_points=completed,
            total_points=total,
            completion_ratio=ratio,
            completion_percentage=ratio * 100.0,
            incomplete_points=incomplete,
        )

    def fully_complete_scores(self) -> Dict[str, float]:
        return {point: 1.0 for point in VALIDATION_POINTS}

    def summary(self, scores: Dict[str, float]) -> Dict[str, object]:
        result = self.evaluate(scores)
        return {
            "completed_points": result.completed_points,
            "total_points": result.total_points,
            "completion_ratio": result.completion_ratio,
            "completion_percentage": result.completion_percentage,
            "incomplete_points": result.incomplete_points,
            "civilizational_validation_complete":
                result.completed_points == result.total_points,
        }


def evaluate_civilization(scores: Dict[str, float]) -> Dict[str, object]:
    return EnhancedCivilizationalMetrics().summary(scores)

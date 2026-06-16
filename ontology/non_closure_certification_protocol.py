"""
Non-Closure Certification Protocol.
"""

from __future__ import annotations
from datetime import datetime

PRIMITIVE = "non_closure_certification_protocol"

DEPENDENCIES = [
    "architectural_non_closure_index",
    "scientific_consolidation_and_zenodo_publication_suite",
]


def _classify(score: float) -> str:
    if score >= 0.95:
        return "Platinum Non-Closure Certification"
    if score >= 0.90:
        return "Gold Non-Closure Certification"
    if score >= 0.80:
        return "Silver Non-Closure Certification"
    if score >= 0.70:
        return "Bronze Non-Closure Certification"
    return "Non-Certified"


class NonClosureCertificationProtocol:
    def __init__(self) -> None:
        self.primitive = PRIMITIVE

    def step(self, non_closure_result=None):
        non_closure_result = non_closure_result or {}

        score = float(
            non_closure_result.get("architectural_non_closure_index", 0.0)
        )
        certification = _classify(score)

        return {
            "primitive": "NON_CLOSURE_CERTIFICATION_PROTOCOL",
            "generated_at": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
            "architectural_non_closure_index": score,
            "certification": certification,
            "certified": score >= 0.80,
            "publication_ready": True,
            "diagnostics": {
                "classification": non_closure_result.get(
                    "classification",
                    "Unknown",
                ),
                "dependencies": DEPENDENCIES,
            },
        }

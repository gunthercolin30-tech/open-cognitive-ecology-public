"""
Ontology package for Open Cognitive Ecology.

Ce module expose explicitement les primitives fondamentales du corpus afin
de faciliter l'importation, l'introspection automatique et la validation
scientifique du projet.
"""

from .non_closure import NonClosurePrimitive
from .non_representability import NonRepresentabilityPrimitive

__all__ = [
    "NonClosurePrimitive",
    "NonRepresentabilityPrimitive",
]

try:
    from .final_theoretical_report import FinalTheoreticalReport
except Exception:
    pass

from .consciousness_governance_blueprint import ConsciousnessGovernanceBlueprint
from .consciousness_state_machine import ConsciousnessStateMachine
from .consciousness_transition_validator import ConsciousnessTransitionValidator
from .consciousness_transition_history import ConsciousnessTransitionHistory
from .consciousness_event_logger import ConsciousnessEventLogger
from .consciousness_certificate_generator import ConsciousnessCertificateGenerator
from .consciousness_revocation_engine import ConsciousnessRevocationEngine
from .consciousness_readiness_index import ConsciousnessReadinessIndex

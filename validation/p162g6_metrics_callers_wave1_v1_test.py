import ast
from pathlib import Path
ROOT=Path.home()/"open-cognitive-ecology"
FILES=['ontology/controlled_evolution_orchestrator.py', 'ontology/embodied_coupling_dashboard_exporter.py', 'ontology/embodied_coupling_scientific_certification.py', 'ontology/environmental_grounding_longitudinal_observatory.py', 'ontology/longitudinal_autonomous_conversation_validation.py', 'ontology/civilizational_regime_dashboard.py', 'ontology/paradigm_shift_detection_engine.py', 'ontology/scientific_paradigm_certification.py']
def test_wave1_compiles_and_transports_without_minting():
    for rel in FILES:
        src=(ROOT/rel).read_text(encoding="utf-8")
        ast.parse(src)
        assert "metrics_effect_context" in src
        assert "effect_context=metrics_effect_context" in src
        assert "ScopedHandleBroker(" not in src
        assert "ExecutionClaimManager(" not in src
        assert "ExecutionLeaseIssuer(" not in src
def test_wave1_removes_context_from_business_input_before_processing():
    for rel in FILES:
        src=(ROOT/rel).read_text(encoding="utf-8")
        assert '.pop("metrics_effect_context", None)' in src

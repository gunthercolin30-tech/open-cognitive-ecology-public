import ast
from pathlib import Path
ROOT=Path.home()/"open-cognitive-ecology"
FILES=['ontology/autonomous_external_collaboration_runner.py', 'ontology/civilizational_attention_allocator.py', 'ontology/continuous_long_duration_runtime_executor.py', 'ontology/external_collaboration_execution_layer.py', 'ontology/external_response_parser.py', 'ontology/multimodal_perception_engine.py', 'ontology/openrouter_autonomous_provider_adapter.py', 'ontology/terminal_conversation_runtime.py']
def test_wave2_compiles_and_transports_without_minting():
    for rel in FILES:
        src=(ROOT/rel).read_text(encoding="utf-8"); ast.parse(src)
        assert "metrics_effect_context" in src
        assert "effect_context=metrics_effect_context" in src
        assert "ScopedHandleBroker(" not in src
        assert "ExecutionClaimManager(" not in src
        assert "ExecutionLeaseIssuer(" not in src
def test_payload_style_callers_strip_authority_from_business_payloads():
    for rel in ["ontology/autonomous_external_collaboration_runner.py","ontology/external_collaboration_execution_layer.py","ontology/multimodal_perception_engine.py","ontology/openrouter_autonomous_provider_adapter.py","ontology/terminal_conversation_runtime.py"]:
        assert '.pop("metrics_effect_context", None)' in (ROOT/rel).read_text(encoding="utf-8")
def test_parser_propagates_context_through_both_entry_paths():
    src=(ROOT/"ontology/external_response_parser.py").read_text(encoding="utf-8")
    assert 'kwargs.pop("metrics_effect_context", None)' in src
    assert "parse_queue_answer(query_record, persist=persist, metrics_effect_context=metrics_effect_context)" in src
    assert 'parse_response(response_text or "", persist=persist, metrics_effect_context=metrics_effect_context, **kwargs)' in src
def test_explicit_parameter_callers_remain_optional():
    assert "metrics_effect_context: Any = None" in (ROOT/"ontology/civilizational_attention_allocator.py").read_text(encoding="utf-8")
    assert "metrics_effect_context: Any = None" in (ROOT/"ontology/continuous_long_duration_runtime_executor.py").read_text(encoding="utf-8")

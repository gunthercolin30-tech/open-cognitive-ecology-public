import json
from pathlib import Path
from tempfile import TemporaryDirectory
from ontology.acee_governed_code_generation_gate import AceeGovernedCodeGenerationGate
from acee5_hardening_test_support import valid_context
with TemporaryDirectory() as td:
    root=Path(td); gate=AceeGovernedCodeGenerationGate(root=root)
    a=gate.step(valid_context(root,'p1'),persist=True); b=gate.step(valid_context(root,'p2'),persist=True)
    assert b['previous_decision_hash']==a['result_hash'] and b['decision_index']==1
    _, history, _=gate._paths(); records=[json.loads(x) for x in history.read_text().splitlines()]
    assert records[1]['previous_decision_hash']==records[0]['result_hash']
print('ACEE5_HASH_CHAIN_INTEGRITY_OK')

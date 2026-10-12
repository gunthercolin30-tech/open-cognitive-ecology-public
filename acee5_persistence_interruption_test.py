from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
from ontology.acee_governed_code_generation_gate import AceeGovernedCodeGenerationGate
from acee5_hardening_test_support import valid_context
with TemporaryDirectory() as td:
    root=Path(td); gate=AceeGovernedCodeGenerationGate(root=root)
    try:
        with patch('ontology.acee_governed_code_generation_gate.os.replace', side_effect=RuntimeError('interrupt')):
            gate.step(valid_context(root),persist=True)
    except RuntimeError: pass
    latest, history, _=gate._paths(); assert history.is_file() and not latest.exists() and not list(latest.parent.glob('*.tmp'))
    r=gate.step(valid_context(root,'p2'),persist=True); assert r['decision_index']==1
print('ACEE5_PERSISTENCE_INTERRUPTION_OK')

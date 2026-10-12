import json
from pathlib import Path
from tempfile import TemporaryDirectory
from ontology.acee_governed_code_generation_gate import AceeGovernedCodeGenerationGate
from acee5_hardening_test_support import valid_context
with TemporaryDirectory() as td:
    root=Path(td); gate=AceeGovernedCodeGenerationGate(root=root)
    gate.step(valid_context(root,'p1'), persist=True); gate.step(valid_context(root,'p2'), persist=True)
    _, history, _=gate._paths(); lines=history.read_text().splitlines(); record=json.loads(lines[0]); record['status']='TAMPERED'; lines[0]=json.dumps(record); history.write_text('\n'.join(lines)+'\n')
    r=gate.step(valid_context(root,'p3'), persist=False)
    assert not r['installation_authorized'] and 'history_corrupted' in r['blocking_reasons'] and r['history_corrupted']
print('ACEE5_HISTORY_CORRUPTION_OK')

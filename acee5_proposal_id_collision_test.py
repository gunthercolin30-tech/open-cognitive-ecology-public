from pathlib import Path
from tempfile import TemporaryDirectory
from ontology.acee_governed_code_generation_gate import AceeGovernedCodeGenerationGate
from acee5_hardening_test_support import valid_context
with TemporaryDirectory() as td:
    root=Path(td); gate=AceeGovernedCodeGenerationGate(root=root)
    assert gate.step(valid_context(root), persist=True)['installation_authorized']
    r=gate.step(valid_context(root, candidate_hash='e'*64), persist=True)
    assert not r['installation_authorized'] and 'proposal_id_collision' in r['blocking_reasons']
print('ACEE5_PROPOSAL_ID_COLLISION_OK')

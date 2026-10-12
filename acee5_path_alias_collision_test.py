from pathlib import Path
from tempfile import TemporaryDirectory
from ontology.acee_governed_code_generation_gate import AceeGovernedCodeGenerationGate
from acee5_hardening_test_support import valid_context
with TemporaryDirectory() as td:
    root=Path(td); (root/'ontology').mkdir(); c=valid_context(root); c['candidate']['target_path']='ontology/../ontology/sample_candidate.py'; c['backup_evidence']['target_path']='ontology/sample_candidate.py'
    r=AceeGovernedCodeGenerationGate(root=root).step(c)
    assert r['installation_authorized'] and r['installation_manifest']['target_path']=='ontology/sample_candidate.py'
print('ACEE5_PATH_ALIAS_COLLISION_OK')

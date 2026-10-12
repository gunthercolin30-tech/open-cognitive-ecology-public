from pathlib import Path
from tempfile import TemporaryDirectory
from ontology.acee_governed_code_generation_gate import AceeGovernedCodeGenerationGate
from acee5_hardening_test_support import valid_context
with TemporaryDirectory() as td, TemporaryDirectory() as outside:
    root=Path(td); (root/'ontology').mkdir(); (root/'ontology'/'escape').symlink_to(Path(outside), target_is_directory=True)
    c=valid_context(root); c['candidate']['target_path']='ontology/escape/candidate.py'
    r=AceeGovernedCodeGenerationGate(root=root).step(c)
    assert not r['installation_authorized'] and 'candidate_path_outside_root' in r['blocking_reasons']
print('ACEE5_SYMLINK_ESCAPE_OK')

from pathlib import Path
from tempfile import TemporaryDirectory
from ontology.acee_governed_code_generation_gate import AceeGovernedCodeGenerationGate
from acee5_hardening_test_support import valid_context, sha_file
with TemporaryDirectory() as td:
    root=Path(td); (root/'ontology').mkdir(); backup=root/'ontology/sample_candidate.py.bak'; backup.write_text('safe')
    c=valid_context(root); c['backup_evidence']['sha256']=sha_file(backup); backup.write_text('swapped')
    r=AceeGovernedCodeGenerationGate(root=root).step(c)
    assert not r['installation_authorized'] and 'backup_hash_mismatch' in r['blocking_reasons']
print('ACEE5_BACKUP_SWAP_RACE_OK')

import tempfile
from pathlib import Path
from unittest.mock import patch
import ontology.acee_governed_code_generation_gate as mod
from ontology.acee_governed_code_generation_gate import AceeGovernedCodeGenerationGate
from acee5_hardening_test_support import valid_context
with tempfile.TemporaryDirectory() as tmp:
 root=Path(tmp);(root/'ontology').mkdir();b=root/'ontology'/'sample_candidate.py.bak';b.write_text('x');c=valid_context(root);c['backup_evidence']['sha256']='0'*64;real=mod._file_sha
 def denied(p):
  if p==b.resolve(): raise PermissionError('denied')
  return real(p)
 with patch.object(mod,'_file_sha',side_effect=denied): r=AceeGovernedCodeGenerationGate(root=root).step(c)
 assert not r['installation_authorized'] and 'backup_unreadable' in r['blocking_reasons']
print('ACEE5_UNREADABLE_ARTIFACT_OK')

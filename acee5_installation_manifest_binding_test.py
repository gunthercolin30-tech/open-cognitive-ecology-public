import copy,tempfile
from pathlib import Path
from ontology.acee_governed_code_generation_gate import AceeGovernedCodeGenerationGate,_sha
from acee5_hardening_test_support import valid_context
def verify(m): return m['manifest_hash']==_sha({k:v for k,v in m.items() if k!='manifest_hash'})
with tempfile.TemporaryDirectory() as tmp:
 root=Path(tmp);(root/'ontology').mkdir();r=AceeGovernedCodeGenerationGate(root=root).step(valid_context(root));m=r['installation_manifest'];assert verify(m)
 for k in ('proposal_id','candidate_content_sha256','target_path','backup_path','refiner_sha256','validation_report_sha256','decision_index','public_schema_version'):
  x=copy.deepcopy(m);x[k]=str(x[k])+'x';assert not verify(x)
print('ACEE5_INSTALLATION_MANIFEST_BINDING_OK')

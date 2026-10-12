import tempfile
from pathlib import Path
from ontology.acee_governed_code_generation_gate import AceeGovernedCodeGenerationGate
from acee5_hardening_test_support import valid_context
REQ={'primitive','public_schema_version','timestamp_utc','proposal_id','status','generation_governed','installation_authorized','authorization_scope','preconditions_complete','blocking_reasons','warnings','installation_manifest','previous_decision_hash','history_corrupted','functional_conclusion_only','phenomenology_undetermined','evidence_hash','result_hash'}
with tempfile.TemporaryDirectory() as tmp:
 root=Path(tmp);(root/'ontology').mkdir();r=AceeGovernedCodeGenerationGate(root=root).step(valid_context(root));assert REQ<=set(r) and r['installation_authorized'];m=r['installation_manifest'];assert m['public_schema_version']==r['public_schema_version'] and m['decision_index']==r['decision_index'] and len(m['manifest_hash'])==64
print('ACEE5_SCHEMA_BACKWARD_COMPATIBILITY_OK')

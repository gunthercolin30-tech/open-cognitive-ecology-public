from datetime import datetime, timedelta, timezone
from pathlib import Path
from tempfile import TemporaryDirectory
from ontology.acee_governed_code_generation_gate import AceeGovernedCodeGenerationGate
from acee5_hardening_test_support import valid_context
with TemporaryDirectory() as td:
    root=Path(td); c=valid_context(root)
    c['timestamp_utc']=datetime.now(timezone.utc).isoformat().replace('+00:00','Z')
    c['validation_evidence']['timestamp_utc']=(datetime.now(timezone.utc)-timedelta(days=2)).isoformat().replace('+00:00','Z')
    r=AceeGovernedCodeGenerationGate(root=root).step(c)
    assert not r['installation_authorized'] and {'validation_predates_proposal','validation_stale'} <= set(r['blocking_reasons'])
print('ACEE5_STALE_VALIDATION_REPLAY_OK')

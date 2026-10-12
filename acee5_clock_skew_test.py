import copy,tempfile
from datetime import datetime,timedelta,timezone
from pathlib import Path
from unittest.mock import patch
import ontology.acee_governed_code_generation_gate as mod
from ontology.acee_governed_code_generation_gate import AceeGovernedCodeGenerationGate
from acee5_hardening_test_support import valid_context
iso=lambda d:d.isoformat().replace('+00:00','Z');fixed=datetime(2026,7,15,8,0,tzinfo=timezone.utc)
class FD(datetime):
 @classmethod
 def now(cls,tz=None): return fixed if tz else fixed.replace(tzinfo=None)
with tempfile.TemporaryDirectory() as tmp:
 root=Path(tmp);(root/'ontology').mkdir();g=AceeGovernedCodeGenerationGate(root=root);base=valid_context(root);base['timestamp_utc']=iso(fixed-timedelta(days=2))
 with patch.object(mod,'datetime',FD):
  c=copy.deepcopy(base);c['validation_evidence']['timestamp_utc']=iso(fixed-timedelta(seconds=mod.MAX_VALIDATION_AGE_SECONDS));assert g.step(c)['installation_authorized']
  c=copy.deepcopy(base);c['validation_evidence']['timestamp_utc']=iso(fixed-timedelta(seconds=mod.MAX_VALIDATION_AGE_SECONDS,microseconds=1));assert 'validation_stale' in g.step(c)['blocking_reasons']
  c=copy.deepcopy(base);c['validation_evidence']['timestamp_utc']='2026-07-15T08:00:00';assert 'validation_timestamp_invalid' in g.step(c)['blocking_reasons']
  c=copy.deepcopy(base);c['timestamp_utc']='bad';assert 'proposal_timestamp_invalid' in g.step(c)['blocking_reasons']
print('ACEE5_CLOCK_SKEW_OK')

import tempfile
from pathlib import Path
from acee6_k6_campaign_support import FAST_DISTRIBUTION
from acee6_k6_longitudinal_runner import PlannedInterruption,run_campaign
with tempfile.TemporaryDirectory() as t:
 w=Path(t)
 try:run_campaign(workspace=w,distribution=FAST_DISTRIBUTION,segment_size=10,interrupt_at=7,interrupt_phase='after_checkpoint')
 except PlannedInterruption:pass
 o=run_campaign(workspace=w,distribution=FAST_DISTRIBUTION,segment_size=10);assert o['verification']['valid'],o['verification'];assert o['report']['transaction_count']==20;assert [r['index'] for r in o['report']['records']]==list(range(1,21))
print('ACEE6_K6_RESTART_OK')

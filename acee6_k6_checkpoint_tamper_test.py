import json,tempfile
from pathlib import Path
from acee6_k6_campaign_support import FAST_DISTRIBUTION
from acee6_k6_checkpoint_manager import CheckpointError
from acee6_k6_longitudinal_runner import PlannedInterruption,run_campaign
with tempfile.TemporaryDirectory() as t:
 w=Path(t)
 try:run_campaign(workspace=w,distribution=FAST_DISTRIBUTION,segment_size=10,interrupt_at=5,interrupt_phase='after_checkpoint')
 except PlannedInterruption:pass
 p=w/'checkpoint.json';d=json.loads(p.read_text());d['next_index']=4;p.write_text(json.dumps(d),encoding='utf-8')
 try:run_campaign(workspace=w,distribution=FAST_DISTRIBUTION,segment_size=10);raise AssertionError('tamper accepted')
 except CheckpointError:pass
print('ACEE6_K6_CHECKPOINT_TAMPER_OK')

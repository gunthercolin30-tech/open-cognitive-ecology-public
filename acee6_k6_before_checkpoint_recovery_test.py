import tempfile
from pathlib import Path
from acee6_k6_campaign_support import FAST_DISTRIBUTION
from acee6_k6_checkpoint_manager import CheckpointError
from acee6_k6_longitudinal_runner import PlannedInterruption,run_campaign
with tempfile.TemporaryDirectory() as t:
 w=Path(t)
 try:run_campaign(workspace=w,distribution=FAST_DISTRIBUTION,segment_size=10,interrupt_at=7,interrupt_phase='before_checkpoint')
 except PlannedInterruption:pass
 try:run_campaign(workspace=w,distribution=FAST_DISTRIBUTION,segment_size=10);raise AssertionError('uncheckpointed record accepted')
 except CheckpointError:pass
print('ACEE6_K6_BEFORE_CHECKPOINT_FAIL_CLOSED_OK')

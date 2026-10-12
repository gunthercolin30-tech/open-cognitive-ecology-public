import tempfile
from pathlib import Path
from acee6_k6_checkpoint_manager import CheckpointError,CheckpointManager
from acee6_k6_campaign_support import GENESIS
with tempfile.TemporaryDirectory() as t:
 m=CheckpointManager(Path(t));p=m.build(campaign_id='c',seed=1,target_sha256='a'*64,segment_size=10,total_transactions=20,next_index=3,scenario_counts={'committed':3},committed_count=3,last_transaction_hash='b'*64,last_segment_hash=GENESIS,checkpoint_generation=3);m.write(p);assert m.load()==p
 m.path.write_text('{"broken":',encoding='utf-8')
 try:m.load();raise AssertionError('truncation accepted')
 except CheckpointError:pass
print('ACEE6_K6_CHECKPOINT_OK')

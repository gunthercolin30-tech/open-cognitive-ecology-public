import tempfile,shutil
from pathlib import Path
from acee6_k7_longitudinal_runner import _run_triplet
from acee6_k6_campaign_support import FAST_DISTRIBUTION
p=Path(tempfile.mkdtemp(prefix='acee6_k7_cleanup_'));o=_run_triplet(root=p,distribution=FAST_DISTRIBUTION,segment_size=10,seed_value=6006,interrupt_at=7);assert o['verification']['valid'];shutil.rmtree(p);assert not p.exists();print('ACEE6_K7_CLEANUP_OK')

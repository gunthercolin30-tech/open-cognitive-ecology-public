import tempfile
from pathlib import Path
from acee6_k6_longitudinal_runner import run_campaign
from acee6_k6_campaign_support import FAST_DISTRIBUTION
parent=Path(tempfile.mkdtemp(prefix='acee6_k6_cleanup_parent_'));work=parent/'work';o=run_campaign(workspace=work,distribution=FAST_DISTRIBUTION,segment_size=10);assert o['verification']['valid'];import shutil;shutil.rmtree(parent);assert not parent.exists();print('ACEE6_K6_CLEANUP_OK')

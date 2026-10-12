from __future__ import annotations
import json
from pathlib import Path
from typing import Any, Mapping
from acee6_k6_campaign_support import GENESIS,atomic_json_write,sha

class CheckpointError(RuntimeError):pass

class CheckpointManager:
    def __init__(self,root:Path):
        self.root=Path(root);self.path=self.root/'checkpoint.json'
    def build(self,*,campaign_id:str,seed:int,target_sha256:str,segment_size:int,total_transactions:int,next_index:int,scenario_counts:Mapping[str,int],committed_count:int,last_transaction_hash:str,last_segment_hash:str,checkpoint_generation:int)->dict[str,Any]:
        body={'schema_version':'1.0.0','campaign_id':campaign_id,'seed':int(seed),'target_sha256':target_sha256,'segment_size':int(segment_size),'total_transactions':int(total_transactions),'next_index':int(next_index),'completed_transaction_count':int(next_index),'scenario_counts':dict(sorted(scenario_counts.items())),'committed_count':int(committed_count),'unexpected_outcome_count':0,'last_transaction_hash':last_transaction_hash,'last_segment_hash':last_segment_hash,'checkpoint_generation':int(checkpoint_generation)}
        body['checkpoint_hash']=sha(body);return body
    def write(self,payload:Mapping[str,Any])->None:atomic_json_write(self.path,payload)
    def load(self)->dict[str,Any]|None:
        if not self.path.exists():return None
        try:data=json.loads(self.path.read_text(encoding='utf-8'))
        except Exception as exc:raise CheckpointError(f'checkpoint_unreadable:{type(exc).__name__}') from exc
        expected=sha({k:v for k,v in data.items() if k!='checkpoint_hash'})
        if data.get('checkpoint_hash')!=expected:raise CheckpointError('checkpoint_hash_invalid')
        return data

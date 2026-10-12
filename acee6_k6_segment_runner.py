from __future__ import annotations
from pathlib import Path
from typing import Any, Mapping
from acee6_k6_campaign_support import GENESIS,atomic_json_write,sha

class SegmentRunner:
    def __init__(self,root:Path):self.root=Path(root);(self.root/'segments').mkdir(parents=True,exist_ok=True)
    def path(self,segment_id:int)->Path:return self.root/'segments'/f'segment_{segment_id:04d}.json'
    def write(self,*,campaign_id:str,segment_id:int,start_index:int,end_index:int,records:list[Mapping[str,Any]],previous_segment_hash:str,checkpoint_hash:str)->dict[str,Any]:
        body={'schema_version':'1.0.0','campaign_id':campaign_id,'segment_id':int(segment_id),'start_index':int(start_index),'end_index':int(end_index),'transaction_count':len(records),'previous_segment_hash':previous_segment_hash,'transaction_hashes':[r['transaction_hash'] for r in records],'checkpoint_hash':checkpoint_hash}
        body['segment_hash']=sha(body);body['report_hash']=sha(body);atomic_json_write(self.path(segment_id),body);return body

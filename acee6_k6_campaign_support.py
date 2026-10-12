from __future__ import annotations
import hashlib, json, os, tempfile
from pathlib import Path
from typing import Any, Mapping

SCIENTIFIC_DISTRIBUTION={'committed':400,'rejected':200,'rolled_back':150,'quarantined':100,'replay':50,'recovery':50,'collision':50}
FAST_DISTRIBUTION={'committed':8,'rejected':4,'rolled_back':3,'quarantined':2,'replay':1,'recovery':1,'collision':1}
INVARIANTS={'consciousness_proven':False,'subjectivity_proven':False,'qualia_proven':False,'phenomenology_proven':False,'functional_conclusion_only':True,'phenomenology_undetermined':True}
GENESIS='0'*64

def canonical_bytes(value:Any)->bytes:
    return json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode('utf-8')

def sha(value:Any)->str:return hashlib.sha256(canonical_bytes(value)).hexdigest()

def file_sha(path:Path)->str:
    d=hashlib.sha256()
    with Path(path).open('rb') as stream:
        for chunk in iter(lambda:stream.read(1024*1024),b''):d.update(chunk)
    return d.hexdigest()

def atomic_json_write(path:Path,payload:Mapping[str,Any])->None:
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    fd,tmp=tempfile.mkstemp(prefix=f'.{path.name}.',suffix='.tmp',dir=str(path.parent))
    tmp_path=Path(tmp)
    try:
        with os.fdopen(fd,'w',encoding='utf-8') as stream:
            json.dump(payload,stream,indent=2,sort_keys=True,ensure_ascii=False,allow_nan=False);stream.write('\n');stream.flush();os.fsync(stream.fileno())
        os.replace(str(tmp_path),str(path))
        try:
            dfd=os.open(str(path.parent),os.O_RDONLY);os.fsync(dfd);os.close(dfd)
        except OSError:pass
    finally:
        if tmp_path.exists():tmp_path.unlink()

def deterministic_schedule(distribution:Mapping[str,int])->list[str]:
    schedule=[]
    for kind,count in distribution.items():schedule.extend([kind]*int(count))
    return schedule

def deterministic_record(record:Mapping[str,Any])->dict[str,Any]:
    return {k:record.get(k) for k in ('index','kind','expected_state','observed_state','ok','input_hash','result_hash')}

def transaction_link(previous_hash:str,record:Mapping[str,Any])->str:
    return sha({'previous_transaction_hash':previous_hash,'record':deterministic_record(record)})

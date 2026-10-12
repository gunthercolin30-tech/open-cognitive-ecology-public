from __future__ import annotations
import hashlib,json,os,tempfile,zipfile
from pathlib import Path
from typing import Any,Mapping
ROOT=Path.home()/"open-cognitive-ecology"
EVIDENCE=ROOT/"acee6_k_evidence"
REPORT_PATH=EVIDENCE/"acee6_k8_global_certification_report.json"
MANIFEST_PATH=EVIDENCE/"sha256_manifest.txt"
BUNDLE_PATH=EVIDENCE/"acee6_k_certification_bundle.zip"
ZERO_TIME=(1980,1,1,0,0,0)
def canonical_bytes(value:Any)->bytes:return json.dumps(value,sort_keys=True,separators=(",",":"),ensure_ascii=False,allow_nan=False).encode()
def sha(value:Any)->str:return hashlib.sha256(value if isinstance(value,bytes) else canonical_bytes(value)).hexdigest()
def file_sha(path:Path)->str:
 h=hashlib.sha256()
 with path.open('rb') as f:
  for chunk in iter(lambda:f.read(1024*1024),b''):h.update(chunk)
 return h.hexdigest()
def atomic_bytes(path:Path,data:bytes)->None:
 path.parent.mkdir(parents=True,exist_ok=True)
 fd,tmp=tempfile.mkstemp(prefix=f'.{path.name}.',dir=str(path.parent))
 try:
  with os.fdopen(fd,'wb') as f:f.write(data);f.flush();os.fsync(f.fileno())
  os.replace(tmp,path)
  try:
   dfd=os.open(str(path.parent),os.O_RDONLY);os.fsync(dfd);os.close(dfd)
  except OSError:pass
 finally:
  try:os.unlink(tmp)
  except FileNotFoundError:pass
def atomic_json(path:Path,value:Any)->None:atomic_bytes(path,json.dumps(value,indent=2,sort_keys=True,ensure_ascii=False,allow_nan=False).encode()+b'\n')
def deterministic_zip(path:Path,entries:Mapping[str,bytes])->None:
 path.parent.mkdir(parents=True,exist_ok=True)
 fd,tmp=tempfile.mkstemp(prefix=f'.{path.name}.',dir=str(path.parent));os.close(fd)
 try:
  with zipfile.ZipFile(tmp,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
   for name in sorted(entries):
    info=zipfile.ZipInfo(name,ZERO_TIME);info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=0o100644<<16
    z.writestr(info,entries[name])
  with open(tmp,'rb') as f:os.fsync(f.fileno())
  os.replace(tmp,path)
 finally:
  try:os.unlink(tmp)
  except FileNotFoundError:pass

from __future__ import annotations
import argparse,json,sys
from pathlib import Path
def main():
 p=argparse.ArgumentParser();p.add_argument("--root",type=Path,default=Path.home()/"open-cognitive-ecology");g=p.add_mutually_exclusive_group(required=True);g.add_argument("--make-template",type=Path);g.add_argument("--check",type=Path);g.add_argument("--apply",type=Path);a=p.parse_args();root=a.root.resolve()
 if str(root) not in sys.path:sys.path.insert(0,str(root))
 from ontology import occ_batch_governed_proposals as b
 if a.make_template:
  a.make_template.parent.mkdir(parents=True,exist_ok=True);a.make_template.write_text(json.dumps(b.template(root),ensure_ascii=False,sort_keys=True,indent=2)+"\n",encoding="utf-8");print("P159_OCC1A_BATCH_TEMPLATE_OK");return
 if a.check:b.validate_document(root,json.loads(a.check.read_text(encoding="utf-8")));print("P159_OCC1A_BATCH_PREVALIDATION_OK");print("no_registry_write=true");return
 r=b.apply_batch(root,a.apply);print("P159_OCC1A_BATCH_APPLY_OK")
 for k,v in r.items():print(f"{k}={str(v).lower() if isinstance(v,bool) else v}")
if __name__=="__main__":main()

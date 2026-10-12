from __future__ import annotations
import hashlib, json, sys
from pathlib import Path
from typing import Any, Mapping
from acee5_hardening_test_support import valid_context
from ontology.acee_governed_code_generation_gate import AceeGovernedCodeGenerationGate
from ontology.acee_installation_executor import AceeInstallationExecutor, _sha

ORDER=("functional","fast_guard","fast_acceptance","final_lock","degradation","non_regression","specialized")

def sha(value: Any)->str:
    return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()

def seed(root: Path)->None:
    (root/'ontology').mkdir(parents=True,exist_ok=True)
    (root/'ontology_inventory.txt').write_text('alpha\n',encoding='utf-8')
    inv="# Auto-generated ontology inventory\n\nONTOLOGY_INVENTORY = ['alpha']\n"
    for rel in ('ontology_inventory.py','ontology/ontology_inventory.py'):
        p=root/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(inv,encoding='utf-8')
    (root/'dependency_registry.py').write_text("# Auto-generated dependency registry\n\nDEPENDENCY_REGISTRY = {'alpha': []}\n",encoding='utf-8')
    (root/'global_module_catalog.txt').write_text('Open Cognitive Ecology — Global Module Catalog\n[modules]\n',encoding='utf-8')

def quick_commands(root: Path, tag: str):
    result=[]
    for role in ORDER:
        p=root/f'k5_{tag}_{role}.py';p.write_text(f"print('K5_{tag.upper()}_{role.upper()}_OK')\n",encoding='utf-8')
        result.append({'role':role,'name':role,'argv':[sys.executable,str(p)],'timeout_seconds':10})
    return result

def payload(root: Path,index:int,stage:str='ACEE6-F2',content:str|None=None):
    content=content if content is not None else f'VALUE = {index}\n'
    digest=hashlib.sha256(content.encode()).hexdigest();proposal=f'k5-proposal-{index:04d}'
    decision=AceeGovernedCodeGenerationGate(root=root).step(inputs=valid_context(root,proposal_id=proposal,candidate_hash=digest),persist=False)
    context={'requested_stage':stage,'candidate_content':content,'inventory_dependencies':[], 'local_validation_commands':quick_commands(root,f'{index:04d}'), 'global_validation_timeout_seconds':10}
    return {'acee5_decision':decision,'admission_context':context}

def write_hashed(ex: AceeInstallationExecutor, path: Path, payload: Mapping[str,Any], field: str)->str:
    body=dict(payload);body[field]=_sha(body);ex._atomic_json_write(path,body);return str(body[field])

def globally_validated_fixture(root: Path,index:int):
    ex=AceeInstallationExecutor(root=root)
    tx=f'k5-commit-{index:04d}';proposal=f'k5-proposal-{index:04d}';manifest=hashlib.sha256(f'manifest:{index}'.encode()).hexdigest()
    target=root/'ontology'/f'k5_candidate_{index:04d}.py';target.parent.mkdir(parents=True,exist_ok=True);target.write_text(f'VALUE = {index}\n',encoding='utf-8')
    target_sha=hashlib.sha256(target.read_bytes()).hexdigest();td=ex._transaction_runtime_root()/tx;td.mkdir(parents=True,exist_ok=True)
    previous=None
    states=("PREPARING","PREPARED","BACKING_UP","BACKED_UP","MUTATING","MUTATED","COMPILING","COMPILED","INVENTORY_UPDATING","INVENTORIES_UPDATED","TESTING","LOCALLY_VALIDATED","GLOBAL_VALIDATING","GLOBALLY_VALIDATED")
    for state in states:
        previous=ex._append_journal_record(td/'journal.jsonl',{'transaction_id':tx,'proposal_id':proposal,'state':state,'timestamp_utc':ex.now_utc.isoformat()},previous)
    latest={'transaction_id':tx,'proposal_id':proposal,'manifest_hash':manifest,'transaction_state':'GLOBALLY_VALIDATED','global_validation_passed':True,'local_validation_passed':True,'committed':False,'latest_record_hash':previous}
    specs=((ex._compilation_report_path(td),'compilation_report_hash'),(ex._inventory_update_manifest_path(td),'inventory_update_manifest_hash'),(ex._local_validation_report_path(td),'local_validation_report_hash'),(ex._global_validation_report_path(td),'global_validation_report_hash'))
    for path,field in specs: latest[field]=write_hashed(ex,path,{'transaction_id':tx,'proposal_id':proposal},field)
    latest['state_hash']=_sha(latest);ex._atomic_json_write(td/'latest_state.json',latest)
    admitted={'proposal_id':proposal,'manifest_hash':manifest,'normalized_plan':{'target_path':str(target.relative_to(root)),'candidate_content_sha256':target_sha}}
    return ex,latest,admitted,td

def prepared_fixture(root: Path,index:int):
    ex=AceeInstallationExecutor(root=root);tx=f'k5-quarantine-{index:04d}';proposal=f'k5-proposal-{index:04d}';td=ex._transaction_runtime_root()/tx;td.mkdir(parents=True,exist_ok=True)
    previous=None
    for state in ('PREPARING','PREPARED'):
        previous=ex._append_journal_record(td/'journal.jsonl',{'transaction_id':tx,'proposal_id':proposal,'state':state,'timestamp_utc':ex.now_utc.isoformat()},previous)
    latest={'transaction_id':tx,'proposal_id':proposal,'transaction_state':'PREPARED','latest_record_hash':previous,'committed':False,'partial_success':False}
    latest['state_hash']=_sha(latest);ex._atomic_json_write(td/'latest_state.json',latest)
    return ex,latest,td

class ForcedCollisionExecutor(AceeInstallationExecutor):
    def _transaction_id(self,result: Mapping[str,Any])->str:return 'acee6c-k5-forced-collision'

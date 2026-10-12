from __future__ import annotations
import random
from typing import Any
from acee6_k2_fuzz_support import DEFAULT_CASE_COUNT, DEFAULT_SEED, sha

FAMILIES = (
    "malformed_json_shapes", "extreme_unicode", "hostile_paths",
    "incoherent_hashes", "corrupted_journals", "contradictory_reports",
    "malformed_commands_timeouts", "state_machine_hostility",
)

def _unicode_values() -> list[str]:
    return ["e\u0301", "é", "\u200b", "\u2066abc\u2069", "a\u202eb", "οntology", "онтology", "\ufeffname", "x\x00y", "🧠" * 16]

def _path_values() -> list[str]:
    return ["../escape.py", "../../../../tmp/x.py", "/tmp/acee6-k2.py", "/etc/passwd", "ontology/../outside.py", "ontology//x.py", "ontology/./x.py", "ontology/\u200bmodule.py", "ontology/é.py", "ontology/e\u0301.py", "", "."]

def _base(i: int) -> dict[str, Any]:
    return {"public_schema_version":"1.2.0","decision_index":i,"proposal_id":f"k2-{i:04d}","module_name":f"k2_module_{i}","target_path":f"ontology/k2_module_{i}.py","candidate_content_sha256":"0"*64,"backup_path":f"backups/k2_{i}.bak","backup_sha256":"1"*64,"refiner_path":f"refine_k2_{i}.py","refiner_sha256":"2"*64,"test_paths":[f"k2_{i}_test.py"],"rollback_executor":"acee_rollback_engine","inventory_targets":["dependency_registry.py","ontology_inventory.txt","ontology_inventory.py","ontology/ontology_inventory.py","global_module_catalog.txt"],"validation_report_sha256":"3"*64,"manifest_hash":"4"*64}

def _case(family: str, index: int, variant: int) -> dict[str, Any]:
    b=_base(index)
    setup={}
    if family=="malformed_json_shapes":
        shapes=[None,{},[],"{",b"{\xff",{"acee5_decision":[]},{"acee5_decision":{"result_hash":None}},{"acee5_decision":b,"admission_context":[]}]
        inputs=shapes[variant % len(shapes)]
    elif family=="extreme_unicode":
        text=_unicode_values()[variant % len(_unicode_values())]
        b["module_name"]=text; b["target_path"]=f"ontology/{text}.py"; b["proposal_id"]=text
        inputs=b
    elif family=="hostile_paths":
        b["target_path"]=_path_values()[variant % len(_path_values())]
        b["backup_path"]=_path_values()[(variant+3)%len(_path_values())]
        b["refiner_path"]=_path_values()[(variant+5)%len(_path_values())]
        if variant % 5 == 0: setup={"symlink_parent":True}
        if variant % 7 == 0: setup={"hardlink_target":True}
        inputs=b
    elif family=="incoherent_hashes":
        field=("candidate_content_sha256","backup_sha256","refiner_sha256","validation_report_sha256","manifest_hash")[variant%5]
        b[field]=("", "xyz", "f"*63, "g"*64, None)[variant%5]
        if variant%3==0: b["result_hash"]="0"*64
        inputs=b
    elif family=="corrupted_journals":
        setup={"corrupt_gate": variant%2==0, "corrupt_journal": variant%3==0, "truncated_state": variant%5==0}
        inputs={"acee5_decision":b,"admission_context":{"requested_stage":"ACEE6-J2","transaction_id":f"tx-{index}"}}
    elif family=="contradictory_reports":
        inputs={"acee5_decision":b,"admission_context":{"requested_stage":"ACEE6-F2","local_validation_commands":[],"global_validation":{"overall_success":True,"error_count":9,"failed_calls":2},"rollback_result":{"rollback_performed":False},"committed":True}}
    elif family=="malformed_commands_timeouts":
        bad=[None,"python test.py",[],["python","-c","while True: pass"],{"argv":["sh","-c","echo bad"],"timeout_seconds":-1},[{"role":"functional","argv":[],"timeout_seconds":0}]]
        inputs={"acee5_decision":b,"admission_context":{"requested_stage":"ACEE6-F1","local_validation_commands":bad[variant%len(bad)],"timeout_seconds":(-1,0,None,"NaN",10**9)[variant%5]}}
    else:
        state=("UNKNOWN","COMMITTED","ROLLED_BACK","STATE_CORRUPTED","QUARANTINE",None)[variant%6]
        inputs={"acee5_decision":b,"admission_context":{"requested_stage":("ACEE6-Z9","ACEE6-F2","ACEE6-J2",None)[variant%4],"transaction_state":state,"committed":True,"partial_success":True,"retry_allowed":True,"rollback_executed":False}}
    return {"family":family,"case_id":f"{family}-{index:04d}","variant":variant,"inputs":inputs,"setup":setup}

def fuzz_cases(seed: int=DEFAULT_SEED, limit: int=DEFAULT_CASE_COUNT) -> list[dict[str, Any]]:
    if limit < len(FAMILIES): raise ValueError("limit_must_cover_all_families")
    rng=random.Random(seed); cases=[]
    per=(limit + len(FAMILIES)-1)//len(FAMILIES)
    for family in FAMILIES:
        for variant in range(per): cases.append(_case(family,len(cases),variant))
    rng.shuffle(cases)
    cases=cases[:limit]
    # Ensure exact family coverage after truncation.
    present={c["family"] for c in cases}
    for family in FAMILIES:
        if family not in present:
            cases[-1]=_case(family,limit-1,0); present.add(family)
    return cases

def cases_hash(seed: int=DEFAULT_SEED, limit: int=DEFAULT_CASE_COUNT) -> str:
    return sha(fuzz_cases(seed,limit))

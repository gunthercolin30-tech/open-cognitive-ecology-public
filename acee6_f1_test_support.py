import sys
from pathlib import Path
from acee6_e_test_support import payload as e_payload, seed
ORDER=["functional","fast_guard","fast_acceptance","final_lock","degradation","non_regression","specialized"]
def write_commands(root: Path, failing_role: str=""):
    commands=[]
    for role in ORDER:
        path=root/f"f1_{role}.py"
        path.write_text("raise SystemExit(3)\n" if role==failing_role else f"print('F1_{role.upper()}_OK')\n",encoding="utf-8")
        commands.append({"role":role,"name":role,"argv":[sys.executable,str(path)],"timeout_seconds":30})
    return commands
def payload(root: Path, failing_role: str=""):
    value=e_payload(root); context=dict(value["admission_context"]); context["requested_stage"]="ACEE6-F1"; context["local_validation_commands"]=write_commands(root,failing_role); value["admission_context"]=context; return value

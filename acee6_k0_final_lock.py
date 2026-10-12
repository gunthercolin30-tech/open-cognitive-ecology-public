from __future__ import annotations
import ast, subprocess, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent
required=['acee6_k0_support.py','acee6_k0_certification_orchestrator.py','acee6_k0_fast_acceptance_suite.py']
for name in required:
    path=ROOT/name
    assert path.is_file(), name
    ast.parse(path.read_text(encoding='utf-8'))
source=(ROOT/'acee6_k0_support.py').read_text(encoding='utf-8')
for token in ['CAMPAIGNS','mutation_score_min','heavy_campaigns_default_enabled','discover_executor_class','verify_report']:
    assert token in source, token
completed=subprocess.run([sys.executable,str(ROOT/'acee6_k0_fast_acceptance_suite.py')],cwd=str(ROOT),text=True,capture_output=True,timeout=300)
if completed.returncode:
    raise SystemExit(f'K0 fast acceptance failed\nSTDOUT:\n{completed.stdout}\nSTDERR:\n{completed.stderr}')
print(completed.stdout.strip())
print('ACEE6_K0_FINAL_LOCK_OK')

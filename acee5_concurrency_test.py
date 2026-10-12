from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from tempfile import TemporaryDirectory
from ontology.acee_governed_code_generation_gate import AceeGovernedCodeGenerationGate
from acee5_hardening_test_support import valid_context
with TemporaryDirectory() as td:
    root=Path(td)
    def run(i): return AceeGovernedCodeGenerationGate(root=root).step(valid_context(root,f'p{i}'),persist=True)
    with ThreadPoolExecutor(max_workers=8) as ex: results=list(ex.map(run,range(24)))
    _, history, _=AceeGovernedCodeGenerationGate(root=root)._paths(); lines=history.read_text().splitlines()
    assert len(lines)==24 and sorted(r['decision_index'] for r in results)==list(range(24))
print('ACEE5_CONCURRENCY_OK')

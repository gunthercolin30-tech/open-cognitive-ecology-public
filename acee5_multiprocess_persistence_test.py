import json, multiprocessing as mp
from pathlib import Path
from tempfile import TemporaryDirectory
from ontology.acee_governed_code_generation_gate import AceeGovernedCodeGenerationGate
from acee5_hardening_test_support import valid_context
def worker(root_text, i):
    root=Path(root_text); AceeGovernedCodeGenerationGate(root=root).step(valid_context(root,f'p{i}'),persist=True)
if __name__=='__main__':
    with TemporaryDirectory() as td:
        ctx=mp.get_context('spawn'); ps=[ctx.Process(target=worker,args=(td,i)) for i in range(12)]
        [p.start() for p in ps]; [p.join(30) for p in ps]; assert all(p.exitcode==0 for p in ps)
        gate=AceeGovernedCodeGenerationGate(root=Path(td)); _, history, _=gate._paths(); records=[json.loads(x) for x in history.read_text().splitlines()]
        assert len(records)==12 and [r['decision_index'] for r in records]==list(range(12))
    print('ACEE5_MULTIPROCESS_PERSISTENCE_OK')

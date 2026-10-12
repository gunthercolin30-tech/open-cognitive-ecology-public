import copy, random, tempfile, time
from pathlib import Path
from ontology.acee_governed_code_generation_gate import AceeGovernedCodeGenerationGate
from acee5_hardening_test_support import valid_context
random.seed(5005)
with tempfile.TemporaryDirectory() as tmp:
 root=Path(tmp);(root/'ontology').mkdir();gate=AceeGovernedCodeGenerationGate(root=root);base=valid_context(root);corpus=[None,[],True,0,'',float('nan'),float('inf'),b'abc',{1,2}];cases=[None,[],'bad',17,{'proposal_id':''}]
 for _ in range(1200):
  c=copy.deepcopy(base);c[random.choice(list(c))]=random.choice(corpus);cases.append(c)
 start=time.perf_counter()
 for c in cases:
  before=copy.deepcopy(c);r=gate.step(c);assert isinstance(r,dict) and not r['code_installed_by_gate'] and not r['validation_executed_by_gate'];assert c==before
 assert time.perf_counter()-start<15
print('ACEE5_INPUT_FUZZ_OK')

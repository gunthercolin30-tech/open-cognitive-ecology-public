import math, random
from pathlib import Path
from tempfile import TemporaryDirectory
from ontology.acee_installation_executor import AceeInstallationExecutor
values=[None,True,False,0,1,-1,math.nan,math.inf,b"x",Path("x"),set([1]),{"x":object()},[{}],"é"*1000]
with TemporaryDirectory() as t:
 r=Path(t); r.mkdir(exist_ok=True); e=AceeInstallationExecutor(root=r)
 for v in values*50:
  x=e.step(v); assert isinstance(x,dict) and x["admissible"] is False
print("ACEE6_B1_INPUT_FUZZ_OK")

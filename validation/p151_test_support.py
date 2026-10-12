from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from ontology.cognitive_economic_efficiency import COST_COMPONENTS
def value(amount=120.0,unit="EUR",verified=True): return {"amount":amount,"unit":unit,"verified":verified,"provenance":"invoice:test"}
def costs(each=10.0,unit="EUR"): return {k:{"amount":each,"unit":unit,"measured":True,"provenance":"ledger:"+k} for k in COST_COMPONENTS}

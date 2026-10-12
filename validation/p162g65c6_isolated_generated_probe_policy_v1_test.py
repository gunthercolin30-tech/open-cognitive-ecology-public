from pathlib import Path
import tempfile,pytest
ROOT=Path(__file__).resolve().parents[1]
MODULES=[
"occ1h_h7_a075_common_tcb_resolution_probe.py",
"occ1h_h7_a075_defensive_identity_drift_discrimination.py",
"occ1h_h7_a075_independent_anchor_rebinding_probe.py",
"occ1h_h7_a075_relocatable_historical_control.py",
"occ1h_h7_a075_strict_relocatable_preclose_control.py",
"occ_constitutional_adversarial_crown_h7.py"]
def test_seven_direct_calls_removed():
 total=0
 for n in MODULES:
  s=(ROOT/"ontology"/n).read_text()
  total+=s.count("run_isolated_generated_probe(")
  assert "subprocess.run(" not in s
 assert total==7
def test_runner_rejects_escape_and_pathlike_args():
 import ontology.governed_isolated_probe_runner as g
 with tempfile.TemporaryDirectory() as td:
  sb=Path(td); sc=sb/"p.py"; sc.write_text("print(1)")
  outside=ROOT/"ontology_inventory.txt"
  with pytest.raises(PermissionError): g.run_isolated_generated_probe(script=outside,sandbox=sb)
  with pytest.raises(PermissionError): g.run_isolated_generated_probe(script=sc,sandbox=sb,args=("../x",))
def test_fixed_timeout():
 import ontology.governed_isolated_probe_runner as g
 with tempfile.TemporaryDirectory() as td:
  sb=Path(td); sc=sb/"p.py"; sc.write_text("print(1)")
  with pytest.raises(PermissionError): g.run_isolated_generated_probe(script=sc,sandbox=sb,timeout_seconds=31)
def test_no_direct_transport_in_runner():
 s=(ROOT/"ontology/governed_isolated_probe_runner.py").read_text()
 assert "subprocess.run" not in s and "subprocess.Popen" not in s

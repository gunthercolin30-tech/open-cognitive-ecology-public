#!/usr/bin/env python3
import hashlib,json
from pathlib import Path
ROOT=Path.home()/"open-cognitive-ecology"
REPORT=ROOT/"p011_e_final_lock_report.json"
FILES={'ontology_inventory.txt': '606dbfaf7676cd5f8a99c0bc0f05e5bf8cfca7c48047286debec45be24a288b9', 'scientific_validation_report.json': 'a32faf23c726d746d5795e0b93332b6ece50cbc155e179724407d7194736c033', 'validation/p011_structural_dna_reconstruction_audit.py': 'b7f846d9cb1bbff46d00654daff771fd33198898b2bfc1991c4199379e26aae7', 'validation/p011_functional_layer_reconstruction.py': '5b024e4fa695e19eca6e5eea4d351e41798ad8c6fe263ef908bb62dd03a2221b', 'validation/p011_c0_executable_interface_audit.py': 'c8e35710cc47ca4f1b66f6e2223cc91f3c67880ea488bfb1afa0fe6be40e3148', 'validation/p011_c1_dynamic_enforcement_probe.py': '2c84757e48977bab9c215acdac176cf3e2811f1fa0b594b38d54b7885b852a4d', 'validation/p011_c2_persistence_restart_probe.py': '0f2d6a13b0b5bafa2bbf505ff2bf240cc803847202bb4f9d721b024c8bd6daee', 'validation/p011_c3_succession_transmission_probe.py': 'a1041937b853c8a658d2d2581b6e401509fff1398a70213e23714484f4f8e463', 'validation/p011_d_adversarial_crown.py': 'bade1b912cb5e26f1ccd3ac03d78ce2fd1806516af02de87d12ef470213ddc58', 'p011_structural_dna_reconstruction_report.json': '5a1e6da5c0f81bfcb77defc63d39106de3928e6e74402d45dec31004d36d643e', 'p011_functional_layer_reconstruction_report.json': '3ad24c21b68a13050f07104d0d501eec1f399db321de0234f22e39c6bb7cb4c7', 'p011_c0_executable_interface_report.json': 'a894d975ef4258be0356222f7e3b712220d6798d31cfe72c685104312f7522f2', 'p011_c1_dynamic_enforcement_probe_report.json': '312f6549ae16446f1c345e28a75de36f086ef65af7bf7478c877f1b882532f34', 'p011_c2_persistence_restart_probe_report.json': '36a65206d10806ceed773314e8de2b62b2fdf701aeae13155bf078fe0e47b79e', 'p011_c3_succession_transmission_probe_report.json': 'a8512ac102a12baed351159f5c11bd547fa61dd7c669d900bb1f68fd3ed3f379', 'p011_d_adversarial_crown_report.json': 'a78387489d993b131b240116fb409b6f9d8f5977f1297d819d0cf4071408d8b8'}
IDS={'A1': '187d29b22ced7fc3dedd7876e2580a77a6ed0e6fed273d88e84be7bdac979f84', 'B': '2dbd735a034110a3c125bd4f9430d26165d1f3d437a8a812a3fe4ed9fb4b7419', 'C0': 'a2ff091d8b84f88813a209a9f4a833a1a7c42385a486eb7fa0ef9be1d384ac06', 'C1': '8f41c83843218c5b5b89e7b146ef0e21ea618e4d5802d1e98b21654ae46f0832', 'C2': 'd0bb7e54c99bc865ecc83d0b31842e7ad12c5e21f93141fcf15aeabed4eeba6b', 'C3': '3d2b55428db94283effbcede2a55168883013a8eb15639453d729a3343bebd8c', 'D': 'a75546deeec160b6d403db06413042fc9960c543e30f7a3d7b65a7758c36445d'}
REPORTS={"A1":"p011_structural_dna_reconstruction_report.json","B":"p011_functional_layer_reconstruction_report.json","C0":"p011_c0_executable_interface_report.json","C1":"p011_c1_dynamic_enforcement_probe_report.json","C2":"p011_c2_persistence_restart_probe_report.json","C3":"p011_c3_succession_transmission_probe_report.json","D":"p011_d_adversarial_crown_report.json"}
STATUSES={"A1":"PARTIAL_RECONSTRUCTION","B":"FUNCTIONAL_RELATIONS_PARTIAL","C0":"EXECUTABLE_INTERFACES_MAPPED","C1":"DYNAMIC_ENFORCEMENT_OBSERVED","C2":"PERSISTENCE_RESTART_PARTIAL","C3":"SUCCESSION_TRANSMISSION_COMPONENTS_OBSERVED","D":"ADVERSARIAL_CROWN_PASSED"}
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def identity(d): return d.get("audit_identity_sha256") or d.get("probe_identity_sha256") or d.get("crown_identity_sha256")
checks={}
for rel,expected in FILES.items():
 p=ROOT/rel
 checks["file:"+rel]=p.is_file() and sha(p)==expected
docs={}
for k,rel in REPORTS.items():
 d=json.loads((ROOT/rel).read_text()); docs[k]=d
 checks[k+":identity"]=identity(d)==IDS[k]
 checks[k+":status"]=d.get("status")==STATUSES[k]
 checks[k+":functional_only"]=d.get("functional_conclusion_only") is True
 checks[k+":phenomenology_undetermined"]=d.get("phenomenology_undetermined") is True
 for flag in ("consciousness_proven","subjectivity_proven","qualia_proven","phenomenology_proven"):
  if flag in d: checks[k+":"+flag]=d.get(flag) is False
checks["D:72_of_72"]=docs["D"].get("checks_passed")==72 and docs["D"].get("checks_total")==72
checks["D:e2e_unknown"]=docs["D"].get("conclusion",{}).get("native_end_to_end_civilizational_enforcement")=="UNKNOWN"
checks["C2:e2e_persistence_unknown"]=docs["C2"].get("conclusion",{}).get("end_to_end_constitutional_state_persistence")=="UNKNOWN"
checks["C3:native_chain_not_observed"]=docs["C3"].get("conclusion",{}).get("native_direct_component_chain")=="NOT_OBSERVED"
checks["C3:e2e_unknown"]=docs["C3"].get("conclusion",{}).get("end_to_end_integration")=="UNKNOWN"
failed=[k for k,v in checks.items() if not v]
if failed: raise SystemExit("P011_E_FINAL_LOCK_REFUSED: "+",".join(failed))
payload={"schema":"oce.p011.final_lock.v1","milestone":"P011","status":"LOCKED","protected_files":FILES,"protected_identities":IDS,
"checks_passed":sum(checks.values()),"checks_total":len(checks),"checks":checks,
"scientific_conclusion":{"structural_dna_reconstruction":"PARTIAL_RECONSTRUCTION","functional_relations":"FUNCTIONAL_RELATIONS_PARTIAL","component_level_dynamic_enforcement":"OBSERVED","protection_reinstantiation":"OBSERVED","succession_transmission_signal_composition":"OBSERVED","native_end_to_end_civilizational_enforcement":"UNKNOWN","phenomenology":"UNDETERMINED"},
"functional_conclusion_only":True,"phenomenology_undetermined":True,"consciousness_proven":False,"subjectivity_proven":False,"qualia_proven":False,"phenomenology_proven":False}
payload["lock_identity_sha256"]=hashlib.sha256(json.dumps(payload,sort_keys=True,separators=(",",":")).encode()).hexdigest()
REPORT.write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n")
print("P011_E_FINAL_LOCK_OK")
print(f"checks_passed={sum(checks.values())}/{len(checks)}")
print("status=LOCKED")
print("native_end_to_end_civilizational_enforcement=UNKNOWN")
print("phenomenology=UNDETERMINED")
print("lock_identity_sha256="+payload["lock_identity_sha256"])
print("report="+str(REPORT))

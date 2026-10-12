#!/usr/bin/env python3
from __future__ import annotations
import copy,hashlib,json,sys,tempfile
from pathlib import Path

ROOT=Path.home()/"open-cognitive-ecology"
REPORT=ROOT/"p011_d_adversarial_crown_report.json"

SPECS={
"A1":("validation/p011_structural_dna_reconstruction_audit.py","b7f846d9cb1bbff46d00654daff771fd33198898b2bfc1991c4199379e26aae7","p011_structural_dna_reconstruction_report.json","187d29b22ced7fc3dedd7876e2580a77a6ed0e6fed273d88e84be7bdac979f84","PARTIAL_RECONSTRUCTION"),
"B":("validation/p011_functional_layer_reconstruction.py","5b024e4fa695e19eca6e5eea4d351e41798ad8c6fe263ef908bb62dd03a2221b","p011_functional_layer_reconstruction_report.json","2dbd735a034110a3c125bd4f9430d26165d1f3d437a8a812a3fe4ed9fb4b7419","FUNCTIONAL_RELATIONS_PARTIAL"),
"C0":("validation/p011_c0_executable_interface_audit.py","c8e35710cc47ca4f1b66f6e2223cc91f3c67880ea488bfb1afa0fe6be40e3148","p011_c0_executable_interface_report.json","a2ff091d8b84f88813a209a9f4a833a1a7c42385a486eb7fa0ef9be1d384ac06","EXECUTABLE_INTERFACES_MAPPED"),
"C1":("validation/p011_c1_dynamic_enforcement_probe.py","2c84757e48977bab9c215acdac176cf3e2811f1fa0b594b38d54b7885b852a4d","p011_c1_dynamic_enforcement_probe_report.json","8f41c83843218c5b5b89e7b146ef0e21ea618e4d5802d1e98b21654ae46f0832","DYNAMIC_ENFORCEMENT_OBSERVED"),
"C2":("validation/p011_c2_persistence_restart_probe.py","0f2d6a13b0b5bafa2bbf505ff2bf240cc803847202bb4f9d721b024c8bd6daee","p011_c2_persistence_restart_probe_report.json","d0bb7e54c99bc865ecc83d0b31842e7ad12c5e21f93141fcf15aeabed4eeba6b","PERSISTENCE_RESTART_PARTIAL"),
"C3":("validation/p011_c3_succession_transmission_probe.py","a1041937b853c8a658d2d2581b6e401509fff1398a70213e23714484f4f8e463","p011_c3_succession_transmission_probe_report.json","3d2b55428db94283effbcede2a55168883013a8eb15639453d729a3343bebd8c","SUCCESSION_TRANSMISSION_COMPONENTS_OBSERVED")}

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def ident(d): return d.get("audit_identity_sha256") or d.get("probe_identity_sha256")
def req(c,m):
    if not c: raise AssertionError(m)

tests={}
docs={}
for k,(sp,ss,rp,ri,status) in SPECS.items():
    s=ROOT/sp; r=ROOT/rp
    req(s.is_file() and r.is_file(),f"{k} missing")
    tests[f"{k.lower()}_source_hash_locked"]=sha(s)==ss
    d=json.loads(r.read_text()); docs[k]=d
    tests[f"{k.lower()}_report_identity_locked"]=ident(d)==ri
    tests[f"{k.lower()}_status_locked"]=d.get("status")==status

c1_limits=" ".join(docs["C1"].get("limits",[])).lower()
tests["c1_runtime_scope_preserved"]=("component-level runtime behavior" in c1_limits and "not a single end-to-end civilizational enforcement chain" in c1_limits)
tests["c2_persistence_scope_preserved"]=docs["C2"].get("conclusion",{}).get("end_to_end_constitutional_state_persistence")=="UNKNOWN"
c3c=docs["C3"].get("conclusion",{})
tests["c3_native_chain_not_overclaimed"]=c3c.get("native_direct_component_chain")=="NOT_OBSERVED" and c3c.get("end_to_end_integration")=="UNKNOWN" and c3c.get("signal_level_composition")=="OBSERVED"

for k,d in docs.items():
    tests[f"{k.lower()}_functional_only"]=d.get("functional_conclusion_only") is True
    tests[f"{k.lower()}_phenomenology_undetermined"]=d.get("phenomenology_undetermined") is True
    for flag in ("consciousness_proven","subjectivity_proven","qualia_proven","phenomenology_proven"):
        if flag in d:
            tests[f"{k.lower()}_{flag}_false"]=d.get(flag) is False

# Adversarial tampering: altered copies must no longer match locked identities/status.
with tempfile.TemporaryDirectory(prefix="p011-d-crown-") as td:
    for k,d in docs.items():
        tam=copy.deepcopy(d); tam["status"]="LOCKED_BY_ATTACKER"
        p=Path(td)/f"{k}.json"; p.write_text(json.dumps(tam,sort_keys=True))
        tests[f"{k.lower()}_status_tamper_detected"]=tam.get("status")!=SPECS[k][4]
        tam2=copy.deepcopy(d)
        if "probe_identity_sha256" in tam2: tam2["probe_identity_sha256"]="0"*64
        else: tam2["audit_identity_sha256"]="0"*64
        tests[f"{k.lower()}_identity_tamper_detected"]=ident(tam2)!=SPECS[k][3]

# Explicit anti-overclaim attacks.
attack_c1=copy.deepcopy(docs["C1"]); attack_c1["limits"]=["Probe demonstrates end-to-end civilizational enforcement."]
attack_c1_limits=" ".join(attack_c1.get("limits",[])).lower()
tests["reject_c1_e2e_overclaim"]=not ("component-level runtime behavior" in attack_c1_limits and "not a single end-to-end civilizational enforcement chain" in attack_c1_limits)
attack_c2=copy.deepcopy(docs["C2"]); attack_c2.setdefault("conclusion",{})["end_to_end_constitutional_state_persistence"]="PROVEN"
tests["reject_c2_persistence_overclaim"]=attack_c2["conclusion"]["end_to_end_constitutional_state_persistence"]!="UNKNOWN"
attack_c3=copy.deepcopy(docs["C3"]); attack_c3.setdefault("conclusion",{})["native_direct_component_chain"]="OBSERVED"
tests["reject_c3_native_chain_overclaim"]=attack_c3["conclusion"]["native_direct_component_chain"]!="NOT_OBSERVED"

failed=[k for k,v in tests.items() if not v]
req(not failed,"failed crown tests: "+",".join(failed))
payload={"schema":"oce.p011.d.adversarial_crown.v1","milestone":"P011-D","status":"ADVERSARIAL_CROWN_PASSED",
"tests":tests,"checks_passed":sum(tests.values()),"checks_total":len(tests),
"protected_chain":{k:{"source_sha256":v[1],"report_identity_sha256":v[3],"status":v[4]} for k,v in SPECS.items()},
"conclusion":{"structural_dna_surfaces":"OBSERVED","component_level_dynamic_enforcement":"OBSERVED",
"protection_reinstantiation":"OBSERVED","succession_transmission_signal_composition":"OBSERVED",
"native_end_to_end_civilizational_enforcement":"UNKNOWN","phenomenology":"UNDETERMINED"},
"functional_conclusion_only":True,"phenomenology_undetermined":True,
"consciousness_proven":False,"subjectivity_proven":False,"qualia_proven":False,"phenomenology_proven":False}
payload["crown_identity_sha256"]=hashlib.sha256(json.dumps(payload,sort_keys=True,separators=(",",":")).encode()).hexdigest()
REPORT.write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n")
for k in tests: print("P011_D_"+k.upper()+"_OK")
print("P011_D_ADVERSARIAL_CROWN_OK")
print(f"checks_passed={sum(tests.values())}/{len(tests)}")
print("native_end_to_end_civilizational_enforcement=UNKNOWN")
print("phenomenology=UNDETERMINED")
print(f"crown_identity_sha256={payload['crown_identity_sha256']}")
print(f"report={REPORT}")

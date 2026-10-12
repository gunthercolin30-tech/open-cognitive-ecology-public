from pathlib import Path
import hashlib, json, re

ROOT = Path.home() / "open-cognitive-ecology"
OUT = ROOT / "validation_artifacts" / "p159" / "occ1k_r1"

FAMILY_COUNTS = {
    "NSI":12, "NIRI":14, "CCI":15, "SCCI":16, "CNPI":12,
    "IVI":12, "GCVI":10, "ACHI":16, "MCI":16, "RPI":18, "FLI":16,
}
STAGE_EVIDENCE = {
    "NSI": "validation/evidence/p159_occ1a_closure",
    "NIRI": "validation_artifacts/p159/occ1b",
    "CCI": "validation_artifacts/p159/occ1c",
    "SCCI": "validation_artifacts/p159/occ1d",
    "CNPI": "validation_artifacts/p159/occ1e",
    "IVI": "validation_artifacts/p159/occ1f",
    "GCVI": "validation_artifacts/p159/occ1g",
    "ACHI": "validation_artifacts/p159/occ1h",
    "MCI": "validation_artifacts/p159/occ1i",
    "RPI": "validation_artifacts/p159/occ1j",
    "FLI": "validation_artifacts/p159/occ1k",
}
CANONICAL_K_OBJECTS = (
    "OCCInvariantRegistry", "FinalLockCoverageMatrix",
    "OCCResidualRiskRegister", "OCCAssuranceDebtRegistry",
)

def _sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def _canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(",",":"), ensure_ascii=False).encode()

def _artifact_inventory(rel):
    base = ROOT / rel
    if not base.is_dir():
        return []
    out=[]
    for p in sorted(x for x in base.rglob("*") if x.is_file() and not x.name.endswith(".bak")):
        out.append({"path":p.relative_to(ROOT).as_posix(),"sha256":_sha(p)})
    return out

def build_foundation():
    registry=[]
    matrix=[]
    risks=[]
    debt=[]
    for fam,count in FAMILY_COUNTS.items():
        evidence=_artifact_inventory(STAGE_EVIDENCE[fam])
        evidence_refs=[x["path"] for x in evidence]
        for i in range(1,count+1):
            iid=f"{fam}-{i}"
            registry.append({
                "invariant_id":iid, "family":fam,
                "canonical_status":"REGISTERED",
                "source":"P159 exhaustive annex contract",
                "retirement_status":"ACTIVE",
            })
            matrix.append({
                "invariant_id":iid,
                "source_stage":STAGE_EVIDENCE[fam].split("/")[-1].upper(),
                "evidence_refs":evidence_refs,
                "evidence_presence":"PRESENT" if evidence_refs else "MISSING",
                "semantic_coverage":"TO_BE_QUALIFIED",
                "lock_credit":"NOT_YET_GRANTED",
            })
        if not evidence_refs:
            risks.append({
                "risk_id":f"RR-{fam}-EVIDENCE-MISSING",
                "family":fam, "severity":"ROOT" if fam in ("NSI","NIRI","CCI","SCCI","CNPI","IVI","FLI") else "CRITICAL",
                "status":"OPEN", "reason":"No stage evidence directory/artifact found",
            })
            debt.append({
                "debt_id":f"AD-{fam}-EVIDENCE-MISSING","family":fam,
                "status":"OPEN","blocks_lock":True,
            })

    # The historical OCC-1K lock is evidence, but cannot receive exhaustive-lock credit
    # until FL-B gates, meta-crown, mutation and independent verification are built.
    risks.append({
        "risk_id":"RR-FLI-EXHAUSTIVE-CERTIFICATION",
        "family":"FLI","severity":"ROOT","status":"OPEN",
        "reason":"Historical OCC-1K lacks exhaustive FL-B1..B12 / FL-A01..A20 / MUT-FL certification contract",
    })
    debt.append({
        "debt_id":"AD-FLI-EXHAUSTIVE-CERTIFICATION","family":"FLI",
        "status":"OPEN","blocks_lock":True,
        "required_next":"OCC-1K-R2 blocker gates and later meta-assurance",
    })

    foundation={
        "schema":"oce.p159.occ1k.evidence_foundation.v1",
        "milestone":"P159/OCC-1K-R1",
        "status":"EVIDENCE_FOUNDATION_READY",
        "historical_lock_preserved":True,
        "lock_granted":False,
        "p160b_opened":False,
        "authorization_created":False,
        "execution_performed":False,
        "functional_conclusion_only":True,
        "phenomenology_undetermined":True,
        "invariant_registry":registry,
        "coverage_matrix":matrix,
        "residual_risk_register":risks,
        "assurance_debt_registry":debt,
        "family_counts":FAMILY_COUNTS,
    }
    foundation["semantic_hash"]=hashlib.sha256(_canonical(foundation)).hexdigest()
    return foundation

def write_artifacts():
    OUT.mkdir(parents=True, exist_ok=True)
    f=build_foundation()
    objects={
        "occ_invariant_registry_v1.json":{"schema":"oce.p159.occ.invariant_registry.v1","items":f["invariant_registry"]},
        "final_lock_coverage_matrix_v1.json":{"schema":"oce.p159.occ.final_lock_coverage_matrix.v1","items":f["coverage_matrix"]},
        "occ_residual_risk_register_v1.json":{"schema":"oce.p159.occ.residual_risk_register.v1","items":f["residual_risk_register"]},
        "occ_assurance_debt_registry_v1.json":{"schema":"oce.p159.occ.assurance_debt_registry.v1","items":f["assurance_debt_registry"]},
        "occ1k_r1_evidence_foundation_v1.json":f,
    }
    manifest=[]
    for name,obj in objects.items():
        p=OUT/name
        p.write_bytes(_canonical(obj)+b"\n")
        try:
            artifact_path = p.relative_to(ROOT).as_posix()
        except ValueError:
            artifact_path = p.name
        manifest.append({"path":artifact_path,"sha256":_sha(p)})
    mp=OUT/"occ1k_r1_sha256_manifest_v1.json"
    mp.write_bytes(_canonical({"schema":"oce.p159.occ1k.r1.sha256_manifest.v1","artifacts":manifest})+b"\n")
    return f, manifest

def main():
    f,manifest=write_artifacts()
    print("P159_OCC1K_R1_EVIDENCE_FOUNDATION_READY")
    print("INVARIANTS_REGISTERED="+str(len(f["invariant_registry"])))
    print("COVERAGE_ROWS="+str(len(f["coverage_matrix"])))
    print("OPEN_RESIDUAL_RISKS="+str(len(f["residual_risk_register"])))
    print("OPEN_ASSURANCE_DEBTS="+str(len(f["assurance_debt_registry"])))
    print("LOCK_GRANTED=false")
    print("HISTORICAL_LOCK_MODIFIED=false")
    print("P160B_OPENED=false")
    print("AUTHORIZATION_CREATED=false")
    print("EXECUTION_PERFORMED=false")
    for x in manifest: print("ARTIFACT_SHA256="+x["sha256"]+" "+x["path"])

if __name__=="__main__":
    main()

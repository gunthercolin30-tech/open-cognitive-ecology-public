from pathlib import Path
import importlib
import tempfile

CONSUMERS = [
 ("ontology.scientific_self_revision_controller","ScientificSelfRevisionController"),
 ("ontology.scientific_consensus_tracker","ScientificConsensusTracker"),
 ("ontology.scientific_anomaly_detector","ScientificAnomalyDetector"),
 ("ontology.scientific_paradigm_shift_monitor","ScientificParadigmShiftMonitor"),
 ("ontology.scientific_meta_analysis_engine","ScientificMetaAnalysisEngine"),
 ("ontology.scientific_theory_confidence_engine","ScientificTheoryConfidenceEngine"),
]
PARENTS = [
 ("ontology.attractor_persistence_analyzer","AttractorPersistenceAnalyzer"),
 ("ontology.ecological_fatigue_analyzer","EcologicalFatigueAnalyzer"),
 ("ontology.ecological_viability_forecaster","EcologicalViabilityForecaster"),
 ("ontology.longitudinal_recovery_observer","LongitudinalRecoveryObserver"),
 ("ontology.resilience_distribution_analyzer","ResilienceDistributionAnalyzer"),
]
class RecordingContext:
    def __init__(self): self.calls=[]
    def execute_path(self,slot,op,path,payload=None):
        self.calls.append((slot,op,Path(path)))
        Path(path).mkdir(parents=True,exist_ok=True)
        return {"status":"EFFECT_CONFIRMED"}

def run():
    with tempfile.TemporaryDirectory() as td:
        base=Path(td)
        for modname,clsname in CONSUMERS:
            cls=getattr(importlib.import_module(modname),clsname)
            existing=base/(clsname+"_existing"); existing.mkdir()
            obj=cls(archive_dir=existing)
            assert obj.archive_dir==existing
            missing=base/(clsname+"_missing"); ctx=RecordingContext()
            obj=cls(archive_dir=missing,fs_context=ctx)
            assert missing.is_dir()
            assert ctx.calls==[("archive_create_dirs","FS_CREATE_DIRS",missing)]
            absent=base/(clsname+"_fail")
            try: cls(archive_dir=absent)
            except RuntimeError: pass
            else: raise AssertionError("missing authority did not fail closed: "+clsname)
            assert not absent.exists()
        childdir=base/"meta_existing"; childdir.mkdir()
        for modname,clsname in PARENTS:
            cls=getattr(importlib.import_module(modname),clsname)
            obj=cls(meta_analysis_archive_dir=childdir)
            assert obj.meta_analysis_engine.archive_dir==childdir
        from ontology.domain_viability_analyzer import _try_step
        r=_try_step("attractor_persistence_analyzer","AttractorPersistenceAnalyzer",constructor_kwargs={"meta_analysis_archive_dir":childdir},persist=False)
        assert isinstance(r,dict)
        from ontology.failure_recovery_orchestrator import FailureRecoveryOrchestrator
        f=object.__new__(FailureRecoveryOrchestrator)
        r=f._call_component("longitudinal_recovery_observer","LongitudinalRecoveryObserver",[],constructor_kwargs={"meta_analysis_archive_dir":childdir})
        assert isinstance(r,dict)
        # The narrow transaction context intentionally omits unrelated reconciliation imports.
        # Runtime behavior is compiled above; verify the exact transport contract statically here.
        import ast
        src=(Path(__file__).parents[1]/"ontology/longitudinal_reconciliation.py").read_text()
        tree=ast.parse(src)
        calls=[n for n in ast.walk(tree) if isinstance(n,ast.Call) and ((isinstance(n.func,ast.Name) and n.func.id=="LongitudinalRecoveryObserver") or (isinstance(n.func,ast.Attribute) and n.func.attr=="LongitudinalRecoveryObserver"))]
        assert len(calls)==1
        kws={k.arg for k in calls[0].keywords}
        assert {"meta_analysis_archive_dir","meta_analysis_fs_context"} <= kws
    print("P162G6_SC_D98F_TRANSACTION_FUNCTIONAL_DEGRADATION_NONREGRESSION_OK")
if __name__=="__main__": run()

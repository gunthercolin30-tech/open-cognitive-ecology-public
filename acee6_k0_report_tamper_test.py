from pathlib import Path
import tempfile
from acee6_k0_support import build_k0_report, verify_report

def main():
    with tempfile.TemporaryDirectory() as tmp:
        root=Path(tmp); (root/'ontology').mkdir()
        (root/'ontology'/'acee_installation_executor.py').write_text('class AceeInstallationExecutor:\n    def __init__(self, root=None): self.root=root\n    def step(self, inputs=None, persist=False): return {}\n',encoding='utf-8')
        report=build_k0_report(root)
        assert verify_report(report)['valid'] is True
        report['thresholds']['mutation_score_min']=0.1
        checked=verify_report(report)
        assert checked['valid'] is False
        assert 'report_hash_invalid' in checked['reasons']
    print('ACEE6_K0_REPORT_TAMPER_OK')
if __name__=='__main__': main()

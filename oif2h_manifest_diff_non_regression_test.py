from copy import deepcopy
from pathlib import Path
from oif.interface.manifest_diff import compare_manifests
from oif.interface.manifest_validator import ManifestValidator
ROOT=Path(__file__).resolve().parent
paths=sorted((ROOT/'interfaces'/'examples'/'minimal').glob('*.*'))+sorted((ROOT/'interfaces'/'examples'/'complex').glob('*.*'))
assert paths
for path in paths:
    report=ManifestValidator().validate(path)
    assert report.valid and report.manifest is not None, (path,report.errors)
    original=path.read_bytes()
    diff=compare_manifests(report.manifest,report.manifest)
    assert not diff.changed and not diff.entries
    assert path.read_bytes()==original
m={'a':1}
try: compare_manifests(m,m)
except Exception: pass
assert m=={'a':1}
print('OIF2H_MANIFEST_DIFF_NON_REGRESSION_OK')

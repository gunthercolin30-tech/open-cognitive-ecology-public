from pathlib import Path
from oif.interface.manifest_diff import compare_manifests
from oif.interface.manifest_validator import ManifestValidator
from oif.interface.serialization import specification_to_json, specification_to_yaml
ROOT=Path(__file__).resolve().parent
p=ROOT/'interfaces'/'examples'/'complex'/'portal_pilot.yaml'
report=ManifestValidator().validate(p)
assert report.valid and report.manifest
j=specification_to_json(report.manifest)
y=specification_to_yaml(report.manifest)
r=compare_manifests(j,y,'json','yaml')
assert not r.changed, r.as_dict()
print('OIF2H_MANIFEST_DIFF_CROSS_FORMAT_OK')

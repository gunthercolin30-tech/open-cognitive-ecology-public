from copy import deepcopy
from pathlib import Path
from oif.interface.manifest_validator import ManifestValidator
ROOT=Path(__file__).resolve().parent
BASE=ROOT/'interfaces'/'examples'/'complex'/'portal_pilot.yaml'
def base_mapping():
    report=ManifestValidator().validate(BASE)
    assert report.valid and report.manifest is not None, report.errors
    return deepcopy(dict(report.manifest.as_dict()))

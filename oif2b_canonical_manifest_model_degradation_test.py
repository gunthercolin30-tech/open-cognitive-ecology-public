from dataclasses import replace
from oif.interface import SpecificationViolation
from oif.interface.models import ModelViolation, InterfaceMetadata
from oif2b_test_support import build_spec

try:
    InterfaceMetadata(interface_id="../bad", title="x", renderer_id="nicegui")
    raise AssertionError("invalid identifier accepted")
except ModelViolation:
    pass

spec = build_spec()
try:
    replace(spec, schema_version="oif.interface.v2")
    raise AssertionError("unsupported schema accepted")
except SpecificationViolation:
    pass

try:
    replace(spec, components=())
    raise AssertionError("dangling component reference accepted")
except SpecificationViolation:
    pass

print("OIF2B_DEGRADATION_OK")

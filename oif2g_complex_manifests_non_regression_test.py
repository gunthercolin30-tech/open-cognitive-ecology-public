from oif2g_test_support import *
from oif.interface.serialization import load_yaml_mapping,mapping_to_canonical_json
from oif.interface.reference_resolver import SecureReferenceResolver
from oif.interface.reference_catalog import ReferenceKind
for name in NAMES:
 m=load_yaml_mapping(MANIFEST_DIR/(name+".yaml")); assert mapping_to_canonical_json(m)==mapping_to_canonical_json(m); r=validator().validate(MANIFEST_DIR/(name+".yaml")); assert r.valid and r.phases_completed==("parse","schema","semantic","reference","constitution")
res=SecureReferenceResolver(catalogue()); assert res.resolve_exact("nicegui",ReferenceKind.RENDERER).reference_id=="nicegui"
print("OIF2G_NON_REGRESSION_OK")

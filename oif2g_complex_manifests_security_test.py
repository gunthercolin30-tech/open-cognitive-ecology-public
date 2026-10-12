from oif2g_test_support import *
from oif.interface.serialization import load_yaml_mapping,mapping_to_canonical_json
for name in NAMES:
 t=mapping_to_canonical_json(load_yaml_mapping(MANIFEST_DIR/(name+".yaml"))).casefold()
 for x in ('"class_path"','"entrypoint"','"callable"','"javascript"','"shell"','"exec"','"import"'): assert x not in t
print("OIF2G_SECURITY_OK")

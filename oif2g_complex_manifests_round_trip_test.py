from oif2g_test_support import *
from oif.interface.serialization import load_yaml_mapping,load_json_mapping,mapping_to_canonical_json
for name in NAMES: assert mapping_to_canonical_json(load_yaml_mapping(MANIFEST_DIR/(name+".yaml")))==mapping_to_canonical_json(load_json_mapping(MANIFEST_DIR/(name+".json")))
print("OIF2G_ROUND_TRIP_OK")

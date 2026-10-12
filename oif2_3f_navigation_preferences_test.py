from __future__ import annotations
from oif.ui.navigation_preferences import MAX_EXPANDED_CARDS, MAX_QUERY_LENGTH, NavigationPreferences, sanitize_preferences

def main():
    zones = ("overview", "runtime")
    source = {"schema_version": 1, "active_zone": "runtime", "query": "  runtime   health ", "expanded_cards": ["a", "a", "b"], "compact": True, "payload": {"forbidden": True}}
    prefs = sanitize_preferences(source, zones)
    assert prefs.active_zone == "runtime"
    assert prefs.query == "runtime health"
    assert prefs.expanded_cards == ("a", "b")
    assert prefs.compact is True
    encoded = prefs.as_dict()
    assert "payload" not in encoded
    damaged = sanitize_preferences({"schema_version": 999, "active_zone": "runtime"}, zones)
    assert damaged == NavigationPreferences(active_zone="overview")
    bounded = sanitize_preferences({"schema_version": 1, "query": "x" * 1000, "expanded_cards": [str(i) for i in range(200)]}, zones)
    assert len(bounded.query) == MAX_QUERY_LENGTH
    assert len(bounded.expanded_cards) == MAX_EXPANDED_CARDS
    print("OIF2_3F_NAVIGATION_PREFERENCES_OK")
    return 0
if __name__ == "__main__": raise SystemExit(main())

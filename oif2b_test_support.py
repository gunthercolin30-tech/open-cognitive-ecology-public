from oif.interface import (
    AccessibilitySpecification, ComponentSpecification, DataSourceSpecification,
    InterfaceMetadata, InterfaceSpecification, LayoutRegionSpecification,
    LayoutSpecification, NavigationSpecification, NavigationZoneSpecification,
    OperationSpecification, PermissionSpecification, PreferenceSpecification,
)
from oif_functional_constitution import ActionLevel


def build_spec():
    return InterfaceSpecification(
        schema_version="oif.interface.v1",
        interface=InterfaceMetadata(
            interface_id="oce.main", title="Open Cognitive Ecology",
            renderer_id="nicegui", metadata={"functional_only": True},
        ),
        navigation=NavigationSpecification(
            default_zone_id="overview",
            zones=(NavigationZoneSpecification(
                zone_id="overview", label="Vue générale", description="État fonctionnel",
                order=0, layout_id="main",
            ),),
        ),
        layout=(LayoutSpecification(
            layout_id="main",
            regions=(LayoutRegionSpecification(region_id="content", component_ids=("status.card",)),),
        ),),
        data_sources=(DataSourceSpecification(
            provider_id="runtime.health", zone_id="overview", data_contract="runtime.health.v1",
        ),),
        components=(ComponentSpecification(
            component_id="status.card", component_type="status_card",
            provider_id="runtime.health", operation_ids=("refresh",),
            properties={"compact": False},
        ),),
        operations=(OperationSpecification(
            operation_id="refresh", action_level=ActionLevel.OBSERVE,
            permission_ids=("runtime.read",),
        ),),
        permissions=(PermissionSpecification(
            permission_id="runtime.read", description="Read runtime state",
        ),),
        preferences=(PreferenceSpecification(
            preference_id="compact", value_type="boolean", default_value=False,
            allowed_values=(False, True),
        ),),
        accessibility=AccessibilitySpecification(),
    )

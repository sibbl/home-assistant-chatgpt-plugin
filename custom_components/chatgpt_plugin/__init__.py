import logging
from aiohttp.web import Request, Response
from http import HTTPStatus
from homeassistant.components.http import HomeAssistantView
from .const import CONF_BASE_URL, CONF_OPENAI_VERIFICATION_TOKEN
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.area_registry import (
    async_get as get_area_registry,
)
from homeassistant.helpers.device_registry import (
    async_entries_for_area as device_entries_for_area,
    async_get as get_device_registry,
)
from homeassistant.helpers.entity_registry import (
    async_entries_for_device as entity_entries_for_device,
    async_get as get_entity_registry,
)
from .views.ai_plugin_view import ai_plugin_view_instance
from .views.openapi_doc_view import openapi_doc_view_instance

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    base_url = entry.data[CONF_BASE_URL]
    verification_token = entry.data[CONF_OPENAI_VERIFICATION_TOKEN]

    ai_plugin_view_instance.set_base_url(base_url)
    ai_plugin_view_instance.set_verification_token(verification_token)
    openapi_doc_view_instance.set_base_url(base_url)

    hass.http.register_view(ai_plugin_view_instance)
    hass.http.register_view(openapi_doc_view_instance)
    hass.http.register_view(APIEntitiesView)
    hass.http.register_view(APIAreasView)
    hass.http.register_view(APIAreaDetailView)
    return True

class APIEntitiesView(HomeAssistantView):
    url = "/api/chatgpt/entities"
    name = "api:chatgpt:entities"

    async def get(self, request: Request) -> Response:
        # TODO: replace this endpoint with more helpful endpoints...
        user = request["hass_user"]
        entity_perm = user.permissions.check_entity
        
        query_parameters = request.rel_url.query
        included_domains = []
        if 'domain' in query_parameters.keys():
            included_domains = query_parameters.getall("domain")
            
        entities = [
            {
                'entity_id': state.entity_id,
                'state': state.state,
                **({'name': state.attributes.get('friendly_name')} 
                   if state.attributes.get('friendly_name') is not None else {}),
                **({'unit': state.attributes.get('unit_of_measurement')}
                   if state.attributes.get('unit_of_measurement') is not None else {}),
                # TODO: add area
            }
            for state in request.app["hass"].states.async_all()
            if (len(included_domains) == 0 or state.entity_id.split('.')[0]
                in included_domains) and entity_perm(state.entity_id, "read")
        ]
        return self.json(entities)


class APIAreasView(HomeAssistantView):
    """View to handle Areas requests."""

    url = "/api/chatgpt/areas"
    name = "api:chatgpt:areas"

    async def get(self, request: Request) -> Response:
        """Get registered areas."""
        areas = await async_areas_json(request.app["hass"])
        return self.json(areas)


class APIAreaDetailView(HomeAssistantView):
    """View to handle Area detail requests."""

    url = "/api/chatgpt/areas/{area_id}"
    name = "api:chatgpt:area-detail"

    async def get(self, request, area_id):
        """Get detail for specified area."""
        area_detail = await async_areas_area_json(request.app["hass"], area_id)
        if area_detail:
            return self.json(area_detail)
        return self.json_message(f"Area {area_id} not found.", HTTPStatus.NOT_FOUND)

async def async_areas_json(hass):
    """Generate areas data to JSONify."""
    registry = get_area_registry(hass)
    return [
        {"area_id": entry.id, "name": entry.name}
        for entry in registry.async_list_areas()
    ]

async def async_areas_area_json(hass, area_id):
    """Generate area detail to JSONify."""
    area_registry = get_area_registry(hass)
    area = area_registry.async_get_area(area_id)
    if not area:
        return None

    device_registry = get_device_registry(hass)
    entity_registry = get_entity_registry(hass)
    entities = []
    devices = []

    for device in device_entries_for_area(device_registry, area_id):
        devices.append({"device_id": device.id, "name": device.name})
        for entity in entity_entries_for_device(entity_registry, device.id):
            entities.append(
                {
                    "entity_id": entity.entity_id,
                    "name": entity.name or entity.original_name,
                }
            )

    return {
        "area_id": area_id,
        "name": area.name,
        "devices": devices,
        "entities": entities,
    }
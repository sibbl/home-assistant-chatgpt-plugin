import logging
import os
from aiohttp.web import Request, Response
from homeassistant.components.http import HomeAssistantView

DOMAIN = "chatgpt_plugin"

_LOGGER = logging.getLogger(__name__)

async def async_setup(hass, config):
    hass.http.register_view(ChatGptPluginManifestView)
    hass.http.register_view(ChatGptPluginDescriptionView)
    hass.http.register_view(APIEntitiesView)
    return True

class ChatGptPluginManifestView(HomeAssistantView):
    url = "/.well-known/ai-plugin.json"
    name = "ChatGPT plugin manifest"
    requires_auth = False

    async def get(self, request: Request) -> Response:
        dirname = os.path.dirname(__file__)
        filename = os.path.join(dirname, "openai-manifest.json")
        with open(filename, 'r') as f:
            data = f.read()
        return Response(text=data, headers={"Content-Type": "application/json"})


class ChatGptPluginDescriptionView(HomeAssistantView):
    url = "/chatgpt/openapi.yaml"
    name = "ChatGPT OpenAPI description"
    requires_auth = False

    async def get(self, request: Request) -> Response:
        dirname = os.path.dirname(__file__)
        filename = os.path.join(dirname, "openapi.yaml")
        with open(filename, 'r') as f:
            data = f.read()
        return Response(text=data, headers={"Content-Type": "application/x-yaml"})
        
class APIEntitiesView(HomeAssistantView):
    url = "/api/chatgpt/entities"
    name = "api:chatgpt:entities"

    async def get(self, request: Request) -> Response:
        """Get current entities."""
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
                **({'name': state.attributes.get('friendly_name')} if state.attributes.get('friendly_name') is not None else {}),
                **({'current_temperature': state.attributes.get('current_temperature')} if state.attributes.get('current_temperature') is not None else {}),
                **({'temperature': state.attributes.get('temperature')} if state.attributes.get('temperature') is not None else {}),
                **({'unit': state.attributes.get('unit_of_measurement')} if state.attributes.get('unit_of_measurement') is not None else {}),
                **({'device_class': state.attributes.get('device_class')} if state.attributes.get('device_class') is not None else {}),
                **({'state_class': state.attributes.get('state_class')} if state.attributes.get('state_class') is not None else {}),
            }
            for state in request.app["hass"].states.async_all()
            if (len(included_domains) == 0 or state.entity_id.split('.')[0] in included_domains) and entity_perm(state.entity_id, "read")
        ]
        return self.json(entities)
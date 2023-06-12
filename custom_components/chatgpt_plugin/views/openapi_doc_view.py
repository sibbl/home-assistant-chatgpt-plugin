import os
from aiohttp.web import Request, Response
from homeassistant.components.http import HomeAssistantView

class OpenApiDocView(HomeAssistantView):
    url = "/chatgpt/openapi.yaml"
    name = "ChatGPT OpenAPI description"
    requires_auth = False

    def __init__(self, base_url = None):
        super().__init__()
        self.base_url = base_url

    def set_base_url(self, base_url):
        self.base_url = base_url

    async def get(self, request: Request) -> Response:
        dirname = os.path.dirname(__file__)
        filename = os.path.join(dirname, "../templates/openapi_doc.yaml")
        with open(filename, 'r') as f:
            data = f.read()
        data = data.replace("{{BASE_URL}}", self.base_url or request.app["hass"].config.external_url)
        return Response(text=data, headers={"Content-Type": "application/x-yaml"})
        
# as long as we cannot unregister or replace views, we need to use this singleton instance
openapi_doc_view_instance = OpenApiDocView()
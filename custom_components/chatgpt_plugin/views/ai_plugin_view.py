import os
from aiohttp.web import Request, Response
from homeassistant.components.http import HomeAssistantView

class AiPluginView(HomeAssistantView):
    url = "/.well-known/ai-plugin.json"
    name = "ChatGPT plugin manifest"
    requires_auth = False
    
    def __init__(self, base_url = None, verification_token = None):
        super().__init__()
        self.base_url = base_url
        self.verification_token = verification_token

    def set_base_url(self, base_url):
        self.base_url = base_url

    def set_verification_token(self, verification_token):
        self.verification_token = verification_token

    async def get(self, request: Request) -> Response:
        dirname = os.path.dirname(__file__)
        filename = os.path.join(dirname, "../templates/ai_plugin.json")
        with open(filename, 'r') as f:
            data = f.read()
        data = data.replace("{{BASE_URL}}", self.base_url or request.app["hass"].config.external_url)
        data = data.replace("{{OPENAI_VERIFICATION_TOKEN}}", self.verification_token or "set up is in progress")
        return Response(text=data, headers={"Content-Type": "application/json"})

print("new AiPluginView instance")
# as long as we cannot unregister or replace views, we need to use this singleton instance
ai_plugin_view_instance = AiPluginView()
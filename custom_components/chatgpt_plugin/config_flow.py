from homeassistant import config_entries
from .const import CONF_BASE_URL, CONF_OPENAI_VERIFICATION_TOKEN, DOMAIN, UNIQUE_ID
import voluptuous as vol
from .views.ai_plugin_view import ai_plugin_view_instance


class ChatGptPluginConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    async def async_step_user(self, user_input=None):
        """Step 1: ask for the external URL"""
        await self.async_set_unique_id(UNIQUE_ID)
        self._abort_if_unique_id_configured()
        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_BASE_URL,
                        default=self.hass.config.external_url
                    ): str
                }
            )
        )
    async def async_step_init(self, user_input=None):
        """Step 2: store base url + ask for verification token"""
        if(user_input is None or user_input[CONF_BASE_URL] is None):
            return self.async_abort(reason="missing_input")
        self.init_base_url = user_input[CONF_BASE_URL]
        self.hass.http.register_view(ai_plugin_view_instance)
        return self.async_show_form(
            step_id="verification_token",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_OPENAI_VERIFICATION_TOKEN
                    ): str
                }
            )
        )

    async def async_step_verification_token(self, user_input=None):
        """Step 3: store verification token + create entry"""
        if(user_input is None or user_input[CONF_OPENAI_VERIFICATION_TOKEN] is None):
            return self.async_abort(reason="missing_input")
        if(self.init_base_url is None):
            return self.async_abort(reason="invalid_state")
        await self.async_set_unique_id(UNIQUE_ID)
        verification_token = user_input[CONF_OPENAI_VERIFICATION_TOKEN]
        ai_plugin_view_instance.set_verification_token(verification_token)
        return self.async_create_entry(
            title="ChatGPT plugin",
            data={
                CONF_BASE_URL: self.init_base_url,
                CONF_OPENAI_VERIFICATION_TOKEN: verification_token
            }
        )
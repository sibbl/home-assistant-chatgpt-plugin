# Home Assistant ChatGPT plugin

This is a protoypical implementation of a Home Assistant ChatGPT plugin. It currently only supports reading entities.

## Setup

1. Ensure that the `api:` component is enabled for your Home Assistant instance
1. Download the `custom_components` directory of this repository
1. Open the `/config/custom_componens/chatgpt_plugin/openai-manifest.json`
1. Replace `{HASS_BASE_URL}` with the public URL of your instance. It must be accessible from the internet and cannot be an internal network address like `192.168.x.x`
1. Save but leave the file open
1. Go to [GPT-4 with plugins](https://chat.openai.com/?model=gpt-4-plugins) and open the Plug-in store
1. Select "Develop your own plugin" at the bottom right of the dialog
1. Enter the value you used for `{HASS_BASE_URL}` above and continue
1. When asked, enter the following values and continue:
   * `clientId` must be set to `https://chat.openai.com`
   * `clientSecret` can be set to any value like `1234`
1. Open the `openai-manifest.json` again and replace `{OPENAI_VERIFICATION_TOKEN}` with the value ChatGPT generated for validation purposes and displays in the dialog (i.e. set the value `XYZ` when `{"openai":"XYZ"}` is displayed)
1. Click "Verify tokens" and login with your Home Assistant account
1. Start chatting 🚀

## Roadmap

* [ ] easier setup flow as integration 
* [ ] make fetching entities more robust
* [ ] support calling services
* [ ] add room and area information
* [ ] use intent REST API endpoint
* [ ] use templating REST API endpoint
* [ ] add managing automations
* [ ] add managing scripts

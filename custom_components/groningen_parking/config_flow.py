"""Config flow for the Groningen Parking component."""
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_USERNAME, CONF_PASSWORD
from .const import DOMAIN, CONF_LICENSE_PLATE, API_BASE
import requests

class GroningenParkingConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Groningen Parking."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}
        if user_input is not None:
            # Validate the input
            if await self._validate_credentials(
                    user_input[CONF_USERNAME], user_input[CONF_PASSWORD]
            ):
                return self.async_create_entry(
                    title=user_input[CONF_LICENSE_PLATE], data=user_input
                )
            errors["base"] = "invalid_auth"

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_USERNAME): str,
                    vol.Required(CONF_PASSWORD): str,
                    vol.Required(CONF_LICENSE_PLATE): str,
                }
            ),
            errors=errors,
        )

    async def _validate_credentials(self, username, password):
        """Validate the given credentials."""
        url = f"{API_BASE}/login"
        data = {
            "identifier": username,
            "loginMethod": "Pas",
            "permitMediaTypeID": 1,
            "password": password,
        }

        def make_request():
            try:
                response = requests.post(url, json=data)
                response.raise_for_status()

                return response.json().get("Token") is not None
            except requests.RequestException:
                return False

        return await self.hass.async_add_executor_job(make_request)
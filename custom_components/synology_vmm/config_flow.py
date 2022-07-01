"""Config flow to configure VMM."""
import logging

import voluptuous as vol
from homeassistant.config_entries import ConfigFlow
from homeassistant.const import CONF_IP_ADDRESS, CONF_PASSWORD, CONF_PORT, CONF_USERNAME
from homeassistant.helpers import selector
from synology_dsm import SynologyDSM

from .consts import DOMAIN

DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_IP_ADDRESS): selector.TextSelector(),
        vol.Required(CONF_PORT): selector.TextSelector(),
        vol.Required(CONF_USERNAME): selector.TextSelector(),
        vol.Required(CONF_PASSWORD): selector.TextSelector(
            selector.TextSelectorConfig(type=selector.TextSelectorType.PASSWORD)
        ),
    }
)

_LOGGER = logging.getLogger(__name__)


class SynoVMMFlowHandler(ConfigFlow, domain=DOMAIN):
    """Handle a Syno config flow."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle a flow initialized by the user."""
        errors = {}
        if user_input is not None:
            self._async_abort_entries_match(
                {
                    CONF_USERNAME: user_input[CONF_USERNAME],
                    CONF_IP_ADDRESS: user_input[CONF_IP_ADDRESS],
                }
            )
            try:
                api = SynologyDSM(
                    user_input[CONF_IP_ADDRESS],
                    user_input[CONF_PORT],
                    user_input[CONF_USERNAME],
                    user_input[CONF_PASSWORD],
                    use_https=False,
                    verify_ssl=False,
                    timeout=None,
                    device_token=None,
                    debugmode=False,
                )
                await self.hass.async_add_executor_job(api.information.update)
            except Exception as er:
                _LOGGER.error(er)
                errors["base"] = "cannot_connect"
            return self.async_create_entry(title=DOMAIN, data=user_input)

        return self.async_show_form(
            step_id="user", data_schema=DATA_SCHEMA, errors=errors
        )

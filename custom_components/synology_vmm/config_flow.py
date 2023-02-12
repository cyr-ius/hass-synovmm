"""Config flow to configure Synology virtual machine."""
import logging

from synology_dsm import SynologyDSM, SynologyDSMException
import voluptuous as vol

from homeassistant.config_entries import ConfigFlow
from homeassistant.const import (
    CONF_IP_ADDRESS,
    CONF_PASSWORD,
    CONF_PORT,
    CONF_SSL,
    CONF_TIMEOUT,
    CONF_USERNAME
)
from homeassistant.helpers import selector
from homeassistant.helpers.aiohttp_client import async_create_clientsession

from .const import DOMAIN

DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_IP_ADDRESS): selector.TextSelector(),
        vol.Required(CONF_PORT, default=5000): selector.NumberSelector(
            selector.NumberSelectorConfig(
                min=1, max=65035, step=1, mode=selector.NumberSelectorMode.BOX
            )
        ),
        vol.Required(CONF_USERNAME): selector.TextSelector(),
        vol.Required(CONF_PASSWORD): selector.TextSelector(
            selector.TextSelectorConfig(type=selector.TextSelectorType.PASSWORD)
        ),
        vol.Required(CONF_TIMEOUT, default=60): selector.NumberSelector(
            selector.NumberSelectorConfig(
                min=0, max=180, step=1, mode=selector.NumberSelectorMode.BOX
            )
        ),
        vol.Required(CONF_SSL, default=False): selector.BooleanSelector(),
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
                user_input[CONF_PORT] = int(user_input[CONF_PORT])
                user_input[CONF_TIMEOUT] = int(user_input[CONF_TIMEOUT])
                api = SynologyDSM(
                    async_create_clientsession(self.hass),
                    user_input[CONF_IP_ADDRESS],
                    user_input[CONF_PORT],
                    user_input[CONF_USERNAME],
                    user_input[CONF_PASSWORD],
                    use_https=user_input[CONF_SSL],
                    timeout=user_input[CONF_TIMEOUT],
                    device_token=None,
                    debugmode=False,
                )
                await api.information.update()
            except SynologyDSMException as error:
                _LOGGER.error(error)
                errors["base"] = "cannot_connect"
            else:
                return self.async_create_entry(
                    title=f"{user_input[CONF_IP_ADDRESS]} ({user_input[CONF_USERNAME]})",
                    data=user_input,
                )

        return self.async_show_form(
            step_id="user", data_schema=DATA_SCHEMA, errors=errors
        )

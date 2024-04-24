"""Config flow for MCP23017 component."""

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback

from .const import (
    DOMAIN,
    CONF_FLOW_PLATFORM,
    CONF_I2C_BUS,
    CONF_DEFAULT_I2C_BUS,
    CONF_DEFAULT_ADDRESS,
    CONF_I2C_ADDRESS,
    CONF_PINS,
    CONF_FLOW_PIN_NUMBER,
    CONF_FLOW_PIN_NAME,
    CONF_GAIN,
    CONF_GAIN_DEFAULT,
    CONF_GAINS
)

PLATFORMS = ["sensor"]


class ADS1115ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """ADS1115 config flow."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_LOCAL_POLL

    def _title(self, user_input):
        return "[%d]0x%02x:pin %d ('%s')" % (
            user_input[CONF_I2C_BUS],
            user_input[CONF_I2C_ADDRESS],
            user_input[CONF_FLOW_PIN_NUMBER],
            user_input[CONF_FLOW_PIN_NAME],
        )

    def _unique_id(self, user_input):
        return "%s.%d.%d.%d" % (
            DOMAIN,
            user_input[CONF_I2C_BUS],
            user_input[CONF_I2C_ADDRESS],
            user_input[CONF_FLOW_PIN_NUMBER],
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Add support for config flow options."""
        return ADS1115OptionsFlowHandler(config_entry)

    async def async_step_import(self, user_input=None):
        """Create a new entity from configuration.yaml import."""

        config_entry =  await self.async_set_unique_id(self._unique_id(user_input))
        # Remove entry (from storage) matching the same unique id
        if config_entry:
            self.hass.config_entries.async_remove(config_entry.entry_id)

        return self.async_create_entry(
            title=self._title(user_input),
            data=user_input,
        )


    async def async_step_user(self, user_input=None):
        """Create a new entity from UI."""

        if user_input is not None:
            await self.async_set_unique_id(self._unique_id(user_input))
            self._abort_if_unique_id_configured()

            if CONF_FLOW_PIN_NAME not in user_input:
                user_input[CONF_FLOW_PIN_NAME] = "bus %d pin 0x%02x:%d" % (
                    user_input[CONF_I2C_BUS],
                    user_input[CONF_I2C_ADDRESS],
                    user_input[CONF_FLOW_PIN_NUMBER],
                )

            return self.async_create_entry(
                title=self._title(user_input),
                data=user_input,
            )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_I2C_BUS, default=CONF_DEFAULT_I2C_BUS
                    ): vol.All(vol.Coerce(int), vol.Range(min=0, max=1)),
                    vol.Required(
                        CONF_I2C_ADDRESS, default=CONF_DEFAULT_ADDRESS
                    ): vol.All(vol.Coerce(int), vol.Range(min=72, max=75)),

                    vol.Required(CONF_FLOW_PIN_NUMBER, default=0): vol.All(
                        vol.Coerce(int), vol.Range(min=0, max=3)
                    ),
                    vol.Optional(CONF_FLOW_PIN_NAME): str,
                }
            ),
        )

class ADS1115OptionsFlowHandler(config_entries.OptionsFlow):
    """ADS1115 config flow options."""

    def __init__(self, config_entry):
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Manage entity options."""

        if user_input is not None:

            return self.async_create_entry(title="", data=user_input)

        data_schema = vol.Schema(
            {
                vol.Optional(
                    CONF_GAIN,
                    default=self.config_entry.options.get(
                        CONF_GAIN, CONF_GAIN_DEFAULT
                    ),
                ): vol.In(CONF_GAINS),
            }
        )
        return self.async_show_form(step_id="init", data_schema=data_schema)

""" Implements the Tuto HACS sensors component """
import logging

from homeassistant.const import UnitOfElectricPotential
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry

from homeassistant.helpers.entity_platform import (
    AddEntitiesCallback,
    async_get_current_platform,
)
from homeassistant.components.sensor import (
    SensorEntity,
    SensorDeviceClass,
    SensorStateClass,
)
from homeassistant.helpers.entity import DeviceInfo#, DeviceEntryType

from .const import DOMAIN, CONF_FLOW_PIN_NAME,CONF_I2C_BUS,CONF_I2C_ADDRESS,CONF_FLOW_PIN_NUMBER

from . import async_get_or_create

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
    discovery_info=None,  # pylint: disable=unused-argument
):
    """Configuration de la plate-forme tuto_hacs à partir de la configuration
    trouvée dans configuration.yaml"""

    _LOGGER.debug("Calling async_setup_entry entry=%s", entry)

    entity = ADS1115Sensor(hass, entry)
    async_add_entities([entity], True)
    platform = async_get_current_platform()
    await async_get_or_create(hass, entity  )


class ADS1115Sensor(SensorEntity):
    """La classe de l'entité ADS1115Sensor"""

    def __init__(
        self,
        hass: HomeAssistant,  # pylint: disable=unused-argument
        entry_infos,  # pylint: disable=unused-argument
    ) -> None:
        """Initisalisation de notre entité"""
        self._state=15
        self._hass = hass
        self._entry_infos=entry_infos
        self._attr_has_entity_name = True
        self._attr_name = entry_infos.data.get(CONF_FLOW_PIN_NAME)
        self._bus = entry_infos.data.get(CONF_I2C_BUS)
        self._i2c_address = entry_infos.data.get(CONF_I2C_ADDRESS)
        self._pin = entry_infos.data.get(CONF_FLOW_PIN_NUMBER)

    @property
    def unique_id(self):
        """Return unique id"""
        return f"{self._bus}-0x{self._i2c_address:02x}-{self._pin}"

    @property
    def state(self):
        """Returns state of the sensor."""
        return self._state

    @property
    def bus(self):
        return self._bus

    @property
    def address(self):
        return self._i2c_address

    @property
    def pin(self):
        return self._pin

    @property
    def should_poll(self) -> bool:
        """Poll for those entities"""
        return True

    @property
    def icon(self) -> str | None:
        return "mdi:sine-wave"

    @property
    def device_class(self) -> SensorDeviceClass | None:
        return SensorDeviceClass.VOLTAGE

    @property
    def state_class(self) -> SensorStateClass | None:
        return SensorStateClass.MEASUREMENT

    @property
    def native_unit_of_measurement(self) -> str | None:
        return UnitOfElectricPotential.MILLIVOLT


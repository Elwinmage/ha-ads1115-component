""" Implements the Tuto HACS sensors component """
import logging

from homeassistant.const import UnitOfTime
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.components.sensor import (
    SensorEntity,
    SensorDeviceClass,
    SensorStateClass,
)

from homeassistant.helpers.entity import DeviceInfo, DeviceEntryType

from .const import DOMAIN, DEVICE_MANUFACTURER, CONF_DEVICE_ID, CONF_NAME

_LOGGER = logging.getLogger(__name__)


async def async_setup_platform(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
    discovery_info=None,  # pylint: disable=unused-argument
):
    """Configuration de la plate-forme tuto_hacs à partir de la configuration
    trouvée dans configuration.yaml"""

    _LOGGER.debug("Calling async_setup_entry entry=%s", entry)

    entity = TutoHacsElapsedSecondEntity(hass, entry)
    async_add_entities([entity], True)


class TutoHacsElapsedSecondEntity(SensorEntity):
    """La classe de l'entité TutoHacs"""

    def __init__(
        self,
        hass: HomeAssistant,  # pylint: disable=unused-argument
        entry_infos,  # pylint: disable=unused-argument
    ) -> None:
        """Initisalisation de notre entité"""
        self._attr_has_entity_name = True
        self._attr_name = entry_infos.get(CONF_NAME)
        self._device_id = entry_infos.get(CONF_DEVICE_ID) # Pas utilisé pour le moment
        self._attr_unique_id = self._device_id + "_seconds"
        self._attr_native_value = 12

    @property
    def should_poll(self) -> bool:
        """Do not poll for those entities"""
        return False

    @property
    def icon(self) -> str | None:
        return "mdi:timer-play"

    @property
    def device_class(self) -> SensorDeviceClass | None:
        return SensorDeviceClass.DURATION

    @property
    def state_class(self) -> SensorStateClass | None:
        return SensorStateClass.MEASUREMENT

    @property
    def native_unit_of_measurement(self) -> str | None:
        return UnitOfTime.SECONDS

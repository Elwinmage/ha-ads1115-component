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
from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo

from .const import DOMAIN, CONF_FLOW_PIN_NAME,CONF_I2C_ADDRESS,CONF_FLOW_PIN_NUMBER,CONF_GAIN, CONF_GAIN_DEFAULT, CONF_DEVICE_ID,DEVICE_MANUFACTURER

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
        self._state=None
        self._hass = hass
        self._entry_infos=entry_infos
        self._attr_has_entity_name = True
        self._attr_name = entry_infos.data.get(CONF_FLOW_PIN_NAME)
        self._i2c_address = entry_infos.data.get(CONF_I2C_ADDRESS)
        self._pin = entry_infos.data.get(CONF_FLOW_PIN_NUMBER)
#        self._device_id = self.unique_id
        self._gain = entry_infos.data.get(CONF_GAIN)
        if self._gain == None:
            self._gain = CONF_GAIN_DEFAULT
        self._read_request=[((((((1 ) <<  3) + self.pinNumber)<<3)+(self.gainNumber))<<1),0x83]
        
    @property
    def device_info(self) -> DeviceInfo:
        """Return the device info."""
        return DeviceInfo(
            entry_type=DeviceEntryType.SERVICE,
            identifiers={(DOMAIN,self.address)},
            name=self.address,
#            identifiers={(DOMAIN,self._device_id)},
#            name=self._device_id,
            manufacturer=DEVICE_MANUFACTURER,
            model=DOMAIN,
        )

    @property
    def readRequest(self):
        """Return bytes to send for reading"""
        return self._read_request
        
    @property
    def unique_id(self):
        """Return unique id"""
        return f"{self._i2c_address}-{self.pin}"

    def set_state(self,state):
        """Set state"""
        self._state = state
        _LOGGER.debug("%s:%f"%(self.unique_id,state))
        
    @property
    def state(self):
        """Returns state of the sensor."""
        return self._state

    @property
    def address(self):
        return self._i2c_address

    @property
    def pin(self):
        return self._pin

    @property
    def pinNumber(self):
        return int(self._pin[0])

    @property
    def gainNumber(self):
        return int(self._gain[0])

    @property
    def gainValue(self):
        return float(self._gain[2:])

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
        return UnitOfElectricPotential.VOLT


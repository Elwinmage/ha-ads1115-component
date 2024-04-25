import logging
import asyncio
import functools
import threading
import time

import smbus2

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers import device_registry
from homeassistant.const import EVENT_HOMEASSISTANT_START, EVENT_HOMEASSISTANT_STOP
from .const import DOMAIN, PLATFORMS, DEFAULT_SCAN_RATE

_LOGGER = logging.getLogger(__name__)
ADS1115_DATA_LOCK = asyncio.Lock()

async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up the ADS1115 component."""
    # hass.data[DOMAIN] stores one entry for each MCP23017 instance using i2c address as a key
    hass.data.setdefault(DOMAIN, {})

    # Callback function to start polling when HA starts
    def start_polling(event):
        for component in hass.data[DOMAIN].values():
            if not component.is_alive():
                component.start_polling()

    # Callback function to stop polling when HA stops
    def stop_polling(event):
        for component in hass.data[DOMAIN].values():
            if component.is_alive():
                component.stop_polling()

    hass.bus.async_listen_once(EVENT_HOMEASSISTANT_START, start_polling)
    hass.bus.async_listen_once(EVENT_HOMEASSISTANT_STOP, stop_polling)
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Creation des entités à partir d'une configEntry"""

    _LOGGER.debug(
        "Appel de async_setup_entry entry: entry_id='%s', data='%s'",
        entry.entry_id,
        entry.data,
    )

    hass.data.setdefault(DOMAIN, {})
    entry.async_on_unload(entry.add_update_listener(update_listener))
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

   # Callback function to start polling when HA start
    def start_polling(event):
        for component in hass.data[DOMAIN].values():
            if not component.is_alive():
                component.start_polling()

    # Callback function to stop polling when HA stops
    def stop_polling(event):
        for component in hass.data[DOMAIN].values():
            if component.is_alive():
                component.stop_polling()
    return True

async def update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Fonction qui force le rechargement des entités associées à une configEntry"""
    await hass.config_entries.async_reload(entry.entry_id)

async def async_get_or_create(hass, entity):
    """Get or create a ADS115 component from entity bus and i2c address."""

    i2c_address = entity.address
    i2c_component = i2c_address
    # DOMAIN data async mutex
    try:
        async with ADS1115_DATA_LOCK:
            if i2c_address in hass.data[DOMAIN]:
                component = hass.data[DOMAIN][i2c_component]
            else:
                # Try to create component when it doesn't exist
                component = await hass.async_add_executor_job(
                    functools.partial(ADS1115, i2c_address)
                )
                hass.data[DOMAIN][i2c_component] = component

                # Start polling thread if hass is already running
                if hass.is_running:
                    component.start_polling()

                # Register a device combining all related entities
                devices = device_registry.async_get(hass)
                devices.async_get_or_create(
                    config_entry_id=entity._entry_infos.entry_id,
                    identifiers={(DOMAIN, i2c_component)},
                    model=DOMAIN,
                    name=f"{DOMAIN}{i2c_address}",
                )

            # Link entity to component
            await hass.async_add_executor_job(
                functools.partial(component.register_entity, entity)
            )
    except ValueError as error:
        component = None
        await hass.config_entries.async_remove(entity._entry_infos.entry_id)

        hass.components.persistent_notification.create(
            f"Error: Unable to access {DOMAIN}{i2c_address} ({error})",
            title=f"{DOMAIN} Configuration",
            notification_id=f"{DOMAIN} notification",
        )

    return component



class ADS1115(threading.Thread):
    """ADS1115 component (device)"""
    def __init__(self, address):
        # Address is this form /dev/i2c-1@0x48
        self._bus      = int(address.split('@')[0][-1])
        self._address  = int(address.split('@')[1],16)
        self._full_address = address
        self._entities = [None for i in range(8)]
        self._device_lock = threading.Lock()
        self._run = False
        threading.Thread.__init__(self, name=self.unique_id)
        _LOGGER.info("%s device created", self.unique_id)

    def __enter__(self):
        """Lock access to device (with statement)."""
        self._device_lock.acquire()
        return self

    def __exit__(self, exception_type, exception_value, exception_traceback):
        """Unlock access to device (with statement)."""
        self._device_lock.release()
        return False


    @property
    def unique_id(self):
        """Return component unique id."""
        return f"{DOMAIN}{self._full_address}"

    @property
    def address(self):
        """Return I2C address"""
        return self._address

    @property
    def bus(self):
        """Return i2c bus number"""
        return self._bus
    
    def start_polling(self):
        """Start polling thread."""
        self._run = True
        self.start()

    def stop_polling(self):
        """Stop polling thread."""
        self._run = False
        self.join()

    def run(self):
        _LOGGER.info("%s start polling thread", self.unique_id)
        bus = smbus2.SMBus(self._bus)
        while self._run:
            with self:
                for entity in self._entities:
                    if entity != None:
                        data = entity.readRequest
                        bus.write_i2c_block_data(self._address, 0x01, data)
                        _LOGGER.debug("request: %s"%(data))
                        time.sleep(0.5)
                        data = bus.read_i2c_block_data(self._address, 0x00, 2)
                        raw_adc = data[0] * 256 + data[1]
                        if raw_adc > 32767:
                          raw_adc -= 65535
                        v_p_b = entity.gainValue / 32768
                        voltage=raw_adc * v_p_b
                        _LOGGER.debug("raw: %d, gain %f, %fmV"%(raw_adc,entity.gainValue,voltage*1000))
                        entity.set_state(voltage)
                _LOGGER.debug("heartrate: %s",self.unique_id)
            time.sleep(DEFAULT_SCAN_RATE)

        _LOGGER.info("%s stop polling thread", self.unique_id)

    def register_entity(self, entity):
        """Register entity to this device instance."""
        with self:
            self._entities[entity.pinNumber] = entity

            _LOGGER.info(
                "%s(pin %s:'%s') attached to %s",
                type(entity).__name__,
                entity.pin,
                entity.name,
                self.unique_id,
            )

        return True



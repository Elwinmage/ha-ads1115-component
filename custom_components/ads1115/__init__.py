import logging
import asyncio
import functools
import threading
import time

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

    i2c_bus = entity.bus
    i2c_address = entity.address
    i2c_component = entity.bus*1000+i2c_address
    # DOMAIN data async mutex
    try:
        async with ADS1115_DATA_LOCK:
            if i2c_address in hass.data[DOMAIN]:
                component = hass.data[DOMAIN][i2c_component]
            else:
                # Try to create component when it doesn't exist
                component = await hass.async_add_executor_job(
                    functools.partial(ADS1115, i2c_bus, i2c_address)
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
                    name=f"{DOMAIN}[{i2c_bus}]@0x{i2c_address:02x}",
                )

            # Link entity to component
            await hass.async_add_executor_job(
                functools.partial(component.register_entity, entity)
            )
    except ValueError as error:
        component = None
        await hass.config_entries.async_remove(entity._entry_infos.entry_id)

        hass.components.persistent_notification.create(
            f"Error: Unable to access {DOMAIN}[{i2c_bus}]0x{i2c_address:02x} ({error})",
            title=f"{DOMAIN} Configuration",
            notification_id=f"{DOMAIN} notification",
        )

    return component



class ADS1115(threading.Thread):
    """ADS1115 component (device)"""
    def __init__(self, bus, address):
        self._bus = bus
        self._address = address
        self._entities = [None for i in range(4)]
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
        return f"{DOMAIN}[{self.bus}]0x{self.address:02x}"

    @property
    def bus(self):
        """Return I2C bus number"""
        return self._bus
    @property
    def address(self):
        """Return I2C address"""
        return self._address

    def start_polling(self):
        """Start polling thread."""
        self._run = True
        self.start()

    def stop_polling(self):
        """Stop polling thread."""
        self._run = False
        self.join()

    def run(self):
        """Poll all ports once and call corresponding callback if a change is detected."""

        _LOGGER.info("%s start polling thread", self.unique_id)
        gpio_port=""
        while self._run:
            with self:
                #for pin in range(4):
                #    self._entities[pin].
                _LOGGER.debug("heartrate: %s",self.unique_id)
            time.sleep(DEFAULT_SCAN_RATE)

        _LOGGER.info("%s stop polling thread", self.unique_id)

    def register_entity(self, entity):
        """Register entity to this device instance."""
        with self:
            self._entities[entity.pin] = entity

            # Trigger a callback to update initial state
            #self._update_bitmap |= (1 << entity.pin) & 0xFFFF

            _LOGGER.info(
                "%s(pin %d:'%s') attached to %s",
                type(entity).__name__,
                entity.pin,
                entity.name,
                self.unique_id,
            )

        return True



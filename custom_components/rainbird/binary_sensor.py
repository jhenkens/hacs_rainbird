"""Support for Rain Bird Irrigation system LNK WiFi Module."""
from __future__ import annotations

import logging

import homeassistant.helpers.config_validation as cv
import voluptuous as vol
from homeassistant.components.binary_sensor import PLATFORM_SCHEMA, BinarySensorEntity
from homeassistant.const import CONF_MONITORED_CONDITIONS
from pyrainbird import RainbirdController

from . import SENSOR_TYPES, DOMAIN, RuntimeEntryData

_LOGGER = logging.getLogger(__name__)

# sensor_type [ description, unit, icon ]

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Optional(CONF_MONITORED_CONDITIONS, default=list(SENSOR_TYPES)): vol.All(
            cv.ensure_list, [vol.In(SENSOR_TYPES)]
        )
    }
)


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up ESPHome binary sensors based on a config entry."""
    runtime_data = hass.data.get(DOMAIN)[config_entry.entry_id]
    config_entry_data = config_entry.data
    controller = runtime_data.client
    sensor = BiStateRainBirdSensor(controller, config_entry_data.get(CONF_MONITORED_CONDITIONS)[0], hass, runtime_data,
                                   config_entry.entry_id)
    async_add_entities([sensor], True)


class BiStateRainBirdSensor(BinarySensorEntity):
    """A sensor implementation for Rain Bird device."""

    def __init__(self, controller: RainbirdController, sensor_type, hass, data: RuntimeEntryData = None,
                 device_id=None):
        """Initialize the Rain Bird sensor."""
        self._data = data
        self._hass = hass
        self._sensor_type = sensor_type
        self._controller = controller
        self._name = SENSOR_TYPES[self._sensor_type][0]
        self._icon = SENSOR_TYPES[self._sensor_type][2]
        self._unit_of_measurement = SENSOR_TYPES[self._sensor_type][1]
        self._device_id = device_id

    def update(self):
        """Get the latest data and updates the states."""
        _LOGGER.debug("Updating sensor: %s", self._name)
        _attr_is_on = self._controller.get_rain_sensor_state()

    @property
    def name(self):
        """Return the name of this camera."""
        return self._name

    @property
    def unique_id(self):
        """Return Unique ID string."""
        return "%s_switch_%s" % (DOMAIN, self._sensor_type)

    @property
    def device_info(self):
        """Information about this entity/device."""

        return {
            "identifiers": {(DOMAIN, self._device_id)},
            # If desired, the name for the device could be different to the entity
            "name": "Rainbird controller",
            "sw_version": self._data.get_version(),
            "model": self._data.get_model(),
            "manufacturer": "Rainbird",
        }

    @property
    def unit_of_measurement(self):
        """Return the units of measurement."""
        return self._unit_of_measurement

    @property
    def icon(self):
        """Return icon."""
        return self._icon
"""Luas sensor"""
from __future__ import annotations
import logging

import typing
import voluptuous as vol

from homeassistant.components.sensor import (
    SensorEntity,
    PLATFORM_SCHEMA,
)
from homeassistant.const import TIME_MINUTES
from homeassistant.core import HomeAssistant
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType
from . import luasforecasts

_LOGGER = logging.getLogger(__name__)

CONF_STATION: typing.Final = "station"
CONF_DIRECTION: typing.Final = "direction"
CONF_DESTINATION: typing.Final = "destination"
CONF_NAME: typing.Final = "name"

DEFAULT_NAME: typing.Final = "Next Luas"

ATTR_MESSAGE = "Message"
ATTR_DUE_IN = "Due in"
ATTR_DESTINATION = "Destination"
ATTR_NEXT_DUE_IN = "Next due in"
ATTR_NEXT_DESTINATION = "Next destination"

ICON = "mdi:tram"

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_STATION): cv.string,
        vol.Optional(CONF_DIRECTION): cv.string,
        vol.Optional(CONF_DESTINATION): cv.string,
        vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
    }
)


def setup_platform(
    hass: HomeAssistant,  # pylint: disable=unused-argument
    config: ConfigType,
    add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None,  # pylint: disable=unused-argument
) -> None:
    """Set up the sensor platform."""
    add_entities([LuasSensor(config)])


class LuasSensor(SensorEntity):
    """Representation of a Sensor."""

    _attr_name = "LUAS"
    _attr_native_unit_of_measurement = TIME_MINUTES
    _attributes = {}

    def __init__(self, config: ConfigType) -> None:
        """Initialize a LuasSensor"""
        self._station = config[CONF_STATION]
        self._name = config[CONF_NAME]

        self._direction = config.get(CONF_DIRECTION, "").lower()
        self._destination = config.get(CONF_DESTINATION, "").lower()

    @property
    def icon(self):
        """Icon to use in the frontend, if any."""
        return ICON

    @property
    def extra_state_attributes(self):
        return self._attributes

    def _filter_trams(
        self, trams: list[luasforecasts.Tram]
    ) -> list[luasforecasts.Tram]:
        if self._direction:
            _LOGGER.debug("Filtering for direction: %s", self._direction)
            trams = [t for t in trams if t["direction"].lower() == self._direction]
        if self._destination:
            _LOGGER.debug("Filtering for destination: %s", self._destination)
            trams = [t for t in trams if t["destination"].lower() == self._destination]
        return trams

    def update(self) -> None:
        """Fetch new Luas data"""
        self._attr_native_value = ""
        self._attributes = {
            ATTR_MESSAGE: "",
            ATTR_DUE_IN: "",
            ATTR_DESTINATION: "",
            ATTR_NEXT_DUE_IN: "",
            ATTR_NEXT_DESTINATION: "",
        }

        data = luasforecasts.fetch(self._station)
        _LOGGER.debug("Got LUAS data: %s", data)

        self._attributes[ATTR_MESSAGE] = data["message"]
        self._attr_name = self._name

        relevant_trams = self._filter_trams(data["trams"])

        _LOGGER.debug("Relevant trams: %s", relevant_trams)

        if len(relevant_trams) > 0:
            due_mins = relevant_trams[0]["dueMins"]
            self._attributes.update(
                {
                    ATTR_DUE_IN: due_mins,
                    ATTR_DESTINATION: relevant_trams[0]["destination"],
                }
            )
            self._attr_native_value = due_mins

        if len(relevant_trams) > 1:
            self._attributes.update(
                {
                    ATTR_NEXT_DUE_IN: relevant_trams[1]["dueMins"],
                    ATTR_NEXT_DESTINATION: relevant_trams[1]["destination"],
                }
            )

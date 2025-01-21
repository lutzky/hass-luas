"""Sensor platform for luas."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.components.sensor import SensorEntity, SensorEntityDescription
from homeassistant.const import UnitOfTime

from .const import LOGGER
from .entity import LuasEntity

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from .api import Tram
    from .coordinator import LuasDataUpdateCoordinator
    from .data import LuasConfigEntry, LuasData


ENTITY_DESCRIPTIONS = (
    SensorEntityDescription(
        key="inbound_trams",
        name="Inbound trams",
        icon="mdi:tram",
    ),
    SensorEntityDescription(
        key="outbound_trams",
        name="Outbound trams",
        icon="mdi:tram",
    ),
)


async def async_setup_entry(
    _hass: HomeAssistant,
    entry: LuasConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the sensor platform."""
    async_add_entities(
        [
            LuasMessageSensor(
                coordinator=entry.runtime_data.coordinator,
                data=entry.runtime_data,
            )
        ]
    )
    async_add_entities(
        LuasTramSensor(
            coordinator=entry.runtime_data.coordinator,
            data=entry.runtime_data,
            direction=direction,
        )
        for direction in ["inbound", "outbound"]
    )


class LuasMessageSensor(LuasEntity, SensorEntity):
    """Sensor for showing the luas message."""

    _attr_has_entity_name = True
    _attr_icon = "mdi:tram"
    _attr_name = "Message"

    def __init__(
        self,
        coordinator: LuasDataUpdateCoordinator,
        data: LuasData,
    ) -> None:
        """Initialize the sensor class."""
        super().__init__(coordinator, data=data)
        self._attr_unique_id = f"{self.device_id}_message"

    @property
    def native_value(self) -> str | None:
        """Native value for the sensor is the Luas station message."""
        return self.coordinator.data.get("message")


class LuasTramSensor(LuasEntity, SensorEntity):
    """Sensor for showing Luas trams."""

    _attr_icon = "mdi:tram"
    _attr_has_entity_name = True
    _attr_native_unit_of_measurement = UnitOfTime.MINUTES

    direction: str

    def __init__(
        self,
        coordinator: LuasDataUpdateCoordinator,
        data: LuasData,
        direction: str,
    ) -> None:
        """Initialize the sensor class."""
        super().__init__(coordinator, data=data)
        self.direction = direction
        self._attr_unique_id = f"{self.device_id}_tram_{direction}"

    @property
    def name(self) -> str:
        """Name for Luas trams sensor."""
        return f"Next tram {self.direction}"

    def _trams_in_direction(self) -> list[Tram]:
        all_trams = self.coordinator.data.get("trams", [])
        result = [
            tram
            for tram in all_trams
            if tram["direction"].upper() == self.direction.upper()
            and (
                self.data.translated_destination is None
                or self.data.translated_destination.upper()
                == tram["destination"].upper()
            )
        ]
        LOGGER.debug(
            "%r: All trams: %r\ndirection=%r, destination=%r\nFiltered trams:%r",
            self._attr_unique_id,
            all_trams,
            self.direction,
            self.data.translated_destination,
            result,
        )

        return result

    @property
    def native_value(self) -> int | None:
        """Native value for the sensor is due minutes for next tram."""
        trams = self._trams_in_direction()
        if len(trams) == 0:
            return None
        return trams[0]["dueMins"]

    @property
    def extra_state_attributes(self) -> dict[str, str | int | None]:
        """Return the state attributes."""
        trams = self._trams_in_direction()
        return {
            "destination": trams[0]["destination"] if len(trams) > 0 else None,
            "next_due": trams[1]["dueMins"] if len(trams) > 1 else None,
            "next_destination": trams[1]["destination"] if len(trams) > 1 else None,
        }

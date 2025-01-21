"""LuasEntity class."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import ATTRIBUTION
from .coordinator import LuasDataUpdateCoordinator

if TYPE_CHECKING:
    from .data import LuasData


class LuasEntity(CoordinatorEntity[LuasDataUpdateCoordinator]):
    """Luas entity base class."""

    _attr_attribution = ATTRIBUTION
    translated_station: str
    device_id: str
    data: LuasData

    def __init__(
        self,
        coordinator: LuasDataUpdateCoordinator,
        data: LuasData,
    ) -> None:
        """Initialize."""
        super().__init__(coordinator)
        self.data = data
        self.device_id = f"luas_{data.station}" + (
            f"_to_{data.destination}" if data.destination else ""
        )
        self._attr_device_info = DeviceInfo(
            name=f"Luas {data.translated_station}"
            + (
                f" to {data.translated_destination}"
                if data.translated_destination
                else ""
            ),
            identifiers={
                (
                    coordinator.config_entry.domain,
                    coordinator.config_entry.entry_id,
                ),
            },
        )

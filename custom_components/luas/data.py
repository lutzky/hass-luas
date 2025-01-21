"""Custom types for Luas."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.loader import Integration

    from .api import LuasApiClient
    from .coordinator import LuasDataUpdateCoordinator


type LuasConfigEntry = ConfigEntry[LuasData]


@dataclass
class LuasData:
    """Data for the Luas integration."""

    client: LuasApiClient
    coordinator: LuasDataUpdateCoordinator
    integration: Integration
    station: str
    translated_station: str
    destination: str | None
    translated_destination: str | None

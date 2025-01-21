"""
Custom integration to integrate luas with Home Assistant.

For more details about this integration, please refer to
https://github.com/lutzky/hass-luas
"""

from __future__ import annotations

from datetime import timedelta
from typing import TYPE_CHECKING

from homeassistant.const import Platform
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.loader import async_get_loaded_integration

from .api import LuasApiClient
from .const import (
    CONF_DESTINATION,
    CONF_STATION,
    DOMAIN,
    LOGGER,
    async_translate_station_name,
)
from .coordinator import LuasDataUpdateCoordinator
from .data import LuasData

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant

    from .data import LuasConfigEntry

PLATFORMS: list[Platform] = [
    Platform.SENSOR,
]


# https://developers.home-assistant.io/docs/config_entries_index/#setting-up-an-entry
async def async_setup_entry(
    hass: HomeAssistant,
    entry: LuasConfigEntry,
) -> bool:
    """Set up this integration using UI."""
    coordinator = LuasDataUpdateCoordinator(
        hass=hass,
        logger=LOGGER,
        name=DOMAIN,
        update_interval=timedelta(hours=1),
    )
    entry.runtime_data = LuasData(
        client=LuasApiClient(
            station=entry.data[CONF_STATION],
            session=async_get_clientsession(hass),
        ),
        station=entry.data[CONF_STATION],
        translated_station=await async_translate_station_name(
            hass, entry.data[CONF_STATION]
        ),
        destination=entry.data.get(CONF_DESTINATION, None),
        translated_destination=await async_translate_station_name(
            hass, entry.data[CONF_DESTINATION]
        )
        if CONF_DESTINATION in entry.data
        else None,
        integration=async_get_loaded_integration(hass, entry.domain),
        coordinator=coordinator,
    )

    # https://developers.home-assistant.io/docs/integration_fetching_data#coordinated-single-api-poll-for-data-for-all-entities
    await coordinator.async_config_entry_first_refresh()

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(async_reload_entry))

    return True


async def async_unload_entry(
    hass: HomeAssistant,
    entry: LuasConfigEntry,
) -> bool:
    """Handle removal of an entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


async def async_reload_entry(
    hass: HomeAssistant,
    entry: LuasConfigEntry,
) -> None:
    """Reload config entry."""
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)

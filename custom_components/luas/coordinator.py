"""DataUpdateCoordinator for luas."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import (
    LuasApiClientError,
)

if TYPE_CHECKING:
    from .data import LuasConfigEntry


# https://developers.home-assistant.io/docs/integration_fetching_data#coordinated-single-api-poll-for-data-for-all-entities
class LuasDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the API."""

    config_entry: LuasConfigEntry

    async def _async_update_data(self) -> Any:
        """Update data via library."""
        try:
            return await self.config_entry.runtime_data.client.async_get_data()
        except LuasApiClientError as exception:
            raise UpdateFailed(exception) from exception

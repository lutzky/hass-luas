"""Adds config flow for Luas."""

from __future__ import annotations

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.helpers import selector, translation
from slugify import slugify

from .const import (
    CONF_DESTINATION,
    CONF_STATION,
    DOMAIN,
    LUAS_STATIONS,
    async_translate_station_name,
)


class LuasConfigFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for Luas."""

    VERSION = 1

    def _get_unique_id(self, user_input: dict) -> str:
        return slugify(
            f"luas-{user_input[CONF_STATION]}"
            + (
                f"-to-{user_input[CONF_DESTINATION]}"
                if CONF_DESTINATION in user_input
                else ""
            )
        )

    async def _translate_station_name(self, station: str) -> str:
        translations = await translation.async_get_translations(
            self.hass, self.hass.config.language, "selector", {DOMAIN}
        )
        return translations.get(
            f"component.luas.selector.station.options.{station}",
            station,
        )

    async def async_step_user(
        self,
        user_input: dict | None = None,
    ) -> config_entries.ConfigFlowResult:
        """Handle a flow initialized by the user."""
        _errors = {}
        if user_input is not None:
            await self.async_set_unique_id(self._get_unique_id(user_input))
            self._abort_if_unique_id_configured()
            translated_station = await async_translate_station_name(
                self.hass, user_input[CONF_STATION]
            )
            if CONF_DESTINATION in user_input:
                destination = await async_translate_station_name(
                    self.hass, user_input[CONF_DESTINATION]
                )
            else:
                destination = None
            return self.async_create_entry(
                title=(
                    translated_station
                    + ("" if not destination else f" to {destination}")
                ),
                data=user_input,
            )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_STATION,
                    ): selector.selector(
                        {
                            "select": {
                                "translation_key": "station",
                                "options": LUAS_STATIONS,
                                "sort": True,
                            },
                        }
                    ),
                    vol.Optional(
                        CONF_DESTINATION,
                    ): selector.selector(
                        {
                            "select": {
                                "translation_key": "station",
                                "options": LUAS_STATIONS,
                                "sort": True,
                            },
                        }
                    ),
                },
            ),
            errors=_errors,
        )

"""Constants for luas."""

from logging import Logger, getLogger

from homeassistant.core import HomeAssistant
from homeassistant.helpers import translation

LOGGER: Logger = getLogger(__package__)

DOMAIN = "luas"
ATTRIBUTION = "Data provided by https://luasforecasts.rpa.ie/analysis/view.aspx"

CONF_STATION = "station"
CONF_DESTINATION = "destination"

LUAS_STATIONS = [
    # cSpell: disable  # noqa: ERA001
    # These are from https://luasforecasts.rpa.ie/analysis/view.aspx, in that
    # order. Heuston shows up as both HIN and HCT. Notably, homeassistant
    # translation requires them to be in lowercase.
    # Keep these in sync with translations/*.json
    "hin",  # Heuston HIN
    "hct",  # Heuston HCT
    "tpt",  # The Point
    "sdk",  # Spencer Dock
    "mys",  # Mayor Square - NCI
    "gdk",  # George's Dock
    "con",  # Connolly
    "bus",  # Busáras
    "abb",  # Abbey Street
    "jer",  # Jervis
    "fou",  # Four Courts
    "smi",  # Smithfield
    "mus",  # Museum
    "heu",  # Heuston
    "jam",  # James's
    "fat",  # Fatima
    "ria",  # Rialto
    "sui",  # Suir Road
    "gol",  # Goldenbridge
    "dri",  # Drimnagh
    "bla",  # Blackhorse
    "blu",  # Bluebell
    "kyl",  # Kylemore
    "red",  # Red Cow
    "kin",  # Kingswood
    "bel",  # Belgard
    "coo",  # Cookstown
    "hos",  # Hospital
    "tal",  # Tallaght
    "fet",  # Fettercairn
    "cvn",  # Cheeverstown
    "cit",  # Citywest Campus
    "for",  # Fortunestown
    "sag",  # Saggart
    "dep",  # Depot
    "stx",  # St. Stephen's Green
    "bro",  # Broombridge
    "cab",  # Cabra
    "phi",  # Phibsborough
    "gra",  # Grangegorman
    "brd",  # Broadstone - University
    "dom",  # Dominick
    "par",  # Parnell
    "oup",  # O'Connell - Upper
    "ogp",  # O'Connell - GPO
    "mar",  # Marlborough
    "wes",  # Westmoreland
    "try",  # Trinity
    "daw",  # Dawson
    "sts",  # St. Stephen's Green
    "har",  # Harcourt
    "cha",  # Charlemont
    "ran",  # Ranelagh
    "bee",  # Beechwood
    "cow",  # Cowper
    "mil",  # Milltown
    "win",  # Windy Arbour
    "dun",  # Dundrum
    "bal",  # Balally
    "kil",  # Kilmacud
    "sti",  # Stillorgan
    "san",  # Sandyford
    "cpk",  # Central Park
    "gle",  # Glencairn
    "gal",  # The Gallops
    "leo",  # Leopardstown Valley
    "baw",  # Ballyogan Wood
    "rcc",  # Racecourse
    "cck",  # Carrickmines
    "bre",  # Brennanstown
    "lau",  # Laughanstown
    "che",  # Cherrywood
    "bri",  # Brides Glen
    # cSpell: enable  # noqa: ERA001
]


async def async_translate_station_name(hass: HomeAssistant, station_code: str) -> str:
    """Retrieve the full name of station_code."""
    # Possibly this can be worked around using translation_key and placeholders,
    # but I couldn't figure out a way to do it. Relevant documentation:
    # https://developers.home-assistant.io/docs/internationalization/core

    translations = await translation.async_get_translations(
        hass, hass.config.language, "selector", {DOMAIN}
    )
    return translations.get(
        f"component.luas.selector.station.options.{station_code}",
        station_code,
    )

"""luasforecasts fetches data from luasforecasts.rpa.ie.

More info: https://data.gov.ie/dataset/luas-forecasting-api
"""

import sys
import typing
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

URLBASE = "https://luasforecasts.rpa.ie/xml/get.ashx"


def _fetch_raw(stop_code: str) -> bytes:
    """Fetch a Luas forecast."""
    params = urllib.parse.urlencode(
        {
            "action": "forecast",
            "stop": stop_code,
            "ver": 2,
            "encrypt": "false",
        }
    )
    url = f"{URLBASE}?{params}"

    req = urllib.request.Request(url)
    with urllib.request.urlopen(req) as response:
        return response.read()


class Tram(typing.TypedDict):
    """Tram represents one Luas Tram in a LuasInfo response."""

    destination: str
    direction: str
    dueMins: int


class LuasInfo(typing.TypedDict):
    """LuasInfo represents a complete Luas forecast for a stop."""

    message: str
    stop: str
    trams: list[Tram]


def _sorted_trams(trams: list[Tram]) -> list[Tram]:
    return sorted(trams, key=lambda t: t["dueMins"])


def _convert_minutes(minutes: str) -> int:
    if minutes == "DUE":
        return 0
    return int(minutes)


def _parse(payload: bytes) -> LuasInfo:
    """Parse an XML Luas forecast from luasforecasts.rpa.ie."""
    tree = ET.fromstring(payload)
    message_node = tree.find("message")
    if message_node is None:
        raise ValueError
    result: LuasInfo = {
        "message": message_node.text or "",
        "stop": tree.attrib["stop"],
        "trams": _sorted_trams(
            [
                {
                    "destination": tram.attrib["destination"],
                    "dueMins": _convert_minutes(tram.attrib["dueMins"]),
                    "direction": direction.attrib["name"],
                }
                for direction in tree.findall("direction")
                for tram in direction.findall("tram")
                if tram.attrib["dueMins"]
            ]
        ),
    }

    return result


def fetch(stop_code: str) -> LuasInfo:
    """Fetch the latest luas forecast."""
    try:
        return _parse(_fetch_raw(stop_code))
    except ValueError as exc:
        raise ValueError(
            f"Failed to parse response. Possibly nonexistent stop {stop_code!r}."
        ) from exc


def main():
    """Runnable unit test."""
    print(fetch(sys.argv[1]))  # noqa: T201


if __name__ == "__main__":
    main()

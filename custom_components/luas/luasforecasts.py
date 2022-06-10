"""luasforecasts fetches data from luasforecasts.rpa.ie

More info: https://data.gov.ie/dataset/luas-forecasting-api"""

import sys
import typing
import urllib
import urllib.parse
import urllib.request
import xml.etree.ElementTree

URLBASE = "https://luasforecasts.rpa.ie/xml/get.ashx"


def _fetch_raw(stop_code: typing.AnyStr):
    """Fetch a LUAS forecast"""
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
    """Tram represents one LUAS Tram in a LuasInfo response"""

    destination: str
    direction: str
    dueMins: str


class LuasInfo(typing.TypedDict):
    """LuasInfo represents a complete LUAS forecast for a stop"""

    message: str
    stop: str
    trams: list[Tram]


def _sorted_trams(trams: list[Tram]):
    return sorted(
        trams, key=lambda t: 0 if t["dueMins"] == "DUE" else int(t["dueMins"])
    )


def _parse(payload: typing.AnyStr) -> LuasInfo:
    """Parse an XML LUAS forecast from luasforecasts.rpa.ie"""
    tree = xml.etree.ElementTree.fromstring(payload)
    message_node = tree.find("message")
    assert message_node is not None
    result: LuasInfo = {
        "message": message_node.text or "",
        "stop": tree.attrib["stop"],
        "trams": _sorted_trams(
            [
                {
                    "destination": tram.attrib["destination"],
                    "dueMins": tram.attrib["dueMins"],
                    "direction": direction.attrib["name"],
                }
                for direction in tree.findall("direction")
                for tram in direction.findall("tram")
                if tram.attrib["dueMins"]
            ]
        ),
    }

    return result


def fetch(stop_code: typing.AnyStr) -> LuasInfo:
    """Fetches the latest luas forecast"""
    return _parse(_fetch_raw(stop_code))


def main():
    """Runnable test"""
    print(fetch(sys.argv[1]))


if __name__ == "__main__":
    main()

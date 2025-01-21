"""Tests for luas forecast module."""

import textwrap
import unittest

from custom_components.luas.api import parse


class TestLuasForecastParsing(unittest.TestCase):
    """Tests for luas forecast parsing."""

    def test_parse(self) -> None:
        """Test parsing of trams XML."""
        payload = textwrap.dedent(
            """
            <stopInfo created="2022-06-10T14:37:15" stop="Leopardstown Valley" stopAbv="LEO">
                <message>Green Line services operating normally</message>
                <direction name="Inbound" statusMessage="Services operating normally" forecastsEnabled="True" operatingNormally="True">
                    <tram dueMins="6" destination="Parnell" />
                    <tram dueMins="18" destination="Parnell" />
                </direction>
                <direction name="Outbound" statusMessage="Services operating normally" forecastsEnabled="True" operatingNormally="True">
                    <tram dueMins="4" destination="Bride's Glen" />
                    <tram dueMins="DUE" destination="Bride's Glen" />
                </direction>
            </stopInfo>
            """  # noqa: E501
        )

        got = parse(payload.encode("utf-8"))

        want = {
            "message": "Green Line services operating normally",
            "stop": "Leopardstown Valley",
            "trams": [
                {
                    "destination": "Bride's Glen",
                    "direction": "Outbound",
                    "dueMins": 0,
                },
                {
                    "destination": "Bride's Glen",
                    "direction": "Outbound",
                    "dueMins": 4,
                },
                {"destination": "Parnell", "direction": "Inbound", "dueMins": 6},
                {"destination": "Parnell", "direction": "Inbound", "dueMins": 18},
            ],
        }

        assert got == want

    def test_parse_empty(self) -> None:
        """Test parsing of after-hours empty result."""
        payload = textwrap.dedent(
            """
            <stopInfo created="2022-06-12T04:09:17" stop="Leopardstown Valley" stopAbv="LEO">
                <message>Green Line services operating normally</message>
                <direction name="Inbound" statusMessage="Services operating normally" forecastsEnabled="True" operatingNormally="True">
                    <tram destination="No trams forecast" dueMins="" />
                </direction>
                <direction name="Outbound" statusMessage="Services operating normally" forecastsEnabled="True" operatingNormally="True">
                    <tram destination="No trams forecast" dueMins="" />
                </direction>
            </stopInfo>
            """  # noqa: E501
        )

        got = parse(payload.encode("utf-8"))

        want = {
            "message": "Green Line services operating normally",
            "stop": "Leopardstown Valley",
            "trams": [],
        }

        assert got == want


if __name__ == "__main__":
    unittest.main()

# cSpell: word Leopardstown

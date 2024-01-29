"""Tests for luasforecasts module."""

import unittest

from custom_components.luas import luasforecasts


class TestLuasForecasts(unittest.TestCase):
    """Tests for luasforecasts module."""

    def test_sort(self):
        """Test sorting of tram lists."""

        tram_a = luasforecasts.Tram(destination="A", direction="", dueMins=7)
        tram_b = luasforecasts.Tram(destination="B", direction="", dueMins=0)
        tram_c = luasforecasts.Tram(destination="C", direction="", dueMins=3)

        data = [tram_a, tram_b, tram_c]
        want = [tram_b, tram_c, tram_a]

        got = luasforecasts._sorted_trams(data)  # pylint: disable=protected-access

        self.assertEqual(got, want)

    def test_parse(self):
        """Test parsing of trams XML."""

        payload = (
            b"""<stopInfo created="2022-06-10T14:37:15" stop="Leopardstown Valley" stopAbv="LEO">"""
            b"""<message>Green Line services operating normally</message>"""
            b"""<direction name="Inbound" statusMessage="Services operating normally" """
            b"""forecastsEnabled="True" operatingNormally="True">"""
            b"""<tram dueMins="6" destination="Parnell" />"""
            b"""<tram dueMins="18" destination="Parnell" /></direction>"""
            b"""<direction name="Outbound" statusMessage="Services operating normally" """
            b"""forecastsEnabled="True" operatingNormally="True"><tram dueMins="4" """
            b"""destination="Bride's Glen" /><tram dueMins="DUE" destination="Bride's Glen" />"""
            b"""</direction></stopInfo>"""
        )

        got = luasforecasts._parse(payload)  # pylint: disable=protected-access

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

        self.assertEqual(got, want)

    def test_parse_empty(self):
        """Test parsing of after-hours empty result."""

        payload = (
            b"""<stopInfo created="2022-06-12T04:09:17" stop="Leopardstown Valley" """
            b"""stopAbv="LEO">"""
            b"""<message>Green Line services operating normally</message>"""
            b"""<direction name="Inbound" statusMessage="Services operating normally" """
            b"""forecastsEnabled="True" operatingNormally="True"><tram """
            b"""destination="No trams forecast" dueMins="" /></direction>"""
            b"""<direction name="Outbound" statusMessage="Services operating normally" """
            b"""forecastsEnabled="True" operatingNormally="True">"""
            b"""<tram destination="No trams forecast" dueMins="" /></direction>"""
            b"""</stopInfo>"""
        )

        got = luasforecasts._parse(payload)  # pylint: disable=protected-access

        want = {
            "message": "Green Line services operating normally",
            "stop": "Leopardstown Valley",
            "trams": [],
        }

        self.assertEqual(got, want)


if __name__ == "__main__":
    unittest.main()

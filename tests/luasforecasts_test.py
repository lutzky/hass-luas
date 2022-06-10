"""Tests for luasforecasts module"""
import unittest

from custom_components.luas import luasforecasts


class TestLuasForecasts(unittest.TestCase):
    """Tests for luasforecasts module"""

    def test_sort(self):
        """Test sorting of tram lists"""

        tram_a = luasforecasts.Tram(destination="A", direction="", dueMins="7")
        tram_b = luasforecasts.Tram(destination="B", direction="", dueMins="DUE")
        tram_c = luasforecasts.Tram(destination="C", direction="", dueMins="3")

        data = [tram_a, tram_b, tram_c]
        want = [tram_b, tram_c, tram_a]

        got = luasforecasts._sorted_trams(data)  # pylint: disable=protected-access

        self.assertEqual(got, want)

    def test_parse(self):
        """Test parsing of trams XML"""

        payload = (
            """<stopInfo created="2022-06-10T14:37:15" stop="Leopardstown Valley" stopAbv="LEO">"""
            """<message>Green Line services operating normally</message>"""
            """<direction name="Inbound" statusMessage="Services operating normally" """
            """forecastsEnabled="True" operatingNormally="True">"""
            """<tram dueMins="6" destination="Parnell" />"""
            """<tram dueMins="18" destination="Parnell" /></direction>"""
            """<direction name="Outbound" statusMessage="Services operating normally" """
            """forecastsEnabled="True" operatingNormally="True"><tram dueMins="4" """
            """destination="Bride's Glen" /><tram dueMins="DUE" destination="Bride's Glen" />"""
            """</direction></stopInfo>"""
        )

        got = luasforecasts._parse(payload)  # pylint: disable=protected-access

        want = {
            "message": "Green Line services operating normally",
            "stop": "Leopardstown Valley",
            "trams": [
                {
                    "destination": "Bride's Glen",
                    "direction": "Outbound",
                    "dueMins": "DUE",
                },
                {
                    "destination": "Bride's Glen",
                    "direction": "Outbound",
                    "dueMins": "4",
                },
                {"destination": "Parnell", "direction": "Inbound", "dueMins": "6"},
                {"destination": "Parnell", "direction": "Inbound", "dueMins": "18"},
            ],
        }

        self.assertEqual(got, want)


if __name__ == "__main__":
    unittest.main()

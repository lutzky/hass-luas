"""
Luas API Client.

This is a client of the Luas Forecasting API, as described in
https://data.gov.ie/dataset/luas-forecasting-api. It can be viewed directly at
https://luasforecasts.rpa.ie/analysis/view.aspx,
"""

from __future__ import annotations

import socket
import typing
from typing import Any

import aiohttp
import async_timeout
import defusedxml.ElementTree as ET  # noqa: N817

from .const import LOGGER

BASE_URL = "https://luasforecasts.rpa.ie/xml/get.ashx"


class LuasApiClientError(Exception):
    """Exception to indicate a general API error."""


class LuasApiClientCommunicationError(
    LuasApiClientError,
):
    """Exception to indicate a communication error."""


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


def _verify_response_or_raise(response: aiohttp.ClientResponse) -> None:
    """Verify that the response is valid."""
    response.raise_for_status()


def parse(payload: bytes) -> LuasInfo:
    """Parse an XML Luas forecast."""
    tree = ET.fromstring(payload)
    message_node = tree.find("message")
    if message_node is None:
        raise ValueError

    trams: list[Tram] = [
        {
            "destination": tram.attrib["destination"],
            "dueMins": (
                int(tram.attrib["dueMins"]) if tram.attrib["dueMins"] != "DUE" else 0
            ),
            "direction": direction.attrib["name"],
        }
        for direction in tree.findall("direction")
        for tram in direction.findall("tram")
        if tram.attrib["dueMins"]
    ]

    messages = []

    if message_node.text:
        messages.append(message_node.text)

    direction_messages = sorted(
        {
            direction.attrib["statusMessage"]
            for direction in tree.findall("direction")
            if direction.attrib["operatingNormally"].lower() != "true"
        }
    )

    messages.extend(direction_messages)

    result: LuasInfo = {
        "message": "; ".join(messages),
        "stop": tree.attrib["stop"],
        "trams": sorted(trams, key=lambda t: t["dueMins"]),
    }

    return result


class LuasApiClient:
    """Luas API Client."""

    def __init__(
        self,
        station: str,
        session: aiohttp.ClientSession,
    ) -> None:
        """Luas API Client."""
        self._station = station
        self._session = session

    async def async_get_data(self) -> LuasInfo:
        """Get data from the API."""
        luas_result = await self._api_wrapper(
            stop=self._station,
        )
        LOGGER.debug("Raw result from luas API: %r", luas_result)
        parsed_result = parse(luas_result)
        LOGGER.debug("Parsed result from luas: %r", parsed_result)
        return parsed_result

    async def _api_wrapper(
        self,
        stop: str,
    ) -> Any:
        """Get information from the API."""
        try:
            async with async_timeout.timeout(10):
                response = await self._session.request(
                    method="get",
                    url=BASE_URL,
                    params={
                        "action": "forecast",
                        "ver": "2",
                        "encrypt": "false",
                        "stop": stop.upper(),
                    },
                )
                _verify_response_or_raise(response)
                return await response.text()

        except TimeoutError as exception:
            msg = f"Timeout error fetching information - {exception}"
            raise LuasApiClientCommunicationError(
                msg,
            ) from exception
        except (aiohttp.ClientError, socket.gaierror) as exception:
            msg = f"Error fetching information - {exception}"
            raise LuasApiClientCommunicationError(
                msg,
            ) from exception
        except Exception as exception:  # pylint: disable=broad-except
            msg = f"Something really wrong happened! - {exception}"
            raise LuasApiClientError(
                msg,
            ) from exception

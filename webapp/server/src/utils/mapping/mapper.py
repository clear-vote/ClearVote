"""This module is used to map addresses and coordinates to their precinct data."""
import os
import json
from urllib.parse import quote
from shapely.geometry import Point

import pandas as pd
import requests
from .geodata.data_loader import PrecinctLoader
from .geodata.precinct import Precinct

class Mapper:
    """This class contains methods to map addresses and coordinates to their precinct data."""

    # a pandas dataframe where each entry corresponds to a single precinct
    _precinct_table = PrecinctLoader.load_data()

    _full_precinct_table, _district_tables = PrecinctLoader.load_precincts_and_districts()

    def _get_coord(self, address: str) -> Point:  # get coordinate given address
        """Gets the latitude/longitude coordinates for the given address.

        Args:
            address: address to find coordinates for.

        Returns:
            latitude/longitude coordinates for the given address as a Point.

        Raises:
            RuntimeError: if issue connecting to or getting valid response from MapBox
        """

        mapbox_token = os.environ.get("MAPBOX_ACCESS_TOKEN")
        # if local mapbox access token, use that; else use public access token
        if mapbox_token is None:
            mapbox_token = "pk.eyJ1IjoiYW5heWFwIiwiYSI6ImNrcTFndGM0NTAzcWIycHBpZHhoenUxeWIifQ.2IvOWRA9LYQlxBk9j7_WaQ"

        url = (
            f"https://api.mapbox.com/geocoding/v5/mapbox.places/{ quote(address) }.json"
            + f"?access_token={ mapbox_token }"
        )
        try:
            response = requests.get(url, timeout=10)
            response_json = json.loads(response.content)
            coord = response_json["features"][0]["center"]

            if not response.ok:
                raise RuntimeError(
                    f"Invalid response from MapBox. Error Code: { response.status_code }"
                )

            return Point(coord[0], coord[1])
        except requests.exceptions.ConnectionError as exc:
            raise RuntimeError("Could not connect.") from exc
        except requests.exceptions.Timeout as exc:
            raise RuntimeError("Request timed out.") from exc
        except requests.exceptions.RequestException as exc:
            raise RuntimeError(f"An error occurred: {exc}") from exc

    def _get_precinct(
        self, coord: Point,
        full_table: bool = False
    ) -> Precinct or pd.Series:  # get precinct for given coordinates
        """Returns a Precinct object containing data about the precinct at the given coordinates.

        Args:
            coord: a latitude/longitude positional coordinate
        Returns:
            A Precinct object containing data about the precinct at the given coordinates.
        Raises:
            ValueError: if the given coordinates do not map to known precinct.
        """
        if full_table:
            geo_rows = Mapper._full_precinct_table.loc[
                Mapper._full_precinct_table.contains(coord)
            ]
        else:
            geo_rows = Mapper._precinct_table.loc[
                Mapper._precinct_table.contains(coord)
            ]

        if len(geo_rows) == 0:
            raise ValueError(
                f"Given coordinates ({ str(coord) }) do not map to a known precinct."
            )

        geo_row = geo_rows.iloc[0]
        if full_table:
            return geo_row
        precinct = Precinct(
            code=geo_row["precinct_code"],
            name=geo_row["precinct_name"],
            county_council=geo_row["county_council_code"],
            leg_dist=geo_row["leg_dist_code"],
            cong_dist=geo_row["cong_dist_code"],
            city_council_dist=geo_row["city_council_dist_code"],
            poly=geo_row["geometry"],
        )
        return precinct

    def get_precinct(self, address: str) -> Precinct or pd.Series:  # get precinct for given address
        """Returns a Precinct object containing data about the precinct at the given address.
        Args:
            address: address to look up precinct for.

        Returns:
            Precinct object containing data about the precinct at the given address.

        Raises:
            ValueError: if the given address does not map to known precinct.
        """
        coord = self._get_coord(address)
        try:
            precinct = self._get_precinct(coord, full_table=True)
        except ValueError as exc:
            raise ValueError(f"Given address ({ address }) does not map to a valid precinct") from exc
        return precinct

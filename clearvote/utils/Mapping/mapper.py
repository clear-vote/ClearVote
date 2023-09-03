"""This module is used to map addresses and coordinates to their precinct data."""
import json
from urllib.parse import quote
from shapely.geometry import Point
# import geopandas
# import pandas as pd
import requests
from clearvote.utils.data.data_loader import PrecinctLoader
from clearvote.utils.data.precinct import Precinct

# 2d binary search of points - at each stage, look at points, divide vertically, go until smallest bounding box can be reached
# reduction algo: state --> county --> precinct
# look into python interfaces
# separate data loader into another file
# instead of csv every time, it should be pickled and stored/read into memory as bin.


class Mapper:
    """This class contains methods to map addresses and coordinates to their precinct data."""
    # a pandas dataframe where each entry corresponds to a single precinct
    _precinct_table = PrecinctLoader.load_data()

    def _get_coord(self, address: str) -> Point:  # get coordinate given address
        """Gets the latitude/longitude coordinates for the given address.

        Args:
            address: address to find coordinates for.
        
        Returns:
            latitude/longitude coordinates for the given address as a Point.
        """
        url = f"https://api.mapbox.com/geocoding/v5/mapbox.places/{ quote(address) }.json?access_token=pk.eyJ1IjoiYW5heWFwIiwiYSI6ImNrcTFndGM0NTAzcWIycHBpZHhoenUxeWIifQ.2IvOWRA9LYQlxBk9j7_WaQ"
        try:
            response = requests.get(url, timeout=10)
        except requests.exceptions.Timeout:
            print("Request timed out")
        except requests.exceptions.RequestException as exc:
            print("An error occurred:", exc)

        if not response.ok:
            raise ValueError(f"Invalid response from MapBox. Error Code: { response.status_code }")

        response_json = json.loads(response.content)
        coord = response_json["features"][0]["center"]
        return Point(coord[0], coord[1])

    def _get_precinct(
        self, coord: Point
    ) -> Precinct:  # get precinct for given coordinates
        """Returns a Precinct object containing data about the precinct at the given coordinates.
        
        Args:
            coord: a latitude/longitude positional coordinate
        Returns:
            A Precinct object containing data about the precinct at the given coordinates.
        Raises:
            ValueError: if the given coordinates do not map to known precinct.
        """
        geo_rows = Mapper._precinct_table.loc[
            Mapper._precinct_table["shape"].contains(coord)
        ]

        if len(geo_rows) == 0:
            raise ValueError(f"Given coordinates ({ str(coord) }) do not map to a known precinct.")

        geo_row = geo_rows.iloc[0]
        precinct = Precinct(
            code=geo_row["precinct_code"],
            name=geo_row["precinct_name"],
            county_council=geo_row["county_council_code"],
            leg_dist=geo_row["leg_dist_code"],
            cong_dist=geo_row["cong_dist_code"],
            city_council_dist=geo_row["city_council_dist_code"],
            poly=geo_row["shape"],
        )
        return precinct

    def get_precinct(self, address: str) -> Precinct:  # get precinct for given address
        """Returns a Precinct object containing data about the precinct at the given address.
        Args:
            address: address to look up precinct for.
        
        Returns:
            Precinct object containing data about the precinct at the given address.

        Raises:
            ValueError: if the given address does not map to known precinct.
        """
        coord = self._get_coord(address)
        return self._get_precinct(coord)

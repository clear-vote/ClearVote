"""This module contains methods to gather all King County District data."""
import json
from typing import Dict
import requests
import pandas as pd
import geopandas as gpd


class KingCountyDistrictsParser:
    """This class contains methods to gather all King County District data."""

    @staticmethod
    def _get_tables_info() -> pd.DataFrame:
        """Gets information on what tables are available from KingCo GIS service.

        Returns:
            A pandas DataFrame containing the following columns:
            - id (index): id of the layer/district type
            - name: name of the layer/district type
        """
        data_url = "https://gismaps.kingcounty.gov/arcgis/rest/services/Districts/KingCo_Electoral_Districts/MapServer?f=pjson"
        table_info = KingCountyDistrictsParser._as_table(
            data_url, data_key="layers", index="id"
        )
        return table_info

    @staticmethod
    def _get_geo_table(id: int) -> gpd.GeoDataFrame:
        """Gets geographical data for the district type with the given id.

        Args:
            id: an integer ID of one of the King County district types.
        Returns:
            A geopandas GeoDataGrame containing a 'geometry' column and other data.
        Raises:
            ValueError: if id is not in the range (0, 15).
        """
        if id < 0 or id > 15:
            raise ValueError(f"given id { id } is not in the range(0, 15)")
        data_url = f"https://gismaps.kingcounty.gov/arcgis/rest/services/Districts/KingCo_Electoral_Districts/MapServer/{ id }/query?where=1%3D1&text=&objectIds=&time=&timeRelation=esriTimeRelationOverlaps&geometry=&geometryType=esriGeometryEnvelope&inSR=&spatialRel=esriSpatialRelIntersects&distance=&units=esriSRUnit_Foot&relationParam=&outFields=&returnGeometry=true&returnTrueCurves=false&maxAllowableOffset=&geometryPrecision=&outSR=&havingClause=&returnIdsOnly=false&returnCountOnly=false&orderByFields=&groupByFieldsForStatistics=&outStatistics=&returnZ=false&returnM=false&gdbVersion=&historicMoment=&returnDistinctValues=false&resultOffset=&resultRecordCount=&returnExtentOnly=false&sqlFormat=none&datumTransformation=&parameterValues=&rangeValues=&quantizationParameters=&featureEncoding=esriDefault&f=geojson"
        table = KingCountyDistrictsParser._as_table(data_url, geo_data=True)
        return table

    @staticmethod
    def _as_table(
        data_url: str,
        data_key: str or None = None,
        geo_data: bool = False,
        index: str or None = None,
    ) -> pd.DataFrame or gpd.GeoDataFrame:
        """Queries the given url and returns the table resulting from its response.

        Args:
            data_url: the url to GET from (must be an endpoint returning json/GeoJSON data).
            data_key: if specified and the data to be parsed is in a key/value pair of the resulting JSON,
                the key to look up.
            geo_data: True if the data is GeoJSON and should be treated as such, false otherwise.
            index: if specified, the name of the feature to use as an index.
        Returns:
            A pandas DataFrame containing the data from the given url.
        Raises:
            RuntimeError: if connection failed or invalid response from the given url.
        """
        try:
            data_response = requests.get(data_url, timeout=10)
            if not data_response.ok:
                raise RuntimeError("Invalid response from server.")
            json_data = data_response.content
            data = json.loads(json_data)
            table = pd.DataFrame()
            if geo_data:
                table = gpd.GeoDataFrame.from_features(data)
            else:
                if data_key:
                    table = pd.DataFrame.from_dict(data[data_key])
                else:
                    table = pd.DataFrame.from_dict(data)
            if index:
                table.set_index(index, inplace=True)
            return table
        except requests.exceptions.ConnectionError as exc:
            raise RuntimeError("Could not connect.") from exc
        except requests.exceptions.Timeout as exc:
            raise RuntimeError("Request timed out.") from exc
        except requests.exceptions.RequestException as exc:
            raise RuntimeError(f"An error occurred: {exc}") from exc

    @staticmethod
    def get_tables(rename_map: Dict[str, str] = {}) -> Dict[str, gpd.GeoDataFrame]:
        """Gets the tables of geographic district data in the form of a dictionary keyed by the name of the district type.

        Returns:
            A dictionary mapping distict types by name to geopandas GeoDataFrame with all geo data for that type.
        Raises:
            RuntimeError: if connection failed or invalid response from the KingCo GIS service.
        """
        table_info = KingCountyDistrictsParser._get_tables_info()
        tables = {}
        for layer_id, row in table_info.iterrows():
            layer_name = row["name"]
            layer_table = KingCountyDistrictsParser._get_geo_table(layer_id)
            layer_table.rename(columns=rename_map, inplace=True)
            tables[layer_name] = layer_table

        return tables

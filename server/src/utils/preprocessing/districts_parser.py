"""This module contains methods to gather all King County District data."""
import json
from typing import Dict, Set
import requests
import pandas as pd
import geopandas as gpd
from requests.models import PreparedRequest
from shapely import Polygon, MultiPolygon


class KingCountyDistrictsParser:
    """This class contains methods to gather all King County District data."""

    # max number of records that can be obtained in a single query from KingCo ArcGIS server
    MAX_RECORD_COUNT = 1000

    @staticmethod
    def _get_tables_info() -> pd.DataFrame:
        """Gets information on what tables are available from KingCo GIS service.

        Returns:
            A pandas DataFrame containing the following columns:
            - id (index): id of the layer/district type
            - name: name of the layer/district type
        """
        data_req = PreparedRequest()
        data_req.prepare_url(
            "https://gismaps.kingcounty.gov/arcgis/rest/services/Districts/KingCo_Electoral_Districts/MapServer",
            {"f": "pjson"}
        )
        json_table_info = KingCountyDistrictsParser._as_json(data_req.url)
        data = json.loads(json_table_info)
        table_info = pd.DataFrame.from_dict(data["layers"])
        table_info.set_index("id", inplace=True)
        return table_info

    @staticmethod
    def _get_geo_table(data_req: PreparedRequest) -> gpd.GeoDataFrame:
        """Gets geographical data from the given url.

        Args:
            data_req: request used to query for geo data. Must return data in GeoJSON form via
                HTTP GET request.
        Returns:
            A geopandas GeoDataGrame containing a 'geometry' column and other data.
        """
        result_offset = 0
        table_parts = []

        while True:
            data_req.prepare_url(data_req.url, params={"resultOffset" : result_offset})
            json_data = KingCountyDistrictsParser._as_json(data_req.url)
            if len(json_data) == 0:
                break
            data = json.loads(json_data)
            part = gpd.GeoDataFrame.from_features(data)
            table_parts.append(part)
            result_offset += KingCountyDistrictsParser.MAX_RECORD_COUNT

        table = pd.concat(table_parts)
        return table

    @staticmethod
    def _as_json(
        data_url: str
    ) -> bytes:
        """Queries the given url and returns the json data resulting from its response.

        Args:
            data_url: the url to GET from (must be an endpoint returning json/GeoJSON data).
        Returns:
            JSON data from the given url in bytes form.
        Raises:
            RuntimeError: if connection failed or invalid response from the given url.
        """
        try:
            data_response = requests.get(data_url, timeout=10)
            if not data_response.ok:
                raise RuntimeError("Invalid response from server.")
            json_data = data_response.content
            return json_data
        except requests.exceptions.ConnectionError as exc:
            raise RuntimeError("Could not connect.") from exc
        except requests.exceptions.Timeout as exc:
            raise RuntimeError("Request timed out.") from exc
        except requests.exceptions.RequestException as exc:
            raise RuntimeError(f"An error occurred: {exc}") from exc

    @staticmethod
    def get_tables(
        rename_map: Dict[str, str] = {
            "NAME": "name",
            "LEGDST": "name",
            "CONGDST": "name",
            "kccdst": "name",
            "geometry": "shape",
        }
    ) -> Dict[str, gpd.GeoDataFrame]:
        """Gets the tables of geographic district data in the form of a dictionary keyed by the
            name of the district type.

        Args:
            rename_map: a map of old column names to new column names
        Returns:
            A dictionary mapping distict types by name to geopandas GeoDataFrame with all
                geo data for that type.
        Raises:
            RuntimeError: if connection failed or invalid response from the KingCo GIS service.
        """
        table_info = KingCountyDistrictsParser._get_tables_info()
        tables = {}
        for layer_id, row in table_info.iterrows():
            layer_name = row["name"]
            # data_url = f"https://gismaps.kingcounty.gov/arcgis/rest/services/Districts/KingCo_Electoral_Districts/MapServer/{ layer_id }/query?where=1%3D1&text=&objectIds=&time=&timeRelation=esriTimeRelationOverlaps&geometry=&geometryType=esriGeometryEnvelope&inSR=&spatialRel=esriSpatialRelIntersects&distance=&units=esriSRUnit_Foot&relationParam=&outFields=&returnGeometry=true&returnTrueCurves=false&maxAllowableOffset=&geometryPrecision=&outSR=&havingClause=&returnIdsOnly=false&returnCountOnly=false&orderByFields=&groupByFieldsForStatistics=&outStatistics=&returnZ=false&returnM=false&gdbVersion=&historicMoment=&returnDistinctValues=false&resultOffset=&resultRecordCount=&returnExtentOnly=false&sqlFormat=none&datumTransformation=&parameterValues=&rangeValues=&quantizationParameters=&featureEncoding=esriDefault&f=geojson"
            data_url = f"https://gismaps.kingcounty.gov/arcgis/rest/services/Districts/KingCo_Electoral_Districts/MapServer/{ layer_id }/query?where=1%3D1&timeRelation=esriTimeRelationOverlaps&geometryType=esriGeometryEnvelope&spatialRel=esriSpatialRelIntersects&units=esriSRUnit_Foot&returnGeometry=true&returnTrueCurves=false&returnIdsOnly=false&returnCountOnly=false&returnZ=false&returnM=false&returnDistinctValues=false&returnExtentOnly=false&sqlFormat=none&featureEncoding=esriDefault&f=geojson"
            layer_table = KingCountyDistrictsParser._get_geo_table(data_url)
            layer_table.rename(columns=rename_map, inplace=True)
            tables[layer_name] = layer_table

        return tables

    @staticmethod
    def get_full_precincts(
        rename_map: Dict[str, str] = {
            "votdst": "precinct_code",
            "NAME": "precinct_name",
            "geometry": "shape",
            "SUM_VOTERS": "num_voters",
            "Shape_Length": "shape_length",
            "Shape_Area": "shape_area",
        }
    ) -> gpd.GeoDataFrame:
        """Gets full precinct table with all metadata.

        Args:
            rename_map: a map of old column names to new column names.
        Returns:
            A geopandas GeoDataFrame containing full KingCo precinct data.
        """
        base_url = "https://gisdata.kingcounty.gov/arcgis/rest/services/OpenDataPortal/district__votdst_area/MapServer/418/query?outFields=*&where=1%3D1&f=geojson"
        result_offset = 0
        precinct_table_parts = []

        while True:
            new_data = KingCountyDistrictsParser._get_geo_table(
                f"{ base_url }&resultOffset={ result_offset }"
            )
            if len(new_data) == 0:
                break
            precinct_table_parts.append(new_data)
            result_offset += KingCountyDistrictsParser.MAX_RECORD_COUNT

        precinct_table = pd.concat(precinct_table_parts)
        precinct_table.rename(columns=rename_map, inplace=True)
        precinct_table.set_index("precinct_code", inplace=True, drop=False)
        return precinct_table
    
    @staticmethod
    def _validate_boundary_results(
        results: gpd.GeoDataFrame
    ):
        if len(results) == 0:
            return gpd.GeoSeries({col: None for col in results.columns})
        elif len(results) > 1:
            raise RuntimeError("Multiple boundaries contain the center.")
        return results.iloc[0]

    @staticmethod
    def get_boundary(
        shape: Polygon or MultiPolygon,
        boundaries: gpd.GeoDataFrame
    ) -> gpd.GeoSeries:
        """Gets the row from the list of boundaries that contains the center of the given shape.
        
        Args:
            shape: shape to check for containment within the boundaries.
            boundaries: a geopandas dataframe with at least a 'name' and 'geometry' column.
        Returns:
            A GeoSeries of the row with geometry that contains the center of shape.
        Raises:
            ValueError: if shape is not an instance of shapely Polygon or Multipolygon.
            RuntimeError: if multiple boundaries contain the center of shape.
        """
        if isinstance(shape, Polygon):
            center = shape.centroid
            containing = boundaries.loc[boundaries.contains(center)]
            return KingCountyDistrictsParser._validate_boundary_results(containing)
        elif isinstance(shape, MultiPolygon):
            prev = None
            for poly in shape.geoms:
                center = poly.centroid
                containing = boundaries.loc[boundaries.contains(center)]
                validated = KingCountyDistrictsParser._validate_boundary_results(containing)
                # if prev and not validated.name == prev.name: TODO fix this so it checks for same boundary
                #     raise RuntimeError(f"given shape falls in both { prev.name } and { validated.name }")
                prev = validated
            return prev
        else:
            raise ValueError(f"shape type { type(shape) } is not valid.")

    @staticmethod
    def get_boundaries_by_center(
        precinct_table: gpd.GeoDataFrame,
        district_table: gpd.GeoDataFrame
    ) -> gpd.GeoDataFrame:
        """Returns a DataFrame of precincts codes and the information about the district that
            contains it.
        
        Args:
            precinct_table: a geopandas GeoDataFrame containing at least the columns 'precinct_code'
                and 'geometry'. 'geometry' must contain shapely Polygons or MultiPolygons.
                'precinct_code' should be the index column of this dataframe.
            district_table: a geopandas GeoDataFrame containing district boundary data. must be
                indexed by a 'name' column and contain a 'geometry' column. 'geometry' must contain
                shapely Polygons or MultiPolygons.
        Returns:
            A geopandas GeoDataFrame with the following columns:
                - precinct_code: a unique code correponding to a precinct in King County
                - name: name of the district that contains the center of this precinct
        Raises:
            ValueError: if the shape of any precinct is not an instance of shapely Polygon
                or Multipolygon.
            RuntimeError: if multiple boundaries contain the center of a precinct.
        """
        return precinct_table.apply(
            lambda row: KingCountyDistrictsParser.get_boundary(row["geometry"], district_table),
            axis=1
        )

    @staticmethod
    def fill_all_containing_districts(
        precinct_table: gpd.GeoDataFrame,
        district_tables: Dict[str, gpd.GeoDataFrame],
        ignore: Set[str] = set(),
    ) -> gpd.GeoDataFrame:
        """Returns a GeoDataFrame that is a left spatial join of the precinct table and each
            district table.
            
        Args:
            precinct_table: table of precinct information. must be indexed by a 'precinct_code'
                column and contain the column 'geometry'.
            district_table: a dictionary mapping district type names to tables containing
                information about them. each table must be indexed by a 'name' column and contain a
                'geometry' column.
            ignore: a set of table names to ignore for joining. must be names that are keys in
                district_tables.
        Returns:
            A GeoDataFrame that is a left spatial join of the precinct table and each
                district table. In the returned dataframe, the 'name' and 'geometry' column names
                of each district that is joined will be prefixed with the district type name in
                snake case. E.g., 'School districts' would be turned into the prefix 'school_districts_'
        Raisese:
            ValueError: if the shape of any precinct is not an instance of shapely Polygon or Multipolygon.
            RuntimeError: if multiple boundaries for a district type contain the center of a precinct."""
        result = precinct_table
        for name, district_table in district_tables.items():
            if name not in ignore:
                formatted_name = name.lower().replace(" ", "_")
                precinct_districts = KingCountyDistrictsParser.get_boundaries_by_center(precinct_table, district_table)
                print(type(precinct_districts))
                precinct_districts = precinct_districts.add_prefix(f"{ formatted_name }_")

                result = pd.merge(result, precinct_districts, how="left", left_index=True, right_index=True, validate="1:1")
        return result

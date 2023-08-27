from shapely.geometry import Polygon, Point
import geopandas
import pandas as pd
import requests
from clearvote.utils.Mapping.precinct import Precinct
import json
from urllib.parse import quote

class Mapper: 
    @staticmethod
    def _generate_precinct_table(polygon_path, id_col1, data_path, id_col2, drop=[]):
        precinct_polygons = geopandas.read_file(polygon_path)
        precinct_polygons[id_col1] = pd.to_numeric(precinct_polygons[id_col1])

        precinct_data = pd.read_csv(data_path)
        precinct_data[id_col2] = pd.to_numeric(precinct_data[id_col2])

        precinct_table = pd.merge(precinct_polygons, precinct_data, left_on=id_col1, right_on=id_col2)
        for col in drop:
            precinct_table.drop(col, axis=1, inplace=True)

        precinct_table.set_index(id_col1, inplace=True, drop=False)

        return precinct_table
    
    _precinct_table = _generate_precinct_table.__func__(
        "clearvote/static/Data/Precincts/Voting_Districts_of_King_County___votdst_area.geojson",
        "votdst",
        "clearvote/static/Data/Precincts/precinct-and-district-data.csv",
        "PrecinctCode",
        drop=["PrecinctName", "PrecinctCode"]
    )
    
    @staticmethod
    def _get_coord(address: str) -> Point: # get coordinate given address
        url = f"https://api.mapbox.com/geocoding/v5/mapbox.places/{ quote(address) }.json?access_token=pk.eyJ1IjoiYW5heWFwIiwiYSI6ImNrcTFndGM0NTAzcWIycHBpZHhoenUxeWIifQ.2IvOWRA9LYQlxBk9j7_WaQ"
        response = requests.get(url)
        
        if not response.ok:
            raise ValueError(f"Error Code: { response.status_code }")
        
        response_json = json.loads(response.content)
        coord = response_json["features"][0]["center"]
        return Point(coord[0], coord[1])


    @staticmethod
    def _get_precinct(coord: Point) -> Precinct: # get precinct for given coordinates
        geo_rows = Mapper._precinct_table.loc[Mapper._precinct_table["geometry"].contains(coord)]
        geo_row = geo_rows.iloc[0]
        precinct = Precinct(
            code=geo_row["votdst"],
            name=geo_row["NAME"],
            county_council=geo_row["CountyCouncil"],
            leg_dist=geo_row["LegislativeDistrict"],
            cong_dist=geo_row["CongressionalDistrict"],
            seattle_council_dist=geo_row["SeattleCouncilDistrict"],
            poly=geo_row["geometry"]
        )
        return precinct
    
    @staticmethod
    def get_precinct(address: str) -> Precinct: # get precinct for given address
        coord = Mapper._get_coord(address)
        return Mapper._get_precinct(coord)
        

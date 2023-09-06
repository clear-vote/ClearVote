"""This module is used to parse scattered precinct data."""
from pathlib import Path
import pandas as pd
import geopandas as gp


class Parser:
    """This class contains methods to parse scattered precinct data."""

    @staticmethod
    def parse_precinct_table() -> pd.DataFrame:
        """Parsers and returns precinct data table.

        Returns:
            A Pandas DataFrame of precinct data with the following standard named columns:
            - precinct_code: numeric code of the precinct; index of the returned dataframe
            - precinct_name: name of the precinct
            - shape: polygon boundary of the precinct
            - num_voters: number of voters in that precinct
            - shape_length: length of the precinct boundary
            - shape_area: area of the precinct boundary
            - county_council_code: numeric code of the precinct's county council
            - cong_dist_code: numeric code of the precinct's congressional district
            - leg_dist_code:  numeric code of the precinct's legislative district
            - city_council_dist_code: numeric code of the precinct's city council district
        """
        polygon_path = Path(
            "preprocessing/data/Precincts/Voting_Districts_of_King_County___votdst_area.geojson"
        )
        id_col1 = "votdst"
        data_path = Path("preprocessing/data/Precincts/precinct-and-district-data.csv")
        id_col2 = "PrecinctCode"
        drop = ["PrecinctName", "PrecinctCode"]
        mapped_names = {
            "votdst": "precinct_code",
            "NAME": "precinct_name",
            "geometry": "shape",
            "SUM_VOTERS": "num_voters",
            "Shape_Length": "shape_length",
            "Shape_Area": "shape_area",
            "CountyCouncil": "county_council_code",
            "LegislativeDistrict": "leg_dist_code",
            "CongressionalDistrict": "cong_dist_code",
            "SeattleCouncilDistrict": "city_council_dist_code",
        }

        precinct_polygons = gp.read_file(polygon_path)
        precinct_polygons[id_col1] = pd.to_numeric(precinct_polygons[id_col1])

        precinct_data = pd.read_csv(data_path)
        precinct_data[id_col2] = pd.to_numeric(precinct_data[id_col2])

        precinct_table = pd.merge(
            precinct_polygons, precinct_data, left_on=id_col1, right_on=id_col2
        )

        precinct_table.rename(columns=mapped_names, inplace=True)

        for col in drop:
            precinct_table.drop(col, axis=1, inplace=True)

        precinct_table.set_index("precinct_code", inplace=True, drop=False)

        return precinct_table

"""This module is used to load the precinct data table into memory."""
from pathlib import Path
import pandas as pd
from src.utils.data.precinct_parser import Parser

class PrecinctLoader:
    """This class contains methods to load the precinct data"""

    @staticmethod
    def load_data() -> pd.DataFrame:
        """Loads the precinct data table.
        
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
            - city: name of the city
            - city_council_dist_code: numeric code of the precinct's city council district
        """

        filepath = Path.joinpath(Path(__file__).parent, "cached_data/precinct_table.pkl") # filepath for binary data file
        if not filepath.exists():
            data_table = Parser.parse_precinct_table()
            data_table.to_pickle(filepath)
        else:
            data_table = pd.read_pickle(filepath)
        return data_table

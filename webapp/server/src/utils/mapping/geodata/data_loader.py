"""This module is used to load the precinct data table into memory."""
from pathlib import Path
import pandas as pd

class PrecinctLoader:
    """This class contains methods to load the precinct data"""

    @staticmethod
    def load_data() -> pd.DataFrame:
        """Loads the precinct data table.
        Must have pickled precinct table at 'cached_data/precinct_table.pkl'.
        
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
        data_table = pd.read_pickle(filepath)
        return data_table
    
    @staticmethod
    def load_precincts_and_districts():
        """"""
        precinct_filepath = Path.joinpath(Path(__file__).parent, "cached_data/precincts_and_districts.pkl") # filepath for binary data file
        precincts_and_districts = pd.read_pickle(precinct_filepath)

        districts_dir = Path.joinpath(Path(__file__).parent, "cached_data/districts/") # filepath for binary data file
        district_tables = {}
        for filepath in districts_dir.iterdir():
            district_tables[filepath.stem] = pd.read_pickle(filepath)
        
        return precincts_and_districts, district_tables

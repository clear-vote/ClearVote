import requests
import json
import geopandas as gpd

class GeoParser:
    @staticmethod
    def get_county_boundaries():
        return GeoParser._get_boundaries(
            "https://gis.dnr.wa.gov/site3/rest/services/Public_Boundaries/WADNR_PUBLIC_Cadastre_OpenData/FeatureServer/11/query?outFields=*&where=1%3D1&f=geojson"
        )
        
        
    @staticmethod
    def get_precinct_boundaries():
        return GeoParser._get_boundaries(
            "https://services.arcgis.com/jsIt88o09Q0r1j8h/arcgis/rest/services/Statewide_Precincts_2019General_SPS/FeatureServer/0/query?outFields=*&where=1%3D1&f=geojson"
        )

    @staticmethod
    def get_state_boundaries():
        pass

        
    @staticmethod
    def _get_boundaries(url, timeout=10):
        try:
            data_request = requests.get(
                url,
                timeout=timeout
                )
            if not data_request.ok:
                raise RuntimeError("Could not query Open Data Portal")
            raw_boundary_data = json.loads(data_request.content)
            processed_boundary_data = gpd.GeoDataFrame.from_features(raw_boundary_data["features"])
            return processed_boundary_data
        except requests.exceptions.ConnectionError as exc:
            raise RuntimeError("Could not connect.") from exc
        except requests.exceptions.Timeout as exc:
            raise RuntimeError("Request timed out.") from exc
        except requests.exceptions.RequestException as exc:
            raise RuntimeError(f"An error occurred: {exc}") from exc
        
        
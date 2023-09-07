import json
import requests
import pandas as pd
import geopandas as gpd

class KingCountyDistrictsParser:
    @staticmethod
    def _get_tables_info():
        data_url = "https://gismaps.kingcounty.gov/arcgis/rest/services/Districts/KingCo_Electoral_Districts/MapServer?f=pjson"
        table_info = KingCountyDistrictsParser._as_table(data_url, data_key="layers", index="id")
        return table_info
    
    @staticmethod
    def _get_geo_table(id):
        data_url = f"https://gismaps.kingcounty.gov/arcgis/rest/services/Districts/KingCo_Electoral_Districts/MapServer/{ id }/query?where=1%3D1&text=&objectIds=&time=&timeRelation=esriTimeRelationOverlaps&geometry=&geometryType=esriGeometryEnvelope&inSR=&spatialRel=esriSpatialRelIntersects&distance=&units=esriSRUnit_Foot&relationParam=&outFields=&returnGeometry=true&returnTrueCurves=false&maxAllowableOffset=&geometryPrecision=&outSR=&havingClause=&returnIdsOnly=false&returnCountOnly=false&orderByFields=&groupByFieldsForStatistics=&outStatistics=&returnZ=false&returnM=false&gdbVersion=&historicMoment=&returnDistinctValues=false&resultOffset=&resultRecordCount=&returnExtentOnly=false&sqlFormat=none&datumTransformation=&parameterValues=&rangeValues=&quantizationParameters=&featureEncoding=esriDefault&f=geojson"
        table = KingCountyDistrictsParser._as_table(data_url, geo_data=True)
        return table

    @staticmethod
    def _as_table(data_url, data_key=None, geo_data=False, index=None):
        data_response = requests.get(data_url)
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

    @staticmethod
    def get_tables():
        table_info = KingCountyDistrictsParser._get_tables_info()
        tables = {}
        for layer_id, row in table_info.iterrows():
            layer_name = row["name"]
            tables[layer_name] = KingCountyDistrictsParser._get_geo_table(layer_id)

        return tables

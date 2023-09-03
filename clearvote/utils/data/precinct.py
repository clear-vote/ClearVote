from shapely import Polygon

class Precinct(object):
    def __init__(
        self,
        code: int,
        name: str,
        county_council: int,
        leg_dist: int,
        cong_dist: int,
        city_council_dist: int,
        poly: Polygon,
    ):
        self.code = code
        self.name = name
        self.county_council = county_council
        self.leg_dist = leg_dist
        self.cong_dist = cong_dist
        self.city_council_dist = city_council_dist
        self.poly = poly

    def get_code(self) -> int:
        return self.code

    def get_name(self) -> str:
        return self.name

    def get_county_council(self) -> int:
        return self.county_council

    def get_leg_dist(self) -> int:
        return self.leg_dist

    def get_cong_dist(self) -> int:
        return self.cong_dist

    def get_city_council_dist(self) -> int:
        return self.city_council_dist

    def get_poly(self) -> Polygon:
        return self.poly

    def __str__(self):
        return f"""CODE: { self.get_code() },
            NAME: { self.get_name() },
            COUNTY COUNCIL: { self.get_county_council() },
            LEG. DIST: { self.get_leg_dist() },
            CONG. DIST: { self.get_cong_dist() },
            CITY COUNCIL DIST: { self.get_city_council_dist() }
            """

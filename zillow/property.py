import json
import re

from zillow.session import Session


class Property:
    BASE_URL = "https://www.zillow.com"

    def __init__(self, url):
        self.session = Session()
        partial_url = not url.startswith('http')  # used for rental properties with multiple units
        self.url = f"{self.BASE_URL}{url}" if partial_url else url
        if partial_url:
            urls = self.get_rental_units()

        # self.data = self._scrape_property_results()

    def get_rental_units(self):
        building = self._scrape_rental_results()
        address = building.get("address")
        floor_plans = building.get("floorPlans")
        unit_urls = []
        for plan in floor_plans:
            for unit in plan.get("units"):
                unit_num = '-'.join(re.findall(r'[0-9]+', unit.get('unitNumber')))
                unit_urls.append(f"{self.BASE_URL}/homedetails/{address.get('streetAddress').replace(' ', '-')}"
                                 f"-{unit_num}-{address.get('city')}-{address.get('state')}-{address.get('zipcode')}/"
                                 f"{unit.get('zpid')}_zpid/")
        return unit_urls

    def _scrape_rental_results(self):
        page = self.session.get(self.url).text
        search = re.search(r'(\{"props":.*?)</script>', page)
        if not search:
            return None
        data = json.loads(search.group(1))
        return data.get("props").get("initialData").get("building")

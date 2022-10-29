import json
import logging
import re
from typing import List
import pandas as pd
from zillow.formatter import Formatter
from zillow.session import Session


log = logging.getLogger(__name__)

RENTAL = {
    'homeStatus': 'status',
    'hdpUrl': 'url',
    'homeType': 'home_type',
    'price': 'listed',
    'streetAddress': 'street',
    'bedrooms': 'beds',
    'bathrooms': 'baths',
    'livingArea': 'area',
}

RENTAL_COLS = ['state', 'city', 'zipcode']


def format_apartment_data(data):
    fmt = Formatter(data)
    fmt.select_rename_columns(RENTAL, RENTAL_COLS)
    fmt.filter_apply_column_func('url', lambda x: ~x.str.startswith('http'),
                                 lambda url: f"https://www.zillow.com{url}")
    return fmt.df


class Apartments:
    BASE_URL = "https://www.zillow.com"

    def __init__(self, urls: List[str]):
        self.session = Session()
        self.partial_urls = urls

    def df(self):
        rental_urls = []
        for url in self.partial_urls:
            rental_urls.extend(self._get_rental_unit_urls(f"{self.BASE_URL}{url}"))
        print(rental_urls)
        dfs = []
        for url in rental_urls:
            dfs.append(format_apartment_data(Property(url).fetch()))
        return pd.concat(dfs)
        
    def _get_rental_unit_urls(self, url):
        building = self._scrape_rental_results(url)
        # print(json.dumps(building))
        address = building.get("address")
        floor_plans = building.get("floorPlans")
        fallback = building.get("bestMatchedUnit").get("hdpUrl")
        unit_urls = []
        for plan in floor_plans:
            if "units" not in plan or not plan.get("units"):
                log.debug(f"No units found: {plan}")
                unit_urls.append(f"{self.BASE_URL}{fallback.replace(building.get('zpid'), plan.get('zpid'))}")
                continue
            for unit in plan.get("units"):
                unit_num = '-'.join(re.findall(r'[0-9]+', unit.get('unitNumber')))
                unit_urls.append(f"{self.BASE_URL}/homedetails/{address.get('streetAddress').replace(' ', '-')}"
                                 f"-{unit_num}-{address.get('city')}-{address.get('state')}-{address.get('zipcode')}/"
                                 f"{unit.get('zpid')}_zpid/")
        return unit_urls

    def _scrape_rental_results(self, url):
        page = self.session.get(url).text
        search = re.search(r'(\{"props":.*?)</script>', page)
        if not search:
            return None
        data = json.loads(search.group(1))
        return data.get("props").get("initialData").get("building")


class Property:

    def __init__(self, url, session=None):
        self.session = session if session else Session()
        self.url = url

    def fetch(self):
        page = self.session.get(self.url).text
        search = re.search(r'(\{"apiCache".*?)</script>', page)
        if not search:
            return {}
        raw = json.loads(search.group(1))
        cache = json.loads(raw.get('apiCache'))
        if len(cache.keys()) >= 2:
            return cache.get(list(cache.keys())[1]).get('property')


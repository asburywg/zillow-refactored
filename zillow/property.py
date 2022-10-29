import json
import logging
import re
from typing import List
from zillow.session import Session


log = logging.getLogger(__name__)


class Apartments:
    BASE_URL = "https://www.zillow.com"

    def __init__(self, urls: List[str]):
        self.session = Session()
        self.partial_urls = urls

    def data(self):
        rental_urls = []
        for url in self.partial_urls:
            rental_urls.extend(self._get_rental_unit_urls(f"{self.BASE_URL}{url}"))
        log.debug(rental_urls)
        unit_data = []
        for url in rental_urls:
            # TODO: parallel process
            # TODO: cache lot_id for dev
            unit_data.append(Property(url, self.session).fetch())
        return unit_data
        
    def _get_rental_unit_urls(self, url):
        building = self._scrape_rental_results(url)
        address = building.get("address")
        floor_plans = building.get("floorPlans")
        if not floor_plans:
            # TODO: debug why
            log.error(f"Failed to find units for {url}")
            return []
        fallback = building.get("bestMatchedUnit").get("hdpUrl")
        unit_urls = []
        for plan in floor_plans:
            if "units" not in plan or not plan.get("units"):
                log.debug(f"No units found: {plan}")
                unit_urls.append(f"{self.BASE_URL}{fallback.replace(building.get('zpid'), plan.get('zpid'))}")
                continue
            for unit in plan.get("units"):
                unit_num = '-'.join(re.findall(r'[0-9]+', str(unit.get('unitNumber'))))
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


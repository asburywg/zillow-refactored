import json
import logging
import re
from typing import List, Optional

from zillow.file_util import write_intermediary
from zillow.session import Session
from zillow.zipcode_util import fetch_zipcodes

log = logging.getLogger(__name__)

"""
>>> Search("columbus", "ohio")
>>> Search("Columbus", "OH", exclude_zipcodes=[43085])
>>> Search(zipcodes=[43085, 43206])
"""


class Search:
    BASE_URL = "https://www.zillow.com"
    DEFAULT_OUTPUT_SETTINGS = {
        "write_raw_zipcodes": False,
        "raw_zipcode_file": "./data/zillow/zipcode/{}.json",
        "write_raw_listings": True,
        "raw_listings_file": "./data/zillow/listings.json",
    }

    def __init__(self, city: str = None, state: str = None,
                 exclude_zipcodes: List[int] = None,
                 zipcodes: List[int] = None, output_settings: Optional[dict] = None):
        """
        Search listings by city/state (using zipcode lookup) or a list of zipcodes
        :param city: location used for zipcode lookup
        :param state: location used for zipcode lookup
        :param exclude_zipcodes: list of zipcodes to exclude from city/state zipcode lookup
        :param zipcodes: skip zipcode lookup and only search for specified list
        :param output_settings: controls which intermediary files are written and where to
        """
        # user input should be either city/state or [zipcodes]
        if output_settings is None:
            output_settings = self.DEFAULT_OUTPUT_SETTINGS
        if not (city and state) and not zipcodes or (city and state and zipcodes):
            raise TypeError("Specify *either* city and state or a list of zipcodes to search.")
        self.zipcodes = zipcodes if zipcodes else fetch_zipcodes(city, state, exclude_zipcodes)
        log.info(f"Searching {len(self.zipcodes)} zipcodes: {self.zipcodes}")
        self.output_settings = output_settings
        self.session = Session()

    def get_all_listings(self):
        listings = []
        for zc in self.zipcodes:
            listings.extend(self._zipcode_listings(zc))
        if self.output_settings.get("write_raw_listings"):
            write_intermediary(listings, self.output_settings.get("raw_listings_file"))
        return listings

    def _zipcode_listings(self, zipcode: int):
        log.info(f'Scraping listings in {zipcode}')
        for_rent = self._scrape_results(f"{self.BASE_URL}/homes/for_rent/{zipcode}_rb/")
        log.info(f'Listings FOR_RENT in {zipcode}: {len(for_rent)}')
        for_sale = self._scrape_results(f"{self.BASE_URL}/homes/for_sale/{zipcode}_rb/")
        log.info(f'Listings FOR_SALE in {zipcode}: {len(for_sale)}')
        listings = for_rent + for_sale
        if self.output_settings.get("write_raw_zipcodes"):
            write_intermediary(listings, self.output_settings.get("raw_zipcode_file").format(zipcode))
        return listings

    def _scrape_results(self, url, acc=None):
        if acc is None:
            acc = []
        page_text = self.session.get(url).text
        query_state = re.search(r'!--(\{"queryState".*?)-->', page_text)
        if not query_state:
            raise Exception("Bad result from Zillow", page_text)
        data = json.loads(query_state.group(1))
        """control pagination"""
        current_page = data.get("queryState").get("pagination").get("currentPage") if "pagination" in data.get(
            "queryState") else 1
        total_pages = data.get('cat1').get("searchList").get("totalPages")
        next_url = data.get('cat1').get("searchList").get("pagination").get('nextUrl') if "pagination" in data.get(
            'cat1').get("searchList") else None
        total_listings = data.get("cat1").get("searchList").get("totalResultCount")
        """results"""
        res = data.get('cat1').get("searchResults").get("listResults")
        acc.extend(res)
        log.debug(f'Progress: {current_page} of {total_pages} pages ({len(acc)} of {total_listings} listings)')
        if next_url and current_page < total_pages:
            return self._scrape_results(f"{self.BASE_URL}{next_url}", acc)
        assert len(acc) == total_listings  # TODO: rm
        return acc

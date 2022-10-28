import json
import logging
import re
from typing import List

from zillow.file_util import write_json, file_exists, read_json, is_json_file
from zillow.session import Session
from zillow.zipcode_util import fetch_zipcodes

log = logging.getLogger(__name__)

"""
>>> Search("columbus", "ohio")
>>> Search("Columbus", "OH", exclude_zipcodes=[43085])
>>> Search(zipcodes=[43085, 43206])
"""

# output setting defaults
DATA_DIR: str = "./data"
CACHE_RAW_ZIPCODES: bool = True
WRITE_RAW_LISTINGS: bool = False
RAW_ZIPCODES_FILE: str = "zillow/zipcode/{}.json"
RAW_LISTINGS_FILE: str = "zillow/listings.json"


class Search:
    BASE_URL = "https://www.zillow.com"

    def __init__(self, city: str = None, state: str = None,
                 exclude_zipcodes: List[int] = None,
                 zipcodes: List[int] = None):
        """
        Search listings by city/state (using zipcode lookup) or a list of zipcodes
        :param city: location used for zipcode lookup
        :param state: location used for zipcode lookup
        :param exclude_zipcodes: list of zipcodes to exclude from city/state zipcode lookup
        :param zipcodes: skip zipcode lookup and only search for specified list
        """
        # user input should be either city/state or [zipcodes]
        if not (city and state) and not zipcodes or (city and state and zipcodes):
            raise TypeError("Specify *either* city and state or a list of zipcodes to search.")
        self.zipcodes = zipcodes if zipcodes else fetch_zipcodes(city, state, exclude_zipcodes)
        log.info(f"Searching {len(self.zipcodes)} zipcodes: {self.zipcodes}")
        self.output_settings = {}
        self.set_output_settings()
        self.session = Session()

    def set_output_settings(self, data_dir: str = DATA_DIR,
                            cache_raw_zipcodes: bool = CACHE_RAW_ZIPCODES,
                            raw_zipcode_file: str = RAW_ZIPCODES_FILE,
                            write_raw_listings: bool = WRITE_RAW_LISTINGS,
                            raw_listings_file: str = RAW_LISTINGS_FILE):
        """
        Controls file output settings, call before fetching listings to update
        :param data_dir: root dir for all other paths
        :param cache_raw_zipcodes: boolean to write each zipcode listings from zillow
        :param raw_zipcode_file: relative path for zipcode files
        :param write_raw_listings: boolean to write all raw results for Search zipcodes
        :param raw_listings_file: relative path for raw listings
        """
        data_dir = f"{data_dir}/" if data_dir[-1] != "/" else data_dir
        if not is_json_file(raw_zipcode_file) or not is_json_file(raw_listings_file):
            raise TypeError("raw_zipcode_file and raw_listings_file must be relative paths to JSON files")
        self.output_settings = {"write_raw_zipcodes": cache_raw_zipcodes,
                                "write_raw_listings": write_raw_listings,
                                "raw_zipcode_file": data_dir + raw_zipcode_file,
                                "raw_listings_file": data_dir + raw_listings_file}
        self.print_output_settings()

    def get_all_listings(self, read_cache: bool = False):
        """
        Returns all FOR_SALE/FOR_RENT listings for zipcodes in Search
        :param read_cache: read zipcode intermediary files if exists to reduce calls to zillow
        :return:
        """
        listings = []
        for zc in self.zipcodes:
            listings.extend(self._zipcode_listings(zc, read_cache))
        if self.output_settings.get("write_raw_listings"):
            write_json(listings, self.output_settings.get("raw_listings_file"))
        return listings

    def _zipcode_listings(self, zipcode: int, read_cache: bool):
        cache_file = self.output_settings.get("raw_zipcode_file").format(zipcode)
        if read_cache and file_exists(cache_file):
            log.info(f"Reading from cached file: {cache_file}")
            return read_json(cache_file)

        log.info(f'Scraping listings in {zipcode}')
        for_rent = self._scrape_results(f"{self.BASE_URL}/homes/for_rent/{zipcode}_rb/")
        log.info(f'Listings FOR_RENT in {zipcode}: {len(for_rent)}')
        for_sale = self._scrape_results(f"{self.BASE_URL}/homes/for_sale/{zipcode}_rb/")
        log.info(f'Listings FOR_SALE in {zipcode}: {len(for_sale)}')
        listings = for_rent + for_sale

        if self.output_settings.get("write_raw_zipcodes"):
            write_json(listings, cache_file)
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

    def print_output_settings(self):
        log.info(f"OUTPUT SETTINGS:\n\tCache raw listings by zipcode:\t"
                 f" {self.output_settings.get('write_raw_zipcodes')} ({self.output_settings.get('raw_zipcode_file')})"
                 f"\n\tWrite all raw listings:\t\t\t {self.output_settings.get('write_raw_listings')} "
                 f"({self.output_settings.get('raw_listings_file')})")

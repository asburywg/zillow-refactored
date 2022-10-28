import logging
from typing import List

from zillow.zipcode_util import fetch_zipcodes


log = logging.getLogger(__name__)


"""
>>> Search("columbus", "ohio")
>>> Search("Columbus", "OH", exclude_zipcodes=[43085])
>>> Search(zipcodes=[43085, 43206])
"""


class Search:
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


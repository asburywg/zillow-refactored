import logging
from typing import List, Optional

from uszipcode import SearchEngine, ZipcodeTypeEnum

log = logging.getLogger(__name__)

"""
>>> fetch_zipcodes_info("columbus", "ohio", None)
>>> fetch_zipcodes("columbus", "ohio", [43085])
"""


def fetch_zipcodes_info(city: str, state: str, zipcode_type: Optional[ZipcodeTypeEnum] = ZipcodeTypeEnum.Standard):
    """
    Fetches zipcode info for a city/state, defaults to only STANDARD zipcodes
    :param city:
    :param state:
    :param zipcode_type: set to None for all available zipcodes
    :return: list of SimpleZipcode objects
    """
    search = SearchEngine()
    zipcodes = search.by_city_and_state(city=city, state=state, returns=None, zipcode_type=zipcode_type)
    z_type = zipcode_type.name if zipcode_type else 'total'
    log.debug(f"Found {len(zipcodes)} {z_type} zipcodes in {city.upper()}, {state.upper()}")
    return zipcodes


def fetch_zipcodes(city: str, state: str, exclude: List[int] = None):
    """
    Fetches list of Standard zipcodes for city/state, optionally exclude zipcodes from results
    :param city:
    :param state:
    :param exclude: list of int zipcodes
    :return: int zipcodes
    """
    if not exclude:
        exclude = []
    return [int(zc.zipcode) for zc in fetch_zipcodes_info(city, state) if int(zc.zipcode) not in exclude]

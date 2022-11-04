import logging
from .file_util import export_csv, write_json
from .listings import Search
from .formatter import *
from .property import Apartments

FOR_SALE_LISTINGS_FILE = "for-sale.csv"
FOR_RENT_LISTINGS_FILE = "for-rent.csv"


def format_data(listings, apartment_file=None, include_apartments=False):
    """transform and format listing data"""

    data = ListingFormatter(listings)
    data.select(DETAILS, ADDRESS, HOME)

    """apartments"""
    apartment_urls = data.apartment_urls()
    if apartment_file:
        write_json(apartment_urls, apartment_file)

    data.remove_apartments()

    if include_apartments:
        logging.info(f"Fetching more data for {len(apartment_urls)} apartments")
        # formatting is fragmented, updates to `data` (listings df) must be applied to apartments df
        apt_data = Apartments(apartment_urls).data()
        apt_fmt = ListingFormatter(apt_data)
        apt_fmt.select(DETAILS_APT, ADDRESS_APT, HOME_APT)
        apt_fmt.fix_urls()
        data.concat_df(apt_fmt.df)

    """calc columns"""
    data.price_per_sqft()
    data.remove_dupes()

    return data.df


class ExportListings:

    def __init__(self, city: str, state: str):
        self.city = city
        self.state = state

    def run(self):
        search = Search(city=self.city, state=self.state)
        search.set_output_settings(cache_raw_zipcodes=False)
        listings = search.get_all_listings()
        df = format_data(listings)
        export_csv(df[df["status"] == "FOR_SALE"], FOR_SALE_LISTINGS_FILE)
        export_csv(df[df["status"] == "FOR_RENT"], FOR_RENT_LISTINGS_FILE)

import logging
from datetime import datetime

from zillow.file_util import export_csv, write_json
from zillow.listings import Search
from zillow.formatter import *
from zillow.property import Apartments

logging.basicConfig(level=logging.INFO)

APARTMENT_URL_FILE = "./data/results/{}/{}-apartments.json"
LISTINGS_FILE = "./data/results/{}/{}-listings.csv"


def format_data(listings, apartment_file=None, include_apartments=False):
    """transform and format listing data"""

    data = ListingFormatter(listings)
    # print(data.sample())

    """filter"""
    # data.filter_for_sale()
    # data.filter_for_rent()

    """columns"""
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


def main():
    city, state = "columbus", "ohio"
    search = Search(city=city, state=state)
    listings = search.get_all_listings(read_cache=True)
    # format and export
    date = datetime.now().date().strftime("%Y%m%d")
    df = format_data(listings, APARTMENT_URL_FILE.format(date, city))
    export_csv(df, LISTINGS_FILE.format(date, city))


if __name__ == "__main__":
    main()

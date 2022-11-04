import logging
from datetime import datetime

from zillow.file_util import export_csv, write_json
from zillow.listings import Search
from zillow.formatter import *
from zillow.property import Apartments

logging.basicConfig(level=logging.INFO)

APARTMENT_URL_FILE = "./data/results/{}/{}-apartments.json"
LISTINGS_FILE = "./data/results/{}/{}-listings.csv"
FOR_SALE_LISTINGS_FILE = "./data/results/{}/{}-for-sale.csv"
FOR_RENT_LISTINGS_FILE = "./data/results/{}/{}-for-rent.csv"
ZIPCODE_FILE = "./data/results/{}/{}-zipcodes.json"


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


def stats(df):
    by_status = df.groupby('status').agg({'url': 'count', 'listed': 'mean'}).reset_index()
    by_zipcode = df.groupby(['zipcode', 'status']).agg(
        {'url': 'count', 'listed': 'mean', 'price_per_sqft': 'mean'}).reset_index()
    print(by_zipcode)
    print(by_status)


def export_listings(city="columbus", state="ohio"):
    date = datetime.now().date().strftime("%Y%m%d")
    search = Search(city=city, state=state)
    write_json(search.zipcodes, ZIPCODE_FILE.format(date, city))
    listings = search.get_all_listings(read_cache=True)
    df = format_data(listings, APARTMENT_URL_FILE.format(date, city))
    export_csv(df, LISTINGS_FILE.format(date, city))
    stats(df)
    export_csv(df[df["status"] == "FOR_SALE"], FOR_SALE_LISTINGS_FILE.format(date, city))
    export_csv(df[df["status"] == "FOR_RENT"], FOR_RENT_LISTINGS_FILE.format(date, city))


if __name__ == "__main__":
    export_listings()

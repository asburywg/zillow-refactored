import logging

from zillow.file_util import export_csv
from zillow.listings import Search
from zillow.formatter import *
from zillow.property import Apartments

logging.basicConfig(level=logging.INFO)


def format_data(listings, include_apartments=False):
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
    # TODO: collect stats by zipcode (rent/sale)
    listings = search.get_all_listings(read_cache=True)
    df = format_data(listings)
    export_csv(df, "./data/results/col-listings-no-apt.csv")


if __name__ == "__main__":
    main()

import logging

from zillow.listings import Search
from zillow.formatter import ListingFormatter, DETAILS, HOME, ADDRESS

"""
Input: city, state ?? list of zip codes to exclude || list of zip codes
---
create python package:
- use user input zip codes or fetch zip codes for city, state (less optional exclude list)
- for each zip code, search zillow for FOR_SALE and FOR_RENT listings (in parallel w/ diff UA?)
- concat and cache raw listing data from zillow (JSON)
- format and output data for export (CSV)
---
colab notebook allows user to
- Search("area" || [zipcodes], exclude=[zipcodes])
    - Search(city="columbus", state="ohio")
    - Search(city="columbus", state="ohio", exclude_zipcodes=[12345])
    - Search(zipcodes=[1234, 1235, 1246])
- export_listings(type=FOR_SALE||FOR_RENT)
    - control output columns
- export_raw_listings()
"""

logging.basicConfig(level=logging.INFO)


def format_data(listings):
    """transform and format listing data"""

    data = ListingFormatter(listings)
    # print(data.sample())

    """filter"""
    data.filter_for_sale()
    # data.filter_for_rent()

    """columns"""
    data.select(DETAILS, ADDRESS, HOME, ["units"])
    data.price_per_sqft()
    data.fix_urls()

    # TODO: parse rental street unit num
    # TODO: explode rental units

    print(data.df)


def main():
    search = Search(zipcodes=[43085])
    listings = search.get_all_listings(read_cache=True)
    format_data(listings)
    # TODO: export formatted


if __name__ == "__main__":
    main()

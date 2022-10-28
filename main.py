import json
import logging

from zillow.listings import Search
from zillow.formatter import ListingFormatter, DETAILS, HOME, ADDRESS
from zillow.property import Property

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
---
goal:
- FOR_SALE / FOR_RENT given a city or zipcodes
- export formatted data for sheets import
- eval 1% rules against FOR_SALE homes
    - get comparable rents
        - zestimate rent
        - similar listed FOR_RENT (by area, bed, bath, etc)
        - take average for total FOR_RENT / zipcode average - per sqft
        - get price history for non-listed properties 
        - user input
"""

logging.basicConfig(level=logging.INFO)


def format_data(listings):
    """transform and format listing data"""

    data = ListingFormatter(listings)

    """filter"""
    # data.filter_for_sale()
    data.filter_for_rent()

    # print(data.sample())

    """columns"""
    data.select(DETAILS, ADDRESS, HOME, ["units", "lotId"])
    data.price_per_sqft()
    # data.fix_urls()

    # TODO: parse rental street unit num
    # TODO: explode rental units
    # TODO: try getting home details for rentals

    print(data.df)


def main():
    search = Search(zipcodes=[43085])
    listings = search.get_all_listings(read_cache=True)
    format_data(listings)
    # TODO: export formatted


# if __name__ == "__main__":
#     main()


# url = "https://www.zillow.com/homedetails/7830-Alta-Dr-503-103-Columbus-OH-43085/2071536922_zpid/"
# url = "/b/the-thomas-columbus-oh-ByK4GB/"
# url = "/b/traditions-at-worthington-woods-worthington-oh-5gKnT7/"
# url = "/b/187-wilson-dr-columbus-oh-5gpSDL/"
url = "/b/summerside-apartments-columbus-oh-5wyXP7/"
rp = Property(url=url)

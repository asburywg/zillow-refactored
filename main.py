import logging

from zillow.file_util import export_csv
from zillow.listings import Search
from zillow.formatter import *
from zillow.property import Apartments

# TODO: mv to README
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

"""
partial apartment URL: "/b/the-thomas-columbus-oh-ByK4GB/"
missing: url, house_type, listed, street (with unit), beds, baths, area
contains multiple units: ['https://www.zillow.com/homedetails/7830-Alta-Dr-7802-206-Columbus-OH-43085/2071530435_zpid/', 'https://www.zillow.com/homedetails/7830-Alta-Dr-509-201-Columbus-OH-43085/2071503156_zpid/', 'https://www.zillow.com/homedetails/7830-Alta-Dr-7821-203-Columbus-OH-43085/2071506841_zpid/', 'https://www.zillow.com/homedetails/7830-Alta-Dr-7833-202-Columbus-OH-43085/2071507505_zpid/', 'https://www.zillow.com/homedetails/7830-Alta-Dr-503-103-Columbus-OH-43085/2071536922_zpid/']
fetch property data for each unit url
"""

logging.basicConfig(level=logging.INFO)


def format_data(listings):
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
    logging.info(f"Fetching more data for {len(apartment_urls)} apartments")
    data.remove_apartments()

    # formatting is fragmented, updates to `data` (listings df) must be applied to apartments df
    apt_data = Apartments(apartment_urls).data()
    apt_fmt = ListingFormatter(apt_data)
    apt_fmt.select(DETAILS_APT, ADDRESS_APT, HOME_APT)
    apt_fmt.fix_urls()
    data.concat_df(apt_fmt.df)

    """calc columns"""
    data.price_per_sqft()

    return data.df


def main():
    # city, state = "columbus", "ohio"
    # search = Search(city=city, state=state)
    zipcodes = [43085, 43201, 43202, 43203, 43204]
    search = Search(zipcodes=zipcodes)
    # TODO: collect stats by zipcode (rent/sale)
    listings = search.get_all_listings(read_cache=True)
    df = format_data(listings)
    export_csv(df, "./data/results/listings-1.csv")


if __name__ == "__main__":
    main()

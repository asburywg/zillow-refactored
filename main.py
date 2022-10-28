

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
- export_listings(type=FOR_SALE||FOR_RENT)
    - control output columns
- export_raw_listings()
"""


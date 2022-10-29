import operator  # https://docs.python.org/3/library/operator.html
from typing import List
import pandas as pd

pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)
pd.set_option('display.max_colwidth', None)


class Formatter:
    """
    generic class to format a pandas dataframe
    all functions mutate dataframe
    """

    def __init__(self, dict_array: List[dict]):
        self.df = pd.json_normalize(dict_array)

    """helper"""

    def columns(self):
        return self.df.columns

    """filter"""

    def filter(self, column, op, value):
        self.df = self.df.loc[op(self.df[column], value)]

    """columns"""

    def select_rename_columns(self, *column_mappings):
        df_cols = set(self.columns())
        rename_mapping = {}
        keep_columns = []
        for columns in column_mappings:
            if type(columns) == dict:
                verify_renames = df_cols.intersection(set(columns.values()))
                assert len(verify_renames) == 0, f"Rename column name exists in data already: {verify_renames}"
                rename_mapping.update(columns)
                keep_columns.extend(list(columns.values()))
            if type(columns) == list:
                keep_columns.extend(columns)
        df = self.df.rename(columns=rename_mapping)
        self.df = df[keep_columns]
        return self.df

    def new_calc_column(self, column, op, col1, col2):
        self.df[column] = op(self.df[col1], self.df[col2])

    def apply_column_func(self, column, func, *args):
        self.df[column] = self.df[column].apply(lambda x: func(x, *args))

    def filter_apply_column_func(self, column, filter_func, func, *args):
        self.df.loc[filter_func(self.df[column]), column] = self.df[column].apply(lambda x: func(x, *args))


class ListingFormatter:
    """
    Zillow listing specific transformations and filters
    """

    def __init__(self, listings: List[dict]):
        self.listings = listings
        self.fmt = Formatter(listings)

    @property
    def df(self):
        return self.fmt.df

    @property
    def columns(self):
        return self.fmt.columns()

    def sample(self, n=10):
        return self.df.head(n)

    def reset(self):
        self.fmt = Formatter(self.listings)

    def apartment_urls(self):
        return list(self.fmt.df.loc[~self.fmt.df['url'].str.startswith('http')]['url'])

    def remove_apartments(self):
        self.fmt.df = self.df.loc[self.fmt.df['url'].str.startswith('http')]

    def concat_df(self, df):
        self.fmt.df = pd.concat([self.fmt.df, df])

    """filters"""

    def filter_for_rent(self):
        self.fmt.filter('statusType', operator.eq, "FOR_RENT")

    def filter_for_sale(self):
        self.fmt.filter('statusType', operator.eq, "FOR_SALE")

    """custom columns"""

    def select(self, *args):
        self.fmt.select_rename_columns(*args)

    def price_per_sqft(self, name="price_per_sqft", price_col='listed', area_col='area'):
        self.fmt.new_calc_column(name, operator.truediv, price_col, area_col)
        self.fmt.apply_column_func(name, round, 2)


"""formatting listings"""
# predefined sets of column mappings ('column_name': 'rename_column'} or ['column_name', ...]
DETAILS = {
    "statusType": "status",
    "detailUrl": "url",
    "hdpData.homeInfo.homeType": "home_type",
    "unformattedPrice": "listed"
}
ADDRESS = {
    "addressStreet": "street",
    "addressState": "state",
    "addressCity": "city",
    "addressZipcode": "zipcode",
}
HOME = ["beds", "baths", "area"]
HOME_EXT = {
    "hdpData.homeInfo.taxAssessedValue": "tax_assessed",
    "hdpData.homeInfo.lotAreaValue": "lot_area",
    "hdpData.homeInfo.lotAreaUnit": "lot_area_unit"
}
ADDRESS_EXT = {
    "latLong.latitude": "latitude",
    "latLong.longitude": "longitude",
}
ZESTIMATE = {
    "zestimate": "zestimate",
    "hdpData.homeInfo.rentZestimate": "rent_zestimate"
}
PRICE_CHANGE = {
    "hdpData.homeInfo.datePriceChanged": "price_change_date",
    "hdpData.homeInfo.priceChange": "price_change_amount",
}

"""corresponding formatting for apartments (data from homedetails)"""
DETAILS_APT = {
    "homeStatus": "status",
    "hdpUrl": "url",
    "homeType": "home_type",
    "price": "listed",
    "streetAddress": "street"
}
ADDRESS_APT = ['state', 'city', 'zipcode']
HOME_APT = {
    'bedrooms': 'beds',
    'bathrooms': 'baths',
    'livingArea': 'area'
}
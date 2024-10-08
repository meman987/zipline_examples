from norgatedata import StockPriceAdjustmentType
from zipline_norgatedata import (
    register_norgatedata_equities_bundle,
    register_norgatedata_futures_bundle )

#
# Copy to ~/.zipline/extension.py
#

# assuming rand_stock_data.py has been placed in site-packages/date/bundles
# a rather bad idéa but it will do for now...
from zipline.data.bundles import register
#from zipline.data.bundles import random_stock_data
from clenow_book import random_stock_data

register('random_stock_data', random_stock_data.random_stock_data, calendar_name='NYSE')

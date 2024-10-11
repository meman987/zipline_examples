#
# Copy to ~/.zipline/extension.py
#

#from norgatedata import StockPriceAdjustmentType
#from zipline_norgatedata import (
#    register_norgatedata_equities_bundle,
#    register_norgatedata_futures_bundle )

from zipline.data.bundles import register
from random_stock_data import random_stock_data

register('random_stock_data', random_stock_data.random_stock_data, calendar_name='NYSE')

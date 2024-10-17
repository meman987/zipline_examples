#
# Copy to ~/.zipline/extension.py
#

#from norgatedata import StockPriceAdjustmentType
#from zipline_norgatedata import (
#    register_norgatedata_equities_bundle,
#    register_norgatedata_futures_bundle )

from zipline.data.bundles import register
from data_management import (   random_stock_data
                              , random_futures_data
                              , yf_stock_data
                              #, csi_futures_data
                              #, sc_futures_data
                             )

register('random_stock_data',   random_stock_data.random_stock_data,     calendar_name='NYSE')
register('random_futures_data', random_futures_data.random_futures_data, calendar_name='us_futures')
register('yf_stock_data',       yf_stock_data.yf_stock_data,             calendar_name='NYSE')
#register('csi_futures_data',    csi_futures_data.csi_futures_data,       calendar_name='us_futures')
#register('sc_futures_data',     sc_futures_data.sc_futures_data,         calendar_name='us_futures')

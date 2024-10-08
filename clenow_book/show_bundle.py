from zipline.data import bundles
from zipline.data.data_portal import DataPortal
#from zipline.utils.calendar_utils import get_calendar

from clenow_book import random_stock_data

import pprint
import pandas as pd


pprint.pprint(bundles.bundles)

bundle = bundles.load('quandl')
assets = bundle.asset_finder.retrieve_all(bundle.asset_finder.sids)
pprint.pprint(assets)

bundles.register('random_stock_data', random_stock_data.random_stock_data, calendar_name='NYSE')
bundle = bundles.load('random_stock_data')
assets = bundle.asset_finder.retrieve_all(bundle.asset_finder.sids)
pprint.pprint(assets)


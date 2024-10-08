# Data Management

Here are some examples and notes taken when reading Trading Evolved by 
[Andreas Clenow](https://www.clenow.com/books).

## Test data

We need some data to work with. Here we'll use the [yfinance](https://pypi.org/project/yfinance/)
package to download some test data. Run `python3 yf.py` and some test data should end
up in the folder `./csv`.


## Import data into zipline

Make sure that `PYTHONPATH` includes this folder: `export PYTHONPATH=$PYTHONPATH:$HOME/<git_repo>/clenow_book/1_Data_Management`.
[`direnv`](https://direnv.net/) is a good tool to automate management of environment variables!


Have a look at `extension.py` in `zipline-files` and copy it to `~/.zipline`.

Then do try this:

```
zipline ingest -b random_stock_data

# cleanup
zipline bundles
zipline clean -b random_stock_data --before 2024-10-07
zipline bundles


# view the contents of a bundles
python3
from zipline.data import bundles
from random_stock_data import random_stock_data
bundles.register('random_stock_data', random_stock_data.random_stock_data, calendar_name='NYSE')

bundle = bundles.load('random_stock_data')

bundle.asset_finder.retrieve_all(bundle.asset_finder.sids)
[Equity(0 [AAPL]), Equity(1 [SPY])]
```

## Calendars

Exchange calendars are key in zipline. There cannot be any transactions outside the window where 
the exchange is open. There are packages that are maintained by others, now that quantopian is
'dead'. See [pandas-market-calendars](https://pypi.org/project/pandas-market-calendars/) and 
[exchange-calendars](https://pypi.org/project/exchange-calendars/).

`calendar_example.py` and `calendar_example2.py` shows some use cases for calendars.



## Problem - no 'US' equities after ingest of random_stock_data

Running `python3 show_bundles2.py` will give an error for our bundle `random_stock_data`.

The table exchanges in the metadata stored in sqlite seams to be messed up.

```
cd ~/.zipline/data/random_stock_data
cd 2024...
sqlite3 assets-7.sqlite
.tables
.headers on
select * from exchanges;
```

One solution can be found here (see last post): https://github.com/quantopian/zipline/issues/2517
It involves patching a file in the zipline packages. Not ideal but the simplest solution I've found so
far.

Here is a snippet that shows where the zipline package is stored. This is usefull when having multiple
python versions installed (packages that are installed sometimes do *not* end up where you'd think).

```
python3

import sys
import importlib

print(sys.path)
print(importlib.util.find_spec("zipline"))
```

Copy file `zipline-files/assets.py` to this folder and try `show_bundles2.py` again.

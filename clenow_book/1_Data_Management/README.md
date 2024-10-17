# Data Management

Here are some examples and notes taken when reading Trading Evolved by 
[Andreas Clenow](https://www.clenow.com/books).

Some good stuff about Zipline Data Management can be found [here](https://pypi.org/project/zipline-norgatedata/).
In particular, see the note about Zipline only using 20 years of data and 
suggested patch! Also, check out this note about [futures contracts](https://github.com/quantopian/zipline/issues/2340).


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
# or
zipline clean -b random_stock_data --keep-last=1

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

`show_calendar.py` shows some use cases for calendars.


## View Time Series

Try `show_bundle.py`. You'll probably get an error. See below for a solution.


## Problem - no 'US' equities after ingest of random_stock_data

Running `python3 show_bundles.py` will give an error for our bundle `random_stock_data`.

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

Copy file `zipline-files/assets.py` to this folder and try `show_bundles.py` again.


## More tickers for Yahoo Finance

IMPORTANT: The Yahoo Finance Futures data is not back adjusted so it shouldn't be used without corrections!

Here are some tickers that can be used with `yf.py`:

currencies:      `6A=F,6B=F,6C=F,6E=F,6J=F,6N=F,6S=F`
softs:           `CT=F,CC=F,OJ=F,SB=F,KC=F,LBS=F`
meat:            `GF=F,HE=F,LE=F`
grains:          `ZC=F,ZO=F,KE=F,ZR=F,ZM=F,ZS=F`
equities:        `ES=F,YM=F,NQ=F,RTY=F`
fixed income:    `ZB=F,ZN=F,ZF=F,ZT=F`
precious metals: `GC=F,SI=F,HG=F,PA=F,PL=F`
energy:          `CL=F,HO=F,RB=F,NG=F,BZ=F`

All: `6A=F,6B=F,6C=F,6E=F,6J=F,6N=F,6S=F,CT=F,CC=F,OJ=F,SB=F,KC=F,LBS=F,GF=F,HE=F,LE=F,ZC=F,ZO=F,KE=F,ZR=F,ZM=F,ZS=F,ES=F,YM=F,NQ=F,RTY=F,ZB=F,ZN=F,ZF=F,ZT=F,GC=F,SI=F,HG=F,PA=F,PL=F,CL=F,HO=F,RB=F,NG=F,BZ=F`

NOTE: Use single quotes around these in bash.

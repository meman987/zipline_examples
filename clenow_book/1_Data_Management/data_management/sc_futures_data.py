import os
import sys
import glob
import datetime

import pandas as pd
import numpy as np
from tqdm import tqdm                # Used for progress bar

from .helpers import *

cwd = os.path.dirname(os.path.realpath(__file__))
to_year = int(datetime.date.today().year) + 1

conf = f'{cwd}/contracts.yaml'
expirations_lookup = get_exps(conf, 'calF', 1970, to_year)
expirations_lookup['exp'] = expirations_lookup['exp'].apply(int2dt)

data_path = os.environ['SC_DATA']
meta_path = f'{cwd}/sc_meta.csv'

futures_lookup = pd.read_csv(meta_path, index_col=0)
df_files = None

# returns: sc_root_symbol, zl_root_symbol, zl_symbol, expiration_date
def to_zipline_format(filename_):
  if len(filename_.split('-')) != 2:
    return None, None, None, None

  symbol_, exch   = filename_.split('-')
  sc_symbol       = symbol_[:len(symbol_)-3]
  zl_symbol       = None
  expiration_date = None  

  root_       = futures_lookup.loc[futures_lookup.sc_symbol==sc_symbol, 'root_symbol']
  root_symbol = root_.iloc[0] if root_.shape[0] != 0 else None

  decade          = int(symbol_[-2:])
  year            = decade + (2000 if decade < 50 else 1900)   
  contract_code   = symbol_[-3]

  if not root_symbol is None:
    zl_symbol      = f'{root_symbol}{contract_code}{decade}'
    el = expirations_lookup
    expiration_date = el.loc[(el['root_symbol'] == root_symbol) & (el['year']==year) & (el['contract_code']==contract_code), 'exp']
    expiration_date = expiration_date.iloc[0] if expiration_date.shape[0] != 0 else np.nan
  
  return sc_symbol, root_symbol, zl_symbol, expiration_date

def sc_futures_data(environ, asset_db_writer, minute_bar_writer, daily_bar_writer, adjustment_writer,
                        calendar, start_session, end_session,cache, show_progress, output_dir):
  global df_files

  filenames = [f[:-4].split('/')[-1] for f in glob.glob(f'{data_path}/*.dly')]

  if not filenames:
    raise ValueError("No files found in folder.")

  df_files = pd.DataFrame(data=filenames, columns=['filename'])
  df_files[['sc_root_symbol','zl_root_symbol','zl_symbol','expiration_date']] = df_files.filename.apply(lambda x: to_zipline_format(x)).apply(pd.Series)
  
  if df_files.zl_root_symbol.isnull().sum().any():
    print('WARNING: Files with missing Zipline root symbol will be ignored!')
    print(df_files[df_files.zl_root_symbol.isnull()])
  df_files = df_files[~df_files.zl_root_symbol.isnull()]
   
  if df_files.expiration_date.isnull().sum().any():
    print('ERROR: missing expiration dates! See ./missing_expiration_data.csv for details.')
    print(df_files[df_files.expiration_date.isnull()])
    df_files[df_files.expiration_date.isnull()].to_csv('./missing_expiration_data.csv')
    sys.exit(1)

  divs     = pd.DataFrame(columns=['sid','amount','ex_date','record_date','declared_date','pay_date'])
  splits   = pd.DataFrame(columns=['sid','ratio','effective_date'])
  metadata = pd.DataFrame(columns=('start_date','end_date','auto_close_date','symbol','root_symbol',
                                  'expiration_date','notice_date','tick_size','exchange'))

  sessions = calendar.sessions_in_range(start_session, end_session)
  daily_bar_writer.write( process_futures(df_files.filename.tolist(), sessions, metadata) )
  
  adjustment_writer.write(splits=splits, dividends=divs)    

  # write the meta data
  root_symbols = futures_lookup.copy()
  root_symbols['root_symbol_id'] = root_symbols.index.values
  del root_symbols['minor_fx_adj']    
  asset_db_writer.write(futures=metadata, root_symbols=root_symbols)

def make_meta(sid, metadata, df, sessions):
  start_date = df.index[0]
  end_date = df.index[-1]        
  ac_date = end_date + pd.Timedelta(days=1)

  symbol = df.iloc[0]['symbol']
  root_sym = df.iloc[0]['root_symbol']
  exchng = futures_lookup.loc[futures_lookup['root_symbol'] == root_sym ]['exchange'].iloc[0]
  exp_date = end_date

  # Tip to improve: Set notice date to one month prior to expiry for commodity markets.
  notice_date = ac_date
  tick_size = 0.0001   # Placeholder

  metadata.loc[sid] = start_date, end_date, ac_date, symbol, \
                    root_sym, exp_date, notice_date, tick_size, exchng

def process_futures(filenames, sessions, metadata):

  # Loop the symbols with progress bar, using tqdm
  sid = 0
  for filename in tqdm(filenames, desc='Loading data...'):
    sid += 1

    print(f'{filename}...', end='', flush=True)
    
    df = pd.read_csv(f'{data_path}/{filename}.dly', index_col=[0], parse_dates=[0])
    df.columns = list(map(lambda x: x.strip().lower(), df.columns))

    if df.shape[0] == 0:
      print(f'WARNING: empty file {filename}')
      continue

    if ((df<0).any()).any():
      print(f'WARNING: Negative prices are not supported:\n{(df<0).any()}. These are set to 0.')
      print(f'shape:{df.shape} df.dtypes:{df.dtypes}...', end='', flush=True)
      for col in df.columns[(df<0).any()]:
        df.loc[col][df[col]<0] = 0

    sc_root_symbol, zl_root_symbol, zl_symbol, expiration_date = to_zipline_format(filename)

    if zl_root_symbol is None or expiration_date is None:
      print('ERROR: None found is for root symbol {zl_root_symbol} and/or expiration date {expiration_date} in {filename}')
      sys.exit(1)
    
    df['root_symbol']     = zl_root_symbol
    df['symbol']          = zl_symbol
    df['expiration_date'] = expiration_date

    # Check for minor currency quotes
    adjustment_factor = futures_lookup.loc[
            futures_lookup['root_symbol'] == df.iloc[0]['root_symbol']
            ]['minor_fx_adj'].iloc[0]

    if adjustment_factor*1==0:
      print('ERROR: Incorrect min_fx_adj {adjustment_factor} for {filename}')
      sys.exit(1)
      
    df['open'] *= adjustment_factor
    df['high'] *= adjustment_factor
    df['low'] *= adjustment_factor
    df['close'] *= adjustment_factor

    # Avoid potential high / low data errors in data set
    # And apply minor currency adjustment for USc quotes
    df['high'] = df[['high', 'close']].max(axis=1) 
    df['low']  = df[['low', 'close']].min(axis=1) 
    df['high'] = df[['high', 'open']].max(axis=1)
    df['low']  = df[['low', 'open']].min(axis=1) 

    # Synch to the official exchange calendar
    df = df.reindex(sessions.tz_localize(None))[df.index[0]:df.index[-1] ]

    # df.fillna(method='ffill', inplace=True)
    df = df.ffill()
    df = df.dropna()

    # Cut dates before 2000, avoiding Zipline issue
    # df = df['2000-01-01':]

    # Prepare contract metadata
    make_meta(sid, metadata, df, sessions)

    del df['openinterest']
    del df['expiration_date']
    del df['root_symbol']
    del df['symbol']

    yield sid, df        
        


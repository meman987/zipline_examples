import re
import sys
import pandas as pd
from os import listdir

from pathlib import Path


# Change the path to where you have your data
path = Path('./csv')

def yf_stock_data(environ,
                      asset_db_writer,
                      minute_bar_writer,
                      daily_bar_writer,
                      adjustment_writer,
                      calendar,
                      start_session,
                      end_session,
                      cache,
                      show_progress,
                      output_dir):
    
    symbols = [f[:-4] for f in listdir(path)]

    if not symbols:
        raise ValueError("No symbols found in folder.")

    divs = pd.DataFrame(columns=['sid','amount','ex_date','record_date','declared_date','pay_date'])
    splits = pd.DataFrame(columns=['sid','ratio','effective_date'])
    metadata = pd.DataFrame(columns=('start_date','end_date','auto_close_date','symbol','exchange'))

    sessions = calendar.sessions_in_range(start_session, end_session)
    daily_bar_writer.write( process_stocks(symbols, sessions, metadata, divs) )
    asset_db_writer.write(equities=metadata)
    adjustment_writer.write(splits=splits,dividends=divs)


def process_stocks(symbols, sessions, metadata, divs):
    
    for sid, symbol in enumerate(symbols):
        print(f'Loading {symbol}...', end='', flush=True)

        df = pd.read_csv('{}/{}.csv'.format(path, symbol), index_col=[0], parse_dates=[0])
        df.columns = list(map(lambda x: x.lower(), df.columns))
        # divs = pd.DataFrame(columns=['sid','amount','ex_date','record_date','declared_date','pay_date'])

        start_date = df.index[0]
        end_date = df.index[-1]

        if ((df<0).any()).any():
            print(f'Negative prices are not supported:\n{(df<0).any()}')
            print(f'shape:{df.shape} df.dtypes:{df.dtypes}...', end='', flush=True)
            for col in df.columns[(df<0).any()]:
                df[col][df[col]<0] = 0

        # Synch to the official exchange calendar
        df = df.reindex(sessions.tz_localize(None))[start_date:end_date]

        df.ffill(inplace=True)
        df.dropna(inplace=True)
#        df.fillna(0, inplace=True)
        ac_date = end_date + pd.Timedelta(days=1)             # auto close date

        metadata.loc[sid] = start_date, end_date, ac_date, symbol, 'NYSE'

        l = list(map(lambda x: not re.search('dividend.*', x, re.IGNORECASE) is None, df.columns))
        
        # If there's dividend data, add that to the dividend DataFrame
        if True in l:
            idx = l.index(True)
            
            # Slice off the days with dividends
            tmp = df[df.iloc[:,idx] != 0.0].iloc[:,idx]

            if tmp.shape[0] > 0:

                div = pd.DataFrame(data=tmp.index.tolist(), columns=['ex_date'])
                div['record_date']   = pd.NaT
                div['declared_date'] = pd.NaT
                div['pay_date']      = pd.NaT
                div['amount']        = tmp.tolist()
                div['sid']           = sid

                ind = pd.Index(range(divs.shape[0], divs.shape[0] + div.shape[0]))
                div.set_index(ind, inplace=True)

                divs = pd.concat([divs, div], axis=0)

                print(f'divs:\n{divs}...')
            
        yield sid, df

import yfinance as yf
from pathlib import Path

csv_folder = Path('./csv')
tickers = ['SPY','AAPL']

csv_folder.mkdir(parents=True, exist_ok=True)

for ticker in tickers:
  print(f'{ticker}...', end='', flush=True)
  
  da1 = yf.Ticker(ticker).actions.reset_index()
  da1['Date'] = da1.Date.dt.strftime('%Y%m%d').astype(int)
  da2 = yf.download(ticker, period="max").reset_index()
  da2['Date'] = da2.Date.dt.strftime('%Y%m%d').astype(int)

  da = da2.merge(da1, how='outer', left_on='Date', right_on='Date')
  da = da.fillna(0)
  da.to_csv(f'./csv/{ticker}.csv', index=False)

  print(da)

  
  '''
  print(da1.actions)
  print(da1.actions)
  print(da1.history_metadata)
  print(da1.dividends)
  print(da1.splits)
  print(da1.capital_gains)  # only for mutual funds & etfs
  '''


import pickle
import argparse

import pandas as pd
import pyfolio as pf
import matplotlib.pyplot as plt

def create_args_parser():
  parser = argparse.ArgumentParser(prog='view_stats.py', description='Show stats for trades stored in a pickle file.')
  parser.add_argument('action',     help='What to do', choices=['tearsheet','csv','plot','ratios'])
  parser.add_argument('filename',   help='Name of pickle file to use' )
  parser.add_argument('--from_',    help='From date', default='1970-1-1' )
  return parser

def read_pickle(filename_):
  f = open(filename_, 'rb')
  results = pickle.load(f)
  return results

def to_csv(result_):
  results.to_csv(f'{args.filename.removesuffix(".pickle")}.csv')  
  print(results)
  print(f'Saved content to {args.filename.removesuffix(".pickle")}.csv')

def plot(results_):
  ax1 = plt.subplot(211)
  results_.portfolio_value.plot(ax=ax1)
  ax1.set_ylabel('Portfolio Value')
  ax2 = plt.subplot(212, sharex=ax1)
  results_.ASSET.plot(ax=ax2)
  ax2.set_ylabel('Stock Price')
  plt.show()

def tearsheet(results_, from_dt):
  returns, positions, transactions = pf.utils.extract_rets_pos_txn_from_zipline(results_)

  pf.create_full_tear_sheet(returns, positions=positions, transactions=transactions,
                            live_start_date=from_dt, round_trips=True)

def positions_tearsheet(results_):
  returns, positions, transactions = pf.utils.extract_rets_pos_txn_from_zipline(results_)
  pf.create_position_tear_sheet(returns, positions)

def returns_tearsheet(results_):
  returns, positions, transactions = pf.utils.extract_rets_pos_txn_from_zipline(results_)
  pf.create_returns_tear_sheet(returns)

def simple_tearsheet(results_):
  returns, positions, transactions = pf.utils.extract_rets_pos_txn_from_zipline(results_)
  pf.create_simple_tear_sheet(returns, positions=positions, transactions=transactions)

def drawdown(results_):
  returns, positions, transactions = pf.utils.extract_rets_pos_txn_from_zipline(results_)
  pf.plot_drawdown_periods(returns, top=5).set_xlabel('Date');

def roundtrip(results_):
  # Optional: Sector mappings may be passed in as a dict or pd.Series. If a mapping is
  # provided, PnL from symbols with mappings will be summed to display profitability by sector.
  sect_map = {'COST': 'Consumer Goods', 'INTC':'Technology', 'CERN':'Healthcare', 'GPS':'Technology',
            'MMM': 'Construction', 'DELL': 'Technology', 'AMD':'Technology'}

  returns, positions, transactions = pf.utils.extract_rets_pos_txn_from_zipline(results_)
  pf.create_round_trip_tear_sheet(returns, positions, transactions, sector_mappings=sect_map)

def roundtrip_stats(results_):
  returns, positions, transactions = pf.utils.extract_rets_pos_txn_from_zipline(results_)
  rts = pf.round_trips.extract_round_trips(transactions,
                                           portfolio_value=positions.sum(axis='columns') / (returns + 1))
  pf.round_trips.print_round_trip_stats(rts)

def ratios(results_):
  returns, positions, transactions = pf.utils.extract_rets_pos_txn_from_zipline(results_)
  calmar = pf.timeseries.calmar_ratio(returns)
  print('calmar', calmar)
  
  cs = pf.timeseries.common_sense_ratio(returns)
  print('common sense', cs)
  
  sharpe = pf.timeseries.sharpe_ratio(returns)
  print('sharpe', sharpe)

  sortino = pf.timeseries.sortino_ratio(returns)
  print('sortino', sortino)

  tail = pf.timeseries.tail_ratio(returns)
  print('tail', tail)

  omega = pf.timeseries.omega_ratio(returns)
  print('omega', omega)

  
if __name__ == '__main__':
  parser = create_args_parser()
  args = parser.parse_args()
  print(args)

  results = read_pickle(args.filename)
  if args.action == 'csv':
    to_csv(results)
  elif args.action == 'plot':
    plot(results)
  elif args.action == 'tearsheet':
    tearsheet(results_, args.from_)
  elif args.action == 'ratios':
    ratios(results)
  else:
    print(f'Unknown action {args.action}')


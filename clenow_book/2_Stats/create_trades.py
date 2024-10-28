import pickle
import datetime
import argparse

from zipline import run_algorithm
from zipline.api import order_target_percent, symbol,  order_target, record


import matplotlib.pyplot as plt
import pandas as pd


def initialize(context):
  context.i = 0
  context.asset = symbol(args.ticker)
  context.index_average_window = 100

def handle_data_mean(context, data):
  equities_hist = data.history(context.asset, "close", 
                                 context.index_average_window, "1d")

  if equities_hist.iloc[-1] > equities_hist.mean():
    stock_weight = 1.0
  else:
    stock_weight = 0.0

  order_target_percent(context.asset, stock_weight)

def handle_data_ma(context, data):
  context.i += 1
  if context.i < 300:
    return

  # Compute averages
  # data.history() has to be called with the same params
  # from above and returns a pandas dataframe.
  short_mavg = data.history(context.asset, 'price', bar_count=100, frequency="1d").mean()
  long_mavg = data.history(context.asset, 'price', bar_count=300, frequency="1d").mean()

  # Trading logic
  if short_mavg > long_mavg:
    # order_target orders as many shares as needed to achieve the desired number of shares.
    order_target(context.asset, 100)
  elif short_mavg < long_mavg:
    order_target(context.asset, 0)

  # Save values for later inspection
  record(ASSET=data.current(context.asset, 'price'),
    short_mavg=short_mavg,
    long_mavg=long_mavg)
    
def analyze(context, perf):
  fig = plt.figure(figsize=(12, 8))

  ax = fig.add_subplot(311)
  ax.set_title('Strategy Results')
  ax.semilogy(perf['portfolio_value'], linestyle='-', 
            label='Equity Curve', linewidth=3.0)
  ax.legend()
  ax.grid(False)

  # Second chart
  ax = fig.add_subplot(312)
  ax.plot(perf['gross_leverage'], 
        label='Exposure', linestyle='-', linewidth=1.0)
  ax.legend()
  ax.grid(True)

  # Third chart
  ax = fig.add_subplot(313)
  ax.plot(perf['returns'], label='Returns', linestyle='-.', linewidth=1.0)
  ax.legend()
  ax.grid(True)

def create_args_parser():
  parser = argparse.ArgumentParser(prog='create_trades2.py', description='Create some trades that can be analyzed.')
  parser.add_argument('ticker',     help='Ticker to trade.')
  parser.add_argument('--alg',      help='What to do', choices=['mean','MA'], default='MA')

  parser.add_argument('--bundle',   help='Name of bundle to use.', default='yf_stock_data')
  parser.add_argument('--from_',    help='From year.',
                                    type=lambda d: datetime.datetime.strptime(d, '%Y-%m-%d').date(),
                                    default='1981-6-1')
  parser.add_argument('--to',       help='To year.',
                                    type=lambda d: datetime.datetime.strptime(d, '%Y-%m-%d').date(),
                                    default='2024-10-01')
  return parser

if __name__ == '__main__':
  parser = create_args_parser()
  args = parser.parse_args()
  print(args)

  results = run_algorithm(
    start          = pd.Timestamp(args.from_),
    end            = pd.Timestamp(args.to),
    initialize     = initialize, 
    analyze        = analyze, 
    handle_data    = handle_data_ma if args.alg=='MA' else handle_data_mean, 
    capital_base   = 10000, 
    data_frequency = 'daily', 
    bundle         = args.bundle
   )

  with open('trades.pickle', 'wb') as file:
    pickle.dump(results, file, protocol=pickle.HIGHEST_PROTOCOL)
    print(f'Result saved in trades.pickle')
    
  plt.show()

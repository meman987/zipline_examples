import sys
import argparse
import pandas as pd

from pathlib import Path

csv_folder = Path('./csv')

def create_args_parser():
  parser = argparse.ArgumentParser(prog='yf.py', description='Download CSV-files from Yahoo Finance.')
  parser.add_argument('--tickers',     help='Comma separated list of tickers to download', default='AAPL,IBM')
  return parser

if __name__ == '__main__':
  parser = create_args_parser()
  args = parser.parse_args()
  print(args)

  for ticker in args.tickers.split(','):
    print(f'{ticker}...', end='', flush=True)

    df = pd.read_csv(f'{csv_folder}/{ticker}.csv').set_index('Date')
    gaps = df.Close.shift().fillna(0) - df.Open

    print(gaps)

    df.Open = df.Open   + gaps
    df.High = df.High   + gaps
    df.Low  = df.Low    + gaps
    df.Close = df.Close + gaps

    print( (df.Open.shift().fillna(0) - df.Open) )

    sys.exit(0)


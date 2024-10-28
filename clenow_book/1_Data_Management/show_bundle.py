#
# 241016
#
# Various methods to check the data in a bundle
#

__author__ = 'Jonas Colmsjö'

import os
import re
import sys
import pprint
import argparse

import pandas as pd

import zipline
from zipline import run_algorithm
from zipline.data import bundles
from zipline.pipeline import Pipeline
from zipline.pipeline.data import EquityPricing
from zipline.pipeline.loaders import EquityPricingLoader
from zipline.pipeline.engine import SimplePipelineEngine
from zipline.api import symbol, continuous_future


#
# Pipeline
# =========
#
# Pipelines cannot be used with Futures :-|
#

def _pipeline_engine_and_calendar_for_bundle(bundle, start_date, end_date):
  bundle_data = bundles.load(bundle)
  
  def choose_loader(column):
    return EquityPricingLoader(
      bundle_data.equity_daily_bar_reader,
      bundle_data.adjustment_reader,
    None)

  calendar = bundle_data.equity_daily_bar_reader.trading_calendar

  return SimplePipelineEngine(choose_loader, bundle_data.asset_finder), calendar


def run_pipeline_against_bundle(pipeline, start_date, end_date, bundle):
  engine, calendar = _pipeline_engine_and_calendar_for_bundle(bundle, start_date, end_date)

  if not calendar.is_session(start_date):
    start_date = calendar.minute_to_session(start_date, direction='next')

  if not calendar.is_session(end_date):
    end_date = calendar.minute_to_session(end_date, direction='previous')

  return engine.run_pipeline(pipeline, start_date, end_date)

def run(start, end, bundle_):
  print('--------------------------------')
  try:
    res = run_pipeline_against_bundle(
            Pipeline(columns={'close': EquityPricing.close.latest}, domain=zipline.pipeline.domain.US_EQUITIES),
                     start, end, bundle=bundle_)
    return res

  except Exception as e:
    print(f'\nError: No data found for the selected period and bundle. start:{start}, end:{end}, bundle:{bundle_}.')
    print('This seams to be a bug, a solution is found here: https://github.com/quantopian/zipline/issues/2517')
    print('\nzipline error message:')
    print(e)
    sys.exit(1)

# Create a basic DataFrame with time series as columns
def to_ts_df(zl_df):
  df = zl_df.reset_index()
  #df['ticker'] = list(map(lambda x: f'{x.sid}:{x.symbol}:{x.exchange}:{x.country_code}', df['level_1']))
  df['ticker'] = list(map(lambda x: x.symbol, df['level_1']))
  df['Date'] = df['level_0'].dt.strftime('%Y%m%d').astype(int)
  df = df.pivot(index='Date', columns='ticker', values='close')
  df.columns = sorted(df.columns)
  return df

#
# Algorithm
# =========
#
# Use run_algorithm to iterate over the data in a bundle and output the result.  
# Pipelines cannot be used with futures so this seams to be the simplest way.
# It is *very* slow though!!
#

out_data = []

def initialize(context):
  context.i = 0
  bundle = bundles.load(args.bundle)
  assets = bundle.asset_finder.retrieve_all(bundle.asset_finder.sids)
  root_symbols = list(map(lambda x: x.root_symbol, assets))

  context.universe = [ continuous_future(symbol,
                                         offset=0,
                                         roll='volume',
                                         adjustment='mul') for symbol in root_symbols ]
  

def handle_data(context, data):
  context.i += 1
  if context.i % 10 == 0:
    print(f'{data.current_session.date()}...', end='', flush=True)
    print(out_data)

  out_data.append( data.current(
        context.universe, 
        fields=['close','volume','openinterest','expiration_date'], 
  ))


#
# Main
# ====
  
def create_args_parser():
  parser = argparse.ArgumentParser(prog='show_bundle.py', description='Show contents of zipline bundle.')
  parser.add_argument('action',     help='what to do', choices=['list','show','pipeline','metadata','viewfutures'])
  parser.add_argument('--bundle',   help='Name of bundle to show data for.')
  parser.add_argument('--from_',    help='From year.', default='1970-1-3')
  parser.add_argument('--to',       help='To year.', default='2025-12-31')
  return parser

if __name__ == '__main__':
  parser = create_args_parser()
  args = parser.parse_args()
  print(args)

  if args.action == 'viewfutures':
    results = run_algorithm(
      start          = pd.Timestamp(args.from_),
      end            = pd.Timestamp(args.to),
      initialize     = initialize,
      handle_data    = handle_data,
      capital_base   = 10000, 
      bundle         = args.bundle
    )

    print(out_data)
    sys.exit(0)

  
  # Make the bundles that are installed available here - run_algorithm does this for us
  path_ = os.path.expanduser('~/.zipline/extension.py')
  with open(path_, 'r') as f:
    py = f.read()
    exec(py)

  if args.action == 'list':
    pprint.pprint(bundles.bundles)
    
  elif args.action == 'show':
    if args.bundle is None:
      print('usage: python3 show_bundle.py show --bundle BUNDLE_NAME')
      sys.exit(1)
    bundle = bundles.load(args.bundle)
    assets = bundle.asset_finder.retrieve_all(bundle.asset_finder.sids)
    pprint.pprint(assets)

  elif args.action == 'pipeline':
    if args.bundle is None or args.from_ is None or args.to is None:
      print('usage: python3 show_bundle.py show --bundle BUNDLE_NAME --from_ 20XX --to 20YY')
      sys.exit(1)
      
    zl_df = run(args.from_, args.to, args.bundle)
    df = to_ts_df(zl_df)
    print(df)
    df.to_csv(f'./{args.bundle}.csv', index=True)
    print(f'Saved the bundle {args.bundle}.csv')

  elif args.action == 'metadata':
    if args.bundle is None :
      print('usage: python3 show_bundle.py metadata --bundle BUNDLE_NAME')
      sys.exit(1)

    bundle = bundles.load(args.bundle)
    assets = bundle.asset_finder.retrieve_all(bundle.asset_finder.sids)

    l = list(map(lambda x: x.to_dict(), assets))
    df = pd.DataFrame(l).set_index('sid')

    print(df.to_string())
    
    df.to_csv(f'./{args.bundle}_metadata.csv', index=True)
    print(f'Saved the bundle metadata to {args.bundle}_metadata.csv')
    
  else:
    print(f'Unknown action {args.action}')



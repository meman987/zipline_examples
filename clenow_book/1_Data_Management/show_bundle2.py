import pandas as pd

from zipline.data import bundles
from zipline.pipeline.data import USEquityPricing
from zipline.pipeline.loaders import USEquityPricingLoader
from zipline.pipeline.engine import SimplePipelineEngine

from random_stock_data import random_stock_data
bundles.register('random_stock_data', random_stock_data.random_stock_data, calendar_name='NYSE')

# Needed when using run_pipeline_against_bundle
from zipline.pipeline import Pipeline
from zipline.pipeline.data import USEquityPricing


def _pipeline_engine_and_calendar_for_bundle(bundle, start_date, end_date):
    bundle_data = bundles.load(bundle)
    pipeline_loader = USEquityPricingLoader(
        bundle_data.equity_daily_bar_reader,
        bundle_data.adjustment_reader,
        None)

    def choose_loader(column):
        print(f'Checking columns: {column}')
        if column in USEquityPricing.columns:
            return pipeline_loader
        raise ValueError('No PipelineLoader registered for column %s.' % column)

    calendar = bundle_data.equity_daily_bar_reader.trading_calendar
    
    return SimplePipelineEngine(choose_loader,bundle_data.asset_finder), calendar


def run_pipeline_against_bundle(pipeline, start_date, end_date, bundle):
    engine, calendar = _pipeline_engine_and_calendar_for_bundle(bundle, start_date, end_date)

    if not calendar.is_session(start_date):
        print('Fix start_date:', start_date)
        start_date = calendar.minute_to_session(start_date, direction='next')
        print('New start_date:', start_date)

    if not calendar.is_session(end_date):
        print('Fix end_date:', end_date)
        end_date = calendar.minute_to_session(end_date, direction='previous')
        print('New end_date:', end_date)

    return engine.run_pipeline(pipeline, start_date, end_date)

def run(start, end, bundle_):
    print('--------------------------------')
    try:
        res = run_pipeline_against_bundle(
            Pipeline({'close': USEquityPricing.close.latest}),
                     start, end, bundle=bundle_)
        return res
    
    except Exception as e:
        print(f'\nError: No data found for the selected period and bundle. start:{start}, end:{end}, bundle:{bundle_}.')
        print('This seams to be a bug, a solution is found here: https://github.com/quantopian/zipline/issues/2517')
        print('\nzipline error message:')
        print(e)

# Create a basic DataFrame with time series as columns
def to_ts_df(zl_df):
    df = zl_df.reset_index()
    #df['ticker'] = list(map(lambda x: f'{x.sid}:{x.symbol}:{x.exchange}:{x.country_code}', df['level_1']))
    df['ticker'] = list(map(lambda x: x.symbol, df['level_1']))
    df['Date'] = df['level_0'].dt.strftime('%Y%m%d').astype(int)
    df = df.pivot(index='Date', columns='ticker', values='close')
    df.columns = sorted(df.columns)
    return df


zl_df = run('2012','2013','quandl')
df = to_ts_df(zl_df)
df.to_csv('./quandl.csv', index=True)
print('Saved the bundle quandl to quandl.csv')
print(df)

zl_df = run('1998','2024','random_stock_data')
df = to_ts_df(zl_df)
df.to_csv('./random_stock_data.csv', index=True)
print('Saved the bundle random_stock_data to random_stock_data.csv')
print(df)

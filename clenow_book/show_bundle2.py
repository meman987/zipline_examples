import pandas as pd

from zipline.data import bundles
from zipline.pipeline.data import USEquityPricing
from zipline.pipeline.loaders import USEquityPricingLoader
from zipline.pipeline.engine import SimplePipelineEngine

from clenow_book import random_stock_data
bundles.register('random_stock_data', random_stock_data.random_stock_data, calendar_name='NYSE')

# Needed when using run_pipeline_against_bundle
from zipline.pipeline import Pipeline
from zipline.pipeline.data import USEquityPricing


def _pipeline_engine_and_calendar_for_bundle(bundle, start_date, end_date):
    bundle_data = bundles.load(bundle)
    pipeline_loader = USEquityPricingLoader(
        bundle_data.equity_daily_bar_reader,
        bundle_data.adjustment_reader,
        None
    )

    def choose_loader(column):
        print(f'Checking columns: {column}')
        if column in USEquityPricing.columns:
            return pipeline_loader
        raise ValueError(
            'No PipelineLoader registered for column %s.' % column
        )

    calendar = bundle_data.equity_daily_bar_reader.trading_calendar
    # sessions = calendar.sessions_in_range(start_date, end_date)
    
    return (
        SimplePipelineEngine(
            choose_loader,
            bundle_data.asset_finder,
        ),
        calendar,
    )


def run_pipeline_against_bundle(pipeline, start_date, end_date, bundle):
    engine, calendar = _pipeline_engine_and_calendar_for_bundle(bundle, start_date, end_date)

    #start_date = pd.Timestamp(start_date, tz='utc')
    if not calendar.is_session(start_date):
        #start_date = calendar.minute_to_session_label(start_date, direction='next')
        print('Fix start_date:', start_date)
        start_date = calendar.minute_to_session(start_date, direction='next')
        print('New start_date:', start_date)

    #end_date = pd.Timestamp(end_date, tz='utc')
    if not calendar.is_session(end_date):
        print('Fix end_date:', end_date)
        end_date = calendar.minute_to_session(end_date, direction='previous')
        print('end_date:', end_date)

    return engine.run_pipeline(pipeline, start_date, end_date)



def run(start, end, bundle_):
    print('--------------------------------')
    try:
        res = run_pipeline_against_bundle(
            Pipeline({'close': USEquityPricing.close.latest}),
            start,
            end,
            bundle=bundle_)
        print(res)
    
    except Exception as e:
        print(f'\nError: No data found for the selected period and bundle. start:{start}, end:{end}, bundle:{bundle_}.')
        print('This seams to be a bug, a solution is found here: https://github.com/quantopian/zipline/issues/2517')
        print('\nzipline error message:')
        print(e)


run('2012','2013','quandl')
run('2023','2024','random_stock_data')
            

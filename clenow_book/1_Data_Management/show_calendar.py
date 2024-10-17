#
# 241016
#
# Some methods to view Exchange Calendars
#

__author__ = 'Jonas Colmsjö'

import sys
import argparse
from datetime import time

import pandas as pd
import pandas_market_calendars as mcal

import exchange_calendars as xcals

from zipline.utils.calendar_utils import get_calendar, days_at_time

def create_args_parser():
  parser = argparse.ArgumentParser(prog='show_calendar.py', description='Show contents of exchange calendars.')
  parser.add_argument('action',     help='Type of calendar', choices=['zipline','pandas','excal'])
  parser.add_argument('--cal',      help='Calendar to view', default='NYSE')
  parser.add_argument('--from_',    help='From date.',       default='1970-1-3')
  parser.add_argument('--to',       help='To date.',         default='2025-12-31')
  parser.add_argument('--tz',       help='Timezone',         default='America/New_York')
  return parser

if __name__ == '__main__':
  parser = create_args_parser()
  args = parser.parse_args()
  print(args)

  if args.action == 'zipline':

    nyse_calendar = get_calendar(args.cal)

    sessions = nyse_calendar.sessions_in_range( pd.Timestamp(args.from_), pd.Timestamp(args.to) )
    opens    = nyse_calendar.first_minutes[sessions]
    closes   = nyse_calendar.schedule.loc[sessions, "close" ]

    print('sessions:\n', sessions)
    print('opens:\n', opens)
    print('closes:\n', closes)

  if args.action == 'pandas':
    nyse = mcal.get_calendar(args.cal)
    print('Timezone:', nyse.tz.zone)

    holidays = nyse.holidays()
    print('Some holidays:', holidays.holidays[-5:])

    print('Regular market hours:', nyse.regular_market_times)

    print(nyse.valid_days(start_date=args.from_, end_date=args.to))


    schedule = nyse.schedule(start_date=args.from_, end_date=args.to)
    print(schedule)

    early = nyse.schedule(start_date=args.from_, end_date=args.to)
    print(early)
    
    ts = pd.Timestamp(f'{args.to} 12:00', tz=args.tz)
    print(f'Check if market is open at {ts}:', end='')
    print(nyse.open_at_time(early, ts))
    
    ts = pd.Timestamp(f'{args.to} 16:00', tz=args.tz)
    print(f'Check if market is open at {ts}:', end='')
    print(nyse.open_at_time(early, ts))


  elif args.action == 'excal':

    # exchange_calendars - https://github.com/gerrymanoim/exchange_calendars?tab=readme-ov-file
    # ==================
    #
    # cli:  ecal XNYS 2024
    #


    print(xcals.get_calendar_names(include_aliases=False))

    cal_ = xcals.get_calendar(args.cal)

    print(cal_.schedule.loc[args.from_:args.to])

    print(cal_.is_session("2022-01-01"))

    print(cal_.sessions_in_range(args.from_, args.to))

    print(cal_.sessions_window(args.from_, 7))

    print(cal_.date_to_session(args.from_, direction="next"))

  else:
    print(f'Unknown action {args.action}')


import sys
from datetime import time

import pandas as pd
import pandas_market_calendars as mcal
import exchange_calendars as xcals


# pandas_market_calendars
# =======================

nyse = mcal.get_calendar('NYSE')
print(nyse.tz.zone)

holidays = nyse.holidays()
print(holidays.holidays[-5:])

print(nyse.regular_market_times)

print(nyse.valid_days(start_date='2016-12-20', end_date='2017-01-10'))


schedule = nyse.schedule(start_date='2016-12-30', end_date='2017-01-10')
print(schedule)

early = nyse.schedule(start_date='2012-07-01', end_date='2012-07-10')
print(early)

print(nyse.open_at_time(early, pd.Timestamp('2012-07-03 12:00', tz='America/New_York')))

print(nyse.open_at_time(early, pd.Timestamp('2012-07-03 16:00', tz='America/New_York')))



# exchange_calendars - https://github.com/gerrymanoim/exchange_calendars?tab=readme-ov-file
# ==================
#
# cli:  ecal XNYS 2024
#

print(xcals.get_calendar_names(include_aliases=False))

xnys = xcals.get_calendar("XNYS")

print(xnys.schedule.loc["2021-12-29":"2022-01-04"])

print(xnys.is_session("2022-01-01"))

print(xnys.sessions_in_range("2022-01-01", "2022-01-11"))

print(xnys.sessions_window("2022-01-03", 7))

print(xnys.date_to_session("2022-01-01", direction="next"))



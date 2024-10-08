import pandas as pd
from zipline.utils.calendar_utils import get_calendar, days_at_time


nyse_calendar = get_calendar("NYSE")

# july 15 is friday, so there are 3 sessions in this range (15, 18, 19)
sessions = nyse_calendar.sessions_in_range( pd.Timestamp("2016-07-15"), pd.Timestamp("2016-07-19") )
opens    = nyse_calendar.first_minutes[sessions]
closes   = nyse_calendar.schedule.loc[sessions, "close" ]

print('sessions:\n', sessions)
print('opens:\n', opens)
print('closes:\n', closes)



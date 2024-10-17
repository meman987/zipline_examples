#!/bin/bash
#
#   /home/me/.local/lib/python3.10/site-packages


if [ $# -ne 1 ]; then
    echo "usage: ./do_patch.sh <site-packages-path>"
    exit 0
fi

cp assets.py         $1/zipline/assets/
cp calendar_utils.py $1/zipline/utils/

# TODO: Problem, need to check!
#cp  exchange_calendar.py $1/exchange_calendars/

cp extension.py ~/.zipline/


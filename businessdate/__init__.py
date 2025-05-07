# -*- coding: utf-8 -*-

# businessdate
# ------------
# Python library for generating business dates for fast date operations
# and rich functionality.
#
# Author:   sonntagsgesicht, based on a fork of Deutsche Postbank [pbrisk]
# Version:  0.5, copyright Wednesday, 18 September 2019
# Website:  https://github.com/sonntagsgesicht/businessdate
# License:  Apache License 2.0 (see LICENSE file)


# todo
#  float(D - B) = B.year_fraction(D)
#  int(D - B) = B.diff_in_days(D)
#  float(D) = float(D - BusinessDate()) = BusinessDate().year_fraction(D)
#  int(D) = int(D - BusinessDate()) = BusinessDate().diff_in_days(D)


__doc__ = 'Python library for generating business dates for fast date operations and rich functionality.'
__version__ = '0.7.1'
__dev_status__ = '4 - Beta'
__date__ = 'Wednesday, 07 May 2025'
__author__ = 'sonntagsgesicht, based on a fork of Deutsche Postbank [pbrisk]'
__email__ = 'sonntagsgesicht@icloud.com'
__url__ = 'https://github.com/sonntagsgesicht/' + __name__
__license__ = 'Apache License 2.0'
__dependencies__ = ()
__dependency_links__ = ()
__data__ = ()
__scripts__ = ()
__theme__ = 'sphinx_rtd_theme'

import logging
logging.getLogger(__name__).addHandler(logging.NullHandler())

# todo:
#  [ ] separate date, time, datetime, timedelta with nice __repr__
#  [ ] add beautiful date
#  [ ] lighter interface (more use of __dunder__)
#  [ ] add docs for float and int conversion
#  [ ] move holidays management to BusinessDayAdjustment
#  [ ] move day_count management to BusinessDayCount
#  [ ] remove duplicates from BusinessRange.adjust()

from .businessholidays import BusinessHolidays
from .businessperiod import BusinessPeriod
from .businessdate import BusinessDate
from .businessdatelist import BusinessDateList
from .businessrange import BusinessRange
from .businessschedule import BusinessSchedule

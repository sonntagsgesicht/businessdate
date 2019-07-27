# -*- coding: utf-8 -*-

#  businessdate
#  ------------
#  A fast, efficient Python library for generating business dates inherited
#  from float for fast date operations. Typical banking business methods
#  are provided like business holidays adjustment, day count fractions.
#  Beside dates generic business periods offer to create time periods like
#  '10Y', '3 Months' or '2b'. Periods can easily added to business dates.
#
#  Author:  pbrisk <pbrisk_at_github@icloud.com>
#  Copyright: 2016, 2017 Deutsche Postbank AG
#  Website: https://github.com/pbrisk/businessdate
#  License: APACHE Version 2 License (see LICENSE file)

# __name__ = 'businessdate'
__doc__ = 'Python library for generating business dates for fast date operations and rich functionality.'
__version__ = '0.5'
__author__ = 'Deutsche Postbank AG [pbrisk]'
__email__ = 'pbrisk_at_github@icloud.com'
__url__ = 'https://github.com/pbrisk/businessdate'
__dependencies__ = ()

from .businessholidays import BusinessHolidays
from .businessperiod import BusinessPeriod
from .businessdate import BusinessDate
from .businessrange import BusinessRange
from .businessschedule import BusinessSchedule

# -*- coding: utf-8 -*-

# businessdate
# ------------
# Python library for generating business dates for fast date operations
# and rich functionality.
# 
# Author:   sonntagsgesicht, based on a fork of Deutsche Postbank [pbrisk]
# Version:  0.5, copyright Sunday 28 July 2019
# Website:  https://github.com/sonntagsgesicht/businessdate
# License:  Apache License 2.0 (see LICENSE file)


from datetime import datetime

# __name__ = 'businessdate'
__doc__ = 'Python library for generating business dates for fast date operations and rich functionality.'
__version__ = '0.5'
__date__ = datetime.today().strftime('%A %d %B %Y')
__author__ = 'sonntagsgesicht, based on a fork of Deutsche Postbank [pbrisk]'
__email__ = 'sonntagsgesicht@icloud.com'
__url__ = 'https://github.com/sonntagsgesicht/businessdate'
__license__ = 'Apache License 2.0'
__dependencies__ = ()

from .businessholidays import BusinessHolidays
from .businessperiod import BusinessPeriod
from .businessdate import BusinessDate
from .businessrange import BusinessRange
from .businessschedule import BusinessSchedule

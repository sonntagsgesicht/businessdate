# -*- coding: utf-8 -*-

#  businessdate
#  ------------
#  A fast, efficient Python library for generating business dates inherited
#  from float for fast date operations. Typical banking business methods
#  are provided like business holidays adjustment, day count fractions.
#  Beside dates generic business periods offer to create time periods like
#  '10Y', '3 Months' or '2b'. Periods can easily added to business dates.
#
#  Author:  sonntagsgesicht <sonntagsgesicht@github.com>
#  Copyright: 2016, 2017 Deutsche Postbank AG
#  Website: https://github.com/sonntagsgesicht/businessdate
#  License: APACHE Version 2 License (see LICENSE file)


from datetime import timedelta


class BasePeriodFloat(float):
    pass


class BasePeriodTimedelta(timedelta):
    pass


class BasePeriod(object):
    pass


def set_base_period(mode='float'):
    if mode == 'float':
        class BasePeriod(BasePeriodFloat):
            pass
    else:
        class BasePeriod(BasePeriodTimedelta):
            pass


set_base_period()

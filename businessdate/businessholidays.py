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


from datetime import date

from .holidays import target_days


class BusinessHolidays(list):
    """
    holiday calendar class
    """

    def __init__(self, iterable=()):
        if iterable:
            # iterable = map(BusinessDate, iterable)
            iterable = [bd if isinstance(bd, date) else date(bd.year, bd.month, bd.day) for bd in iterable]
        super(BusinessHolidays, self).__init__(iterable)

    def __contains__(self, item):
        if super(BusinessHolidays, self).__contains__(item):
            return True
        return super(BusinessHolidays, self).__contains__(date(item.year, item.month, item.day))


class TargetHolidays(BusinessHolidays):
    """
    holiday calendar class for ecb target2 holidays
    """

    def __contains__(self, item):
        if not super(TargetHolidays, self).__contains__(date(item.year, 1, 1)):
            # add tar days if not done jet
            self.extend(list(target_days(item.year).keys()))
        return super(TargetHolidays, self).__contains__(item)

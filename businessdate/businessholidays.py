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


from datetime import date

from .holidays import target_days


class BusinessHolidays(list):
    """ holiday calendar class

    A :class:`BusinessHolidays` instance imitated a list of :class:`datetime.date`
    which can be used to check if a :class:`BusinessDate` is
    included as holiday.

    For convenience input need not to be of type :class:`datetime.date`.
    Duck typing is enough, i.e. having properties
    `year`, `month` and `day`.
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
    """ holiday calendar class of ecb target2 holidays

    Target holidays are

    * Jan, 1st
    * Good Friday
    * Easter Monday
    * May, 1st
    * Christmas Day
    * Boxing Day

    """

    def __contains__(self, item):
        if not super(TargetHolidays, self).__contains__(date(item.year, 1, 1)):
            # add tar days if not done jet
            self.extend(list(target_days(item.year).keys()))
        return super(TargetHolidays, self).__contains__(item)

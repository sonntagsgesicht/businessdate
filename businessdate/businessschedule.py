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

from .businessperiod import BusinessPeriod
from .businessdate import BusinessDate
from .businessrange import BusinessRange


class BusinessSchedule(BusinessRange):
    def __init__(self, start, end, step, roll=None):
        """ class to build date schedules incl. start and end date

        :param BusinessDate start: start date of schedule
        :param BusinessDate end: end date of schedule
        :param BusinessPeriod step: period distance of two dates
        :param BusinessDate roll: origin of schedule

        convenient class to build date schedules
        a schedule includes always start and end date
        and rolls on roll, i.e. builds a sequence by
        adding and/or substracting step to/from roll.
        start and end slice the relevant dates.
        """
        roll = roll if roll else end
        start, end = list(map(BusinessDate, (start, end)))
        super(BusinessSchedule, self).__init__(start, end, step, roll)
        if start not in self:
            self.insert(0, start)
        if end not in self:
            self.append(end)

    def first_stub_long(self):
        """ adjusts the schedule to have a long stub at the beginning,
            i.e. first period is longer a regular step.
        """
        if len(self) > 2:
            self.pop(1)
        return self

    def last_stub_long(self):
        """ adjusts the schedule to have a long stub at the end,
            i.e. last period is longer a regular step.
        """
        if len(self) > 2:
            self.pop(-2)
        return self

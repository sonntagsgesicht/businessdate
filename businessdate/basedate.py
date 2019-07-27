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


from datetime import date, timedelta

from .ymd import from_excel_to_ymd, from_ymd_to_excel


class BaseDateFloat(float):
    """ native `float` backed base class for a performing date calculations counting days since Jan, 1st 1900 """

    def __new__(cls, x=0):
        new = super(BaseDateFloat, cls).__new__(cls, x)
        new._ymd = None
        return new

    # --- property methods ---------------------------------------------------

    @property
    def day(self):
        if not self._ymd:
            self._ymd = self.to_ymd()
        return self._ymd[2]

    @property
    def month(self):
        if not self._ymd:
            self._ymd = self.to_ymd()
        return self._ymd[1]

    @property
    def year(self):
        if not self._ymd:
            self._ymd = self.to_ymd()
        return self._ymd[0]

    def weekday(self):
        return self.to_date().weekday()

    # --- constructor method -------------------------------------------------

    @classmethod
    def from_ymd(cls, year, month, day):
        """ creates instance from a int tuple `(year, month, day)` """
        return cls(from_ymd_to_excel(year, month, day))

    @classmethod
    def from_date(cls, d):
        """ creates instance from a `datetime.date` object `d` """
        return cls.from_ymd(d.year, d.month, d.day)

    @classmethod
    def from_float(cls, x):
        """ creates from a float `x` counting the days since Jan, 1st 1900 """
        return cls(x)

    # --- cast method --------------------------------------------------------

    def to_ymd(self):
        """ returns the int tuple `(year, month, day)` """
        if not self._ymd:
            self._ymd = from_excel_to_ymd(int(self))
        return self._ymd

    def to_date(self):
        """ returns `datetime.date(year, month, day)` """
        if not self._ymd:
            self._ymd = self.to_ymd()
        return date(*self._ymd)

    def to_float(self):
        """ returns float counting the days since Jan, 1st 1900 """
        return int(self)

    # --- calculation methods ------------------------------------------------

    def _add_days(self, n):
        self._ymd = None
        return self.__class__(super(BaseDateFloat, self).__add__(n))

    def _diff_in_days(self, d):
        return super(BaseDateFloat, d).__sub__(float(self))


class BaseDateDatetimeDate(date):
    """ `datetime.date` backed base class for a performing date calculations """

    # --- constructor method -------------------------------------------------

    @classmethod
    def from_ymd(cls, year, month, day):
        """ creates instance from a int tuple `(year, month, day)` """
        return cls(year, month, day)

    @classmethod
    def from_date(cls, d):
        """ creates instance from a `datetime.date` object `d` """
        return cls.from_ymd(d.year, d.month, d.day)

    @classmethod
    def from_float(cls, x):
        """ creates from a float `x` counting the days since Jan, 1st 1900 """
        y, m, d = from_excel_to_ymd(x)
        return cls.from_ymd(y, m, d)

    # --- cast method --------------------------------------------------------

    def to_ymd(self):
        """ returns the int tuple `(year, month, day)` """
        return self.year, self.month, self.day

    def to_date(self):
        """ returns `datetime.date(year, month, day)` """
        return date(*self.to_ymd())

    def to_float(self):
        """ returns float counting the days since Jan, 1st 1900 """
        return from_ymd_to_excel(*self.to_ymd())

    # --- calculation methods ------------------------------------------------

    def _add_days(self, days_int):
        res = super(BaseDateDatetimeDate, self).__add__(timedelta(days_int))
        return self.__class__.from_ymd(res.year, res.month, res.day)

    def _diff_in_days(self, end):
        delta = super(BaseDateDatetimeDate, end).__sub__(self)
        return float(delta.days)

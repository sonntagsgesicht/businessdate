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

from ymd import from_excel_to_ymd, from_ymd_to_excel


class BaseDateFloat(float):

    # --- property methods ---------------------------------------------------
    @property
    def day(self):
        """
        day of date
        :return int:
        """
        return BaseDateFloat.to_ymd(self)[2]

    @property
    def month(self):
        """
        month of date
        :return int:
        """
        return BaseDateFloat.to_ymd(self)[1]

    @property
    def year(self):
        """
        year of date
        :return int:
        """
        return BaseDateFloat.to_ymd(self)[0]

    @property
    def baseclass(self):
        return BaseDateFloat.__name__

    # --- constructor method -------------------------------------------------
    @classmethod
    def from_ymd(cls, year, month, day):
        """
        creates date for year, month and day
        :param int year:
        :param int month:
        :param int day:
        :return BaseDate:
        """
        return cls(from_ymd_to_excel(year, month, day))

    @classmethod
    def from_date(cls, date_obj):
        """
        creates date from date object
        :param date date_obj:
        :return BaseDate:
        """
        return cls.from_ymd(date_obj.year, date_obj.month, date_obj.day)

    @classmethod
    def from_float(cls, xl_int):
        """
        creates date for Microsoft Excel integer date representation
        :param int xl_int:
        :return BaseDate:
        """
        return cls(xl_int)

    # --- cast method --------------------------------------------------------

    def to_ymd(self):
        return from_excel_to_ymd(int(self))

    def to_date(self):
        return date(*self.to_ymd())

    def to_float(self):
        return int(self)

    # --- calculation methods ------------------------------------------------

    def add_days(self, days_int):
        """
        adds number of days to a date

        :param int days_int: number of days to add
        :return BaseDate: resulting date
        """
        return self.__class__(super(BaseDateFloat, self).__add__(days_int))

    def diff_in_days(self, end):
        """
        returns distance of two dates as number of days
        :param BaseDateFloat end: end date
        :return float: difference between end date and start date in days
        """
        return super(BaseDateFloat, end).__sub__(float(self))


class BaseDateDatetimeDate(date):

    # --- property methods ---------------------------------------------------
    # day
    # month
    # year
    @property
    def baseclass(self):
        return BaseDateDatetimeDate.__name__

    # --- constructor method -------------------------------------------------
    @classmethod
    def from_ymd(cls, year, month, day):
        """
        creates date for year, month and day
        :param int year:
        :param int month:
        :param int day:
        :return BaseDate:
        """
        return cls(year, month, day)

    @classmethod
    def from_date(cls, date_obj):
        """
        creates date from date object
        :param date date_obj:
        :return BaseDate:
        """
        return cls.from_ymd(date_obj.year, date_obj.month, date_obj.day)

    @classmethod
    def from_float(cls, xl_int):
        y, m, d = from_excel_to_ymd(xl_int)
        return cls.from_ymd(y, m, d)

    # --- cast method --------------------------------------------------------

    def to_ymd(self):
        return self.year, self.month, self.day

    def to_date(self):
        return date(*self.to_ymd())

    def to_float(self):
        return from_ymd_to_excel(*self.to_ymd())

    # --- calculation methods ------------------------------------------------

    def add_days(self, days_int):
        """
        addition of a number of days

        :param int days_int:
        :return BaseDatetimeDate:
        """
        res = super(BaseDateDatetimeDate, self).__add__(timedelta(days_int))
        return self.__class__(res.year, res.month, res.day)

    def diff_in_days(self, end):
        """
        calculate difference between given dates in days

        :param BaseDateDatetimeDate end: end date
        :return float: difference between end date and start date in days
        """
        delta = super(BaseDateDatetimeDate, end).__sub__(self)
        return float(delta.days)


BaseDate = BaseDateDatetimeDate

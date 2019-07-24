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

from methods.ymd import is_valid_ymd, from_excel_to_ymd, from_ymd_to_excel


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
    @staticmethod
    def from_ymd(year, month, day):
        """
        creates date for year, month and day
        :param int year:
        :param int month:
        :param int day:
        :return BaseDate:
        """
        return BaseDate(from_ymd_to_excel(year, month, day))

    # --- cast method --------------------------------------------------------
    @staticmethod
    def to_ymd(d):
        """
        returns date represented as tuple `year, month, day`
        :param BaseDateFloat d:
        :return tuple(int, int, int):
        """
        return from_excel_to_ymd(d)

    # --- calculation methods ------------------------------------------------
    @staticmethod
    def add_days(d, days_int):
        """
        adds number of days to a date
        :param BaseDateFloat d: date to add days to
        :param int days_int: number of days to add
        :return BaseDate: resulting date
        """

        return BaseDateFloat(super(BaseDate, d).__add__(days_int))

    @staticmethod
    def diff_in_days(start, end):
        """
        returns distance of two dates as number of days
        :param BaseDateFloat start: start date
        :param BaseDateFloat end: end date
        :return float: difference between end date and start date in days
        """
        return super(BaseDateFloat, end).__sub__(start)


class BaseDateDatetimeDate(date):

    # --- property methods ---------------------------------------------------
    # day
    # month
    # year
    @property
    def baseclass(self):
        return BaseDateDatetimeDate.__name__

    # --- constructor method -------------------------------------------------
    @staticmethod
    def from_ymd(year, month, day):
        """
        converts date as `(year, month, day)` tuple into Microsoft Excel representation style

        :param int year:
        :param int month:
        :param int day:
        :return BaseDatetimeDate:
        """
        return BaseDateDatetimeDate(year, month, day)

    # --- cast method --------------------------------------------------------
    @staticmethod
    def to_ymd(d):
        """
        returns date represented as tuple `year, month, day`
        :param BaseDateDatetimeDate d:
        :return tuple(int, int, int):
        """
        # return d.timetuple()[:3]
        return d.year, d.month, d.day

    # --- calculation methods ------------------------------------------------
    @staticmethod
    def add_days(d, days_int):
        """
        addition of a number of days

        :param BaseDateDatetimeDate d:
        :param int days_int:
        :return BaseDatetimeDate:
        """
        # n = date(d.year, d.month, d.day) + timedelta(days_int)
        n = super(BaseDateDatetimeDate, d).__add__(timedelta(days_int))
        return BaseDateDatetimeDate(n.year, n.month, n.day)

    @staticmethod
    def diff_in_days(start, end):
        """
        calculate difference between given dates in days

        :param BaseDateDatetimeDate start: state date
        :param BaseDateDatetimeDate end: end date
        :return float: difference between end date and start date in days
        """
        # diff = date(end.year, end.month, end.day) - date(start.year, start.month, start.day)
        diff = super(BaseDateDatetimeDate, end).__sub__(start)
        return float(diff.days)


class BaseDateTuple(object):

    @staticmethod
    def _is_valid_args(args):

        valid = False
        if len(args) == 3:
            valid = True
            for arg in args:
                if not isinstance(arg, int): valid = False
            if valid:
                if not is_valid_ymd(args[0],args[1],args[2]):
                    valid = False


        if isinstance(args[0], BaseDateTuple):
            valid = True
        return valid

    def __new__(cls, *args):
        """

        :param args: should be three ints (year, month, day)
        """
        new = super(BaseDateTuple, cls).__new__(cls)
        if BaseDateTuple._is_valid_args(args):
            if isinstance(args[0], BaseDateTuple):
                new.date = args[0].date
            else:
                new.date = (args[0], args[1], args[2])
        else:
            msg = str(args) + " has not the correct format or does not stand for a valid year. BaseDateTuple(year, month, day)"
            raise ValueError(msg)
        return new

    @property
    def year(self):
        return self.date[0]

    @property
    def month(self):
        return self.date[1]

    @property
    def day(self):
        return self.date[2]

    @property
    def baseclass(self):
        return BaseDateTuple.__name__

    @staticmethod
    def from_ymd(year, month, day):
        return BaseDateTuple(year, month, day)

    @staticmethod
    def to_ymd(d):
        return d.date

    @staticmethod
    def add_days(date_obj, days_int):
        """
        addition of a number of days

        :param BaseDateTuple d:
        :param int days_int:
        :return BaseDatetimeDate:
        """
        n = from_ymd_to_excel(*date_obj.date) + days_int

        return BaseDateTuple(*from_excel_to_ymd(n))

    @staticmethod
    def diff_in_days(start, end):
        """
        calculate difference between given dates in days

        :param BaseDateTuple start: state date
        :param BaseDateTuple end: end date
        :return float: difference between end date and start date in days
        """

        diff = from_ymd_to_excel(*end.date)-from_ymd_to_excel(*start.date)
        return float(diff)

    def __lt__(self, other):
        return (self.year, self.month, self.day) < (other.year, other.month, other.day)

    def __le__(self, other):
        return (self.year, self.month, self.day) <= (other.year, other.month, other.day)

    def __ge__(self,other):
        return (self.year, self.month, self.day) > (other.year, other.month, other.day)

    def __gt__(self, other):
        return (self.year, self.month, self.day) >=(other.year, other.month, other.day)

    def __eq__(self, other):
        return (self.year, self.month, self.day) == (other.year, other.month, other.day)

    def __ne__(self, other):
        return (self.year, self.month, self.day) != (other.year, other.month, other.day)


BaseDate = BaseDateDatetimeDate

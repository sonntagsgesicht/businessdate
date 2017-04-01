# -*- coding: utf-8 -*-

#  businessdate
#  ------------
#  A fast, efficient Python library for generating business dates inherited
#  from float for fast date operations. Typical banking business methods
#  are provided like business holidays adjustment, day count fractions.
#  Beside dates generic business periods offer to create time periods like
#  '10Y', '3 Months' or '2b'. Periods can easily added to business dates.
#
#  Author:  pbrisk <pbrisk@icloud.com>
#  Copyright: 2016, 2017 Deutsche Postbank AG
#  Website: https://github.com/pbrisk/businessdate
#  License: APACHE Version 2 License (see LICENSE file)


from datetime import date, timedelta
from math import floor

#: float: basis for diff_in_years method
DAYS_IN_YEAR = 365.25

#: list(int): non-leap year number of days per month
_days_per_month = \
    [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

#: list(int): non-leap year cumulative number of days per month
_cum_month_days = \
    [0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334, 365]


def is_leap_year(year):
    """
    returns True for leap year and False otherwise

    :param int year: calendar year
    :return bool:
    """

    return (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0)


def days_in_year(year):
    """
        returns number of days in the given calendar year

        :param int year: calendar year
        :return int:
        """

    return 366 if is_leap_year(year) else 365


def days_in_month(year, month):
    """
    returns number of days for the given year and month

    :param int year: calendar year
    :param int month: calendar month
    :return int:
    """

    eom = _days_per_month[month - 1]
    if is_leap_year(year) and month == 2:
        eom += 1

    return eom


def is_valid_ymd(year, month, day):
    """
    return True if (year,month, day) can be represented in Excel-notation
    (number of days since 30.12.1899) for calendar days, otherwise False

    :param int year: calendar year
    :param int month: calendar month
    :param int day: calendar day
    :return bool:
    """

    return 1 <= month <= 12 and 1 <= day <= days_in_month(year, month) and year >= 1899


def from_excel_to_ymd(excel_int):
    """
    converts date in Microsoft Excel representation style and returns `(year, month, day)` tuple

    :param int excel_int: date as int (days since 1899-12-31)
    :return tuple(int, int, int):
    """

    int_date = int(floor(excel_int))
    int_date -= 1  # count from 31.12.1899 instead of from 30.12.1899
    year = (int_date - 1) // 365
    rest_days = int_date - 365 * year - (year + 3) // 4 + (year + 99) // 100 - (year + 299) // 400
    year += 1900

    while rest_days <= 0:
        year -= 1
        rest_days += days_in_year(year)

    month = 1
    if is_leap_year(year) and rest_days == 60:
        month = 2
        day = 29
    else:
        if is_leap_year(year) and rest_days > 60:
            rest_days -= 1

        while rest_days > _cum_month_days[month]:
            month += 1

        day = rest_days - _cum_month_days[month - 1]
    return year, month, day


def from_ymd_to_excel(year, month, day):
    """
    converts date as `(year, month, day)` tuple into Microsoft Excel representation style

    :param tuple(int, int, int): int tuple `year, month, day`
    :return int:
    """
    if not is_valid_ymd(year, month, day):
        raise ValueError("Invalid date {0}.{1}.{2}".format(year, month, day))

    days = _cum_month_days[month - 1] + day
    days += 1 if (is_leap_year(year) and month > 2) else 0

    years_distance = year - 1900
    days += years_distance * 365 + \
            (years_distance + 3) // 4 - (years_distance + 99) // 100 + (years_distance + 299) // 400

    # count days since 30.12.1899 (excluding 30.12.1899) (workaround for excel bug)
    days += 1
    return days


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
        """
        addition of a number of days

        :param BusinessDate d:
        :param int days_int:
        :return bankdate:
        """
        return BaseDate(super(BaseDate, d).__add__(days_int))

    @staticmethod
    def add_years(d, years_int):
        """
        adds number of years to a date
        :param BaseDateFloat d: date to add years to
        :param int years_int: number of years to add
        :return BaseDate: resulting date
        """
        """
        addition of a number of years

        :param BusinessDate d:
        :param int years_int:
        :return bankdate:
        """
        y, m, d = BaseDate.to_ymd(d)
        if not is_leap_year(years_int) and m == 2:
            d = min(28, d)
        return BaseDate.from_ymd(y + years_int, m, d)

    @staticmethod
    def diff_in_days(start, end):
        """
        returns distance of two dates as number of days
        :param BaseDateFloat start: start date
        :param BaseDateFloat end: end date
        :return float: difference between end date and start date in days
        """
        return super(BaseDateFloat, end).__sub__(start)

    @staticmethod
    def diff_in_years(start, end):
        """
        calculate difference between given dates in years. The difference corresponds to Act/365.25 year fraction

        :param BaseDateFloat start: state date
        :param BaseDateFloat end: end date
        :return float: difference between end date and start date in years
        """
        return BaseDateFloat.diff_in_days(start, end) / DAYS_IN_YEAR


class BaseDatetimeDate(date):
    # --- property methods ---------------------------------------------------
    # day
    # month
    # year

    # --- constructor method -------------------------------------------------
    @staticmethod
    def from_ymd(year, month, day):
        """
        converts date as `(year, month, day)` tuple into Microsoft Excel representation style

        :param tuple(int, int, int): int tuple `year, month, day`
        :return BaseDatetimeDate:
        """
        return BaseDatetimeDate(year, month, day)

    # --- cast method --------------------------------------------------------
    @staticmethod
    def to_ymd(d):
        """
        returns date represented as tuple `year, month, day`
        :param BaseDatetimeDate d:
        :return tuple(int, int, int):
        """

        return d.year, d.month, d.day

    # --- calculation methods ------------------------------------------------
    @staticmethod
    def add_days(d, days_int):
        """
        addition of a number of days

        :param BaseDatetimeDate d:
        :param int days_int:
        :return BaseDatetimeDate:
        """
        n = date(d.year, d.month, d.day) + timedelta(days_int)
        return BaseDatetimeDate(n.year, n.month, n.day)

    @staticmethod
    def add_years(d, years_int):
        """
        addition of a number of years

        :param BaseDatetimeDate d:
        :param int years_int:
        :return BaseDatetimeDate:
        """
        y, m, d = BaseDatetimeDate.to_ymd(d)
        y += years_int
        if not is_leap_year(y) and m == 2:
            d = min(28, d)
        return BaseDatetimeDate.from_ymd(y, m, d)

    @staticmethod
    def diff_in_days(start, end):
        """
        calculate difference between given dates in days

        :param BaseDatetimeDate start: state date
        :param BaseDatetimeDate end: end date
        :return float: difference between end date and start date in days
        """
        diff = date(end.year, end.month, end.day) - date(start.year, start.month, start.day)
        return float(diff.days)

    @staticmethod
    def diff_in_years(start, end):
        """
        calculate difference between given dates in years. The difference corresponds to Act/365.25 year fraction

        :param BaseDatetimeDate start: state date
        :param BaseDatetimeDate end: end date
        :return float: difference between end date and start date in years
        """
        return BaseDatetimeDate.diff_in_days(start, end) / DAYS_IN_YEAR


class BaseDate(BaseDateFloat):
    """
    base class for BusinessDate
    """
    pass

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


# --- year,month,day based calculation methods -----------------------------------------

from math import floor

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


def end_of_quarter_month(month):
    """
    method to return last month of quarter

    :param int month:
    :return: int
    """
    while month % 3:
        month += 1
    return month


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
    int_date -= 1 if excel_int > 60 else 0
    # jd: There are two errors in excels own date <> int conversion.
    # The first is that there exists the 00.01.1900 and the second that there never happened to be a 29.2.1900 since it
    # was no leap year. So there is the int 60 <> 29.2.1900 which has to be jumped over.

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
    converts date as `year, month, day` tuple into Microsoft Excel representation style

    :param int year:
    :param int month:
    :param int day:
    :return int:
    """
    if not is_valid_ymd(year, month, day):
        raise ValueError("Invalid date {0}.{1}.{2}".format(year, month, day))

    days = _cum_month_days[month - 1] + day
    days += 1 if (is_leap_year(year) and month > 2) else 0

    years_distance = year - 1900
    days += \
        years_distance * 365 + (years_distance + 3) // 4 - (years_distance + 99) // 100 + (years_distance + 299) // 400

    # count days since 30.12.1899 (excluding 30.12.1899) (workaround for excel bug)
    days += 1 if (year, month, day) > (1900, 2, 28) else 0
    return days

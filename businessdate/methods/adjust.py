# -*- coding: utf-8 -*-

# --- business day adjustment methods ------------------------------------

from calendar import WEDNESDAY, FRIDAY
from datetime import date, timedelta
from ymd import days_in_month, end_of_quarter_month

# timedelta: one day timedelta
ONE_DAY = timedelta(1)


def is_business_day(business_date, holidays=list()):
    """
    method to check if a date falls neither on weekend nor is holiday

    :param date business_date : date to adjust
    :param list holidays : duck typing `in` for list of dates defining business holidays
    :return: bool
    """
    if business_date.weekday() > FRIDAY:
        return False
    return business_date not in holidays


def adjust_no(business_date, holidays=None):
    """
    no adjusts to Business Day Convention.

    :param date business_date : date to adjust
    :param list holidays : duck typing `in` for list of dates defining business holidays
    :return: date
    """
    return business_date


def adjust_previous(business_date, holidays=None):
    """
    adjusts to Business Day Convention "Preceding" (4.12(a) (iii) 2006 ISDA Definitions).

    :param date business_date : date to adjust
    :param list holidays : duck typing `in` for list of dates defining business holidays
    :return: date
    """
    while not is_business_day(business_date, holidays):
        business_date -= ONE_DAY
    return business_date


def adjust_follow(business_date, holidays=None):
    """
    adjusts to Business Day Convention "Following" (4.12(a) (i) 2006 ISDA Definitions).

    :param date business_date : date to adjust
    :param list holidays : duck typing `in` for list of dates defining business holidays
    :return: date
    """
    while not is_business_day(business_date, holidays):
        business_date += ONE_DAY
    return business_date


def adjust_mod_follow(business_date, holidays=None):
    """
    adjusts to Business Day Convention "Modified [Following]" (4.12(a) (ii) 2006 ISDA Definitions).

    :param date business_date : date to adjust
    :param list holidays : duck typing `in` for list of dates defining business holidays
    :return: date
    """
    month = business_date.month
    new = adjust_follow(business_date, holidays)
    if month != new.month:
        new = adjust_previous(business_date, holidays)
    business_date = new
    return business_date


def adjust_mod_previous(business_date, holidays=None):
    """
    adjusts to Business Day Convention "Modified Preceding" (not in 2006 ISDA Definitons).

    :param date business_date : date to adjust
    :param list holidays : duck typing `in` for list of dates defining business holidays
    :return: date
    """
    month = business_date.month
    new = adjust_previous(business_date, holidays)
    if month != new.month:
        new = adjust_follow(business_date, holidays)
    business_date = new
    return business_date


def adjust_start_of_month(business_date, holidays=None):
    """
    adjusts to Business Day Convention "Start of month".

    :param date business_date : date to adjust
    :param list holidays : duck typing `in` for list of dates defining business holidays
    :return: date
    """
    business_date = date(business_date.year, business_date.month, 1)
    business_date = adjust_follow(business_date, holidays)
    return business_date


def adjust_end_of_month(business_date, holidays=None):
    """
    adjusts to Business Day Convention "End of month".

    :param date business_date : date to adjust
    :param list holidays : duck typing `in` for list of dates defining business holidays
    :return: date
    """
    y, m, d = business_date.year, business_date.month, business_date.day
    business_date = date(y, m, days_in_month(y, m))
    business_date = adjust_previous(business_date, holidays)
    return business_date


def adjust_imm(business_date, holidays=None):
    """
    adjusts to Business Day Convention "International Monetary Market".

    :param date business_date : date to adjust
    :param list holidays : duck typing `in` for list of dates defining business holidays
    :return: date
    """
    business_date = date(business_date.year, end_of_quarter_month(business_date.month), 15)
    while business_date.weekday() == WEDNESDAY:
        business_date += ONE_DAY
    return business_date


def adjust_cds_imm(business_date, holidays=None):
    """
    adjusts to Business Day Convention "Single Name CDS" (not in 2006 ISDA Definitions).

    :param date business_date : date to adjust
    :param list holidays : duck typing `in` for list of dates defining business holidays
    :return: date
    """
    business_date = date(business_date.year, end_of_quarter_month(business_date.month), 20)
    return business_date

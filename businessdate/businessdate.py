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


from calendar import monthrange, weekday, WEDNESDAY, FRIDAY
from copy import copy
from datetime import date, datetime, timedelta

from basedate import BaseDate, BaseDateFloat, BaseDateTuple, BaseDateDatetimeDate, \
    is_leap_year, is_valid_ymd, days_in_year, days_in_month, \
    from_ymd_to_excel, from_excel_to_ymd
from baseperiod import BasePeriod

#: base date
BASE_DATE = '20151231' # date.today()  # BusinessDate() initializes with date of today
#: string: basic date format as string
DATE_FORMAT = '%Y%m%d'


class BusinessHolidays(list):
    """
    holiday calendar class
    """

    def __init__(self, iterable=None):
        """
        :param iterable iterable: sequence of holiday dates

        """
        if iterable:
            super(BusinessHolidays, self).__init__(BusinessDate(iterable))
        else:
            super(BusinessHolidays, self).__init__()

    def __contains__(self, item):
        if super(BusinessHolidays, self).__contains__(item):
            return True
        target_days_in_year = target_days(item.year)
        self.extend(target_days_in_year.keys())
        if item in target_days_in_year:
            return True
        else:
            return False


#: list: list of dates of default holiday calendar
DEFAULT_HOLIDAYS = BusinessHolidays()


class BusinessDate(BaseDate):

    def __new__(cls, date_value=None):
        r"""
        fundamental date class

        :param date_value: input value to create BusinessDate instance
        :type date_value: int, float, string or datetime.date
        :return: BusinessDate

        creates new BusinessDate either from `int`, `float`, `string`, `datetime.date`
        therefore the following will create the same

        .. code-block:: python

            BusinessDate(datetime.date(2015, 12, 31))
            BusinessDate(20151231)
            BusinessDate(2015-12-31)
            BusinessDate(31.12.2015)
            BusinessDate(12/31/2015)
            BusinessDate(42369)
            BusinessDate(42369.0)
            BusinessDate(735963)
            BusinessDate(735963.0)
            BusinessDate()

        **caution:** recommended is the use of class methods BusinessDate.from_string, from_date etc.

        """

        if date_value is None:
            new_date = BusinessDate(BASE_DATE)
        elif isinstance(date_value, BaseDateFloat):
            return super(BusinessDate, cls).__new__(cls, float(date_value))
        elif isinstance(date_value, (BaseDateDatetimeDate, BaseDateTuple)):
            return super(BusinessDate, cls).__new__(cls, date_value.year, date_value.month, date_value.day)
        elif isinstance(date_value, (int, float)):
            if date_value >= 18990101:
                new_date = BusinessDate.from_string(str(date_value))
            elif 1 < date_value < 200 * 365.25:
                new_date = BusinessDate.from_excel(date_value)
            else:
                new_date = BusinessDate.from_ordinal(date_value)
        elif isinstance(date_value, str):
            new_date = BusinessDate.from_string(date_value)
        elif isinstance(date_value, (date, datetime)):
            new_date = BusinessDate.from_date(date_value)
        elif isinstance(date_value, list):
            new_date = [BusinessDate(d) for d in date_value]
        else:
            raise ValueError("Can't build BusinessDate form %s type" % str(type(date_value)))

        return new_date

    def __copy__(self):

        return BusinessDate(date(*self.to_ymd()))

    def __deepcopy__(self, memodict={}):

        return BusinessDate(date(*self.to_ymd()))

    # --- operator methods ---------------------------------------------------
    def __add__(self, other):
        """
            addition of BusinessDate.

        :param BusinessDate or BusinessPeriod or str other: can be BusinessPeriod or
        any thing that might be casted to it.
        """
        if isinstance(other, BusinessPeriod):
            return self.add_period(other)
        elif BusinessPeriod.is_businessperiod(other):
            return self + BusinessPeriod(other)
        else:
            raise TypeError('addition of BusinessDates cannot handle objects of type %s.' % type(other))

    def __sub__(self, other):
        """
            subtraction of BusinessDate.

        :param object other: can be other BusinessDate, BusinessPeriod or any thing that might be casted to those.
        """
        if isinstance(other, BusinessDate):
            y, m, d = self.diff(other)
            return BusinessPeriod(years=y, months=m, days=d)
        elif isinstance(other, BusinessPeriod):
            return self.add_period(-1 * other)
        elif BusinessDate.is_businessdate(other):
            return self - BusinessDate(other)
        elif BusinessPeriod.is_businessperiod(other):
            return self - BusinessPeriod(other)
        else:
            raise TypeError('subtraction of BusinessDates cannot handle objects of type %s.' % type(other))

    def __str__(self):
        # return self.__class__.__name__ + '(' + self.to_string() + ')'
        return self.to_string()

    def __repr__(self):
        return self.to_string()

    # --- constructor methods ------------------------------------------------
    @staticmethod
    def from_ymd(y, m, d):
        # return super(BusinessDate, cls).__new__(BaseDate.from_ymd(y, m, d))

        return BusinessDate(BaseDate.from_ymd(y, m, d))

    @staticmethod
    def from_businessdate(d):
        """
        copy constructor

        :param BusinessDate d:
        :return bankdate:
        """

        return copy(d)

    @staticmethod
    def from_excel(excel_int):
        y, m, d = from_excel_to_ymd(excel_int)
        return BusinessDate.from_ymd(y, m, d)

    @staticmethod
    def from_date(datetime_date):
        """
        construct BusinessDate instance from datetime.date instance,
        raise ValueError exception if not possible

        :param datetime.date datetime_date: calendar day
        :return bool:
        """
        return BusinessDate.from_ymd(datetime_date.year, datetime_date.month, datetime_date.day)

    @staticmethod
    def from_ordinal(ordinal_int):
        d = date.fromordinal(int(ordinal_int))
        return BusinessDate.from_ymd(d.year, d.month, d.day)

    @staticmethod
    def from_string(date_str):
        """
        construction from the following string patterns
        '%Y-%m-%d'
        '%d.%m.%Y'
        '%m/%d/%Y'
        '%Y%m%d'

        :param str date_str:
        :return BusinessDate:
        """
        if date_str.count('-'):
            str_format = '%Y-%m-%d'
        elif date_str.count('.'):
            str_format = '%d.%m.%Y'
        elif date_str.count('/'):
            str_format = '%m/%d/%Y'
        elif len(date_str) == 8:
            str_format = '%Y%m%d'
        elif len(date_str) == 4:
            year = ord(date_str[0]) * 256 + ord(date_str[1])
            month = ord(date_str[2])
            day = ord(date_str[3])
            return BusinessDate.from_ymd(year, month, day)
        else:
            msg = "the date string " + date_str + " has not the right format"
            raise ValueError(msg)

        d = datetime.strptime(date_str, str_format)

        return BusinessDate.from_ymd(d.year, d.month, d.day)

    # --- cast methods -------------------------------------------------------
    def __float__(self):
        return float(self.to_excel())

    def __int__(self):
        return int(self.to_excel())

    def to_businessdate(self, origin_date=None):
        return self

    def to_businessperiod(self, origin_date=None):
        if origin_date is None:
            origin_date = BusinessDate()
        y, m, d = BusinessDate.diff(origin_date, self)
        return BusinessPeriod(years=y, months=m, days=d)

    def to_excel(self):
        y, m, d = self.to_ymd()
        return from_ymd_to_excel(y, m, d)

    def to_ymd(self):
        return super(BusinessDate, self).to_ymd(self)

    def to_date(self):
        """
        construct datetime.date instance represented calendar date of BusinessDate instance

        :return datetime.date:
        """
        y, m, d = self.to_ymd()
        return date(y, m, d)

    def to_ordinal(self):
        return self.to_date().toordinal()

    def to_string(self):
        """
        return BusinessDate as 'date.strftime(DATE_FORMAT)'

        :return string:
        """

        return self.to_date().strftime(DATE_FORMAT)

    # --- inherited validation and validation methods ------------------------
    @staticmethod
    def is_leap_year(year):
        """
        returns True for leap year and False otherwise

        :param int year: calendar year
        :return bool:
        """

        return is_leap_year(year)

    @staticmethod
    def days_in_year(year):
        """
        returns number of days in the given calendar year

        :param int year: calendar year
        :return int:
        """

        return days_in_year(year)

    @staticmethod
    def days_in_month(year, month):
        """
        returns number of days for the given year and month

        :param int year: calendar year
        :param int month: calendar month
        :return int:
        """

        return days_in_month(year, month)

    # --- own validation and information methods -----------------------------

    @staticmethod
    def is_businessdate(in_date):
        """
        checks whether the provided date is a date
        :param BusinessDate, int or float in_date:
        :return bool:
        """
        # Note: if the data range has been created from pace_xl, then all the dates are bank dates
        # and here it remains to check the validity.
        # !!! However, if the data has been read from json string via json.load() function
        # it does not recognize that this numbers are bankdates, just considers them as integers
        # therefore, additional check is useful here, first to convert the date if it is integer to BusinessDate,
        # then check the validity.
        # (as the parameter to this method should always be a BusinessDate)
        if not isinstance(in_date, BaseDate):
            try:  # to be removed
                in_date = BusinessDate(in_date)
            except:
                return False
        y, m, d, = in_date.to_ymd()
        return is_valid_ymd(y, m, d)

    @staticmethod
    def end_of_month(year, month):
        return BusinessDate.from_date(date(year, month, BusinessDate.days_in_month(year, month)))

    @staticmethod
    def end_of_quarter(year, month):
        while not month % 3:
            month += 1
        return BusinessDate.end_of_month(year, month)

    def is_business_day(self, holiday_obj=None):
        """
        :param list holiday_obj : datetime.date list defining business holidays
        :return: bool

        method to check if a date falls neither on weekend nor is holiday
        """
        if holiday_obj is None:
            holiday_obj = DEFAULT_HOLIDAYS

        y, m, d = BusinessDate.to_ymd(self)
        if weekday(y, m, d) > FRIDAY:
            return False
        elif self in holiday_obj:
            return False
        elif date(y, m, d) in holiday_obj:
            return False
        else:
            return True

    # --- inherited calculation methods --------------------------------------
    def add_days(self, days):
        return BusinessDate(BaseDate.add_days(self, days))

    def add_years(self, years):
        return BusinessDate(BaseDate.add_years(self, years))

    def diff_in_days(self, end_bd):
        return BaseDate.diff_in_days(self, end_bd)

    def diff_in_years(self, end_bd):
        return BaseDate.diff_in_years(self, end_bd)

    # --- own calculation methods --------------------------------------------
    def add_period(self, p, holiday_obj=None):
        """
        addition of a period object

        :param BusinessDate d:
        :param p:
        :type p: BusinessPeriod or str
        :param list holiday_obj:
        :return bankdate:
        """

        if isinstance(p, (list, tuple)):
            return [BusinessDate.add_period(self, pd) for pd in p]
        elif isinstance(p, str):
            period = BusinessPeriod(p)
        else:
            period = p

        res = BusinessDate.add_years(self, period.years)
        res = BusinessDate.add_months(res, period.months)
        res = BusinessDate.add_days(res, period.days)

        if period.businessdays:
            if holiday_obj:
                res = BusinessDate.add_business_days(res, period.businessdays, holiday_obj)
            else:
                res = BusinessDate.add_business_days(res, period.businessdays, period.holiday)

        return res

    def add_months(self, month_int):
        """
        addition of a number of months

        :param BusinessDate d:
        :param int month_int:
        :return bankdate:
        """

        month_int += self.month
        while month_int > 12:
            self = BusinessDate.add_years(self, 1)
            month_int -= 12
        while month_int < 1:
            self = BusinessDate.add_years(self, -1)
            month_int += 12
        l = monthrange(self.year, month_int)[1]
        return BusinessDate.from_ymd(self.year, month_int, min(l, self.day))

    def add_business_days(self, days_int, holiday_obj=None):
        """
        private method for the addition of business days, used in the addition of a BusinessPeriod only

        :param BusinessDate d:
        :param int days_int:
        :param list holiday_obj:
        :return: BusinessDate
        """

        res = self
        if days_int >= 0:
            count = 0
            while count < days_int:
                res = BusinessDate.add_days(res, 1)
                if BusinessDate.is_business_day(res, holiday_obj):
                    count += 1
        else:
            count = 0
            while count > days_int:
                res = BusinessDate.add_days(res, -1)
                if BusinessDate.is_business_day(res, holiday_obj):
                    count -= 1

        return res

    def diff(self, end_date):
        """
        difference expressed as a tuple of years, months, days
        (see also the python lib dateutils.relativedelta)

        :param BusinessDate start_date:
        :param BusinessDate end_date:
        :return (int, int, int):
        """

        if end_date < self:
            y, m, d = BusinessDate.diff(end_date, self)
            return -y, -m, -d
        y = end_date.year - self.year
        m = end_date.month - self.month

        while m < 0:
            y -= 1
            m += 12
        while m > 12:
            y += 1
            m -= 12

        s = BusinessDate.add_years(BusinessDate.add_months(self, m), y)
        d = BusinessDate.diff_in_days(s, end_date)

        if d < 0:
            m -= 1
            if m < 0:
                y -= 1
                m += 12
            s = BusinessDate.add_years(BusinessDate.add_months(self, m), y)

        d = BusinessDate.diff_in_days(s, end_date)

        return int(y), int(m), int(d)

    # --- day count fraction methods -----------------------------------------


    # List of day count conventions
    # 30/360 (4.16(f) 2006 ISDA Definitions) [other names: 360/360]
    # Act/365.25 (not in ISDA Definitions)
    # Act/365 (4.16(d) 2006 ISDA Definitions) [other names: actual/365 (Fixed), act/365 (Fixed), A/365 (Fixed), A/365F
    # Act/360 (4.16(e) 2006 ISDA Definitions) [other names: actual/360, A/360
    # Act/ACT (4.16(b) 2006 ISDA Definitions) [other names: actual/actual [(ISDA)], act/act (ISDA)]
    # 30E/360 (4.16(g) 2006 ISDA Definitions) [other names: Eurobond Basis]

    def get_30_360(self, end):
        """
            implements 30/360 Day Count Convention (4.16(f) 2006 ISDA Definitions)
        """
        start_day = min(self.day, 30)
        end_day = 30 if (start_day == 30 and end.day == 31) else end.day
        return (360 * (end.year - self.year) + 30 * (end.month - self.month) + (end_day - start_day)) / 360.0

    def get_act_36525(self, end):
        """
            implements Act/365.25 Day Count Convention
        """
        return BusinessDate.diff_in_days(self, end) / 365.25

    def get_act_365(self, end):
        """
            implements Act/365 day count convention (4.16(d) 2006 ISDA Definitions)
        """
        return BusinessDate.diff_in_days(self, end) / 365.0

    def get_act_360(self, end):
        """
            implements Act/360 day count convention (4.16(e) 2006 ISDA Definitions)
        """
        return BusinessDate.diff_in_days(self, end) / 360.0

    def get_act_act(self, end):
        """
            implements Act/Act day count convention (4.16(b) 2006 ISDA Definitions)
        """
        # split end-self in year portions

        # if the period does not lie within a year split the days in the period as following:
        #           restdays of start year / years in between / days in the end year
        # REMARK: following the affore mentioned ISDA Definition the first day of the period is included whereas the
        # last day will be excluded
        # What remains to check now is only whether the start and end year are leap or non-leap years. The quotients
        # can be easily calculated and for the years in between they are always one (365/365 = 1; 366/366 = 1)

        if end.year - self.year == 0:
            if BusinessDate.is_leap_year(self.year):
                return BusinessDate.diff_in_days(self, end) / 366.0     # leap year: 366 days
            else:
               # return BusinessDate.diff_in_days(self, end) / 366.0
                return BusinessDate.diff_in_days(self, end) / 365.0     # non-leap year: 365 days
        else:
            rest_year1 = BusinessDate.diff_in_days(self, BusinessDate(
                date(self.year, 12, 31))) + 1  # since the first day counts

            rest_year2 = abs(BusinessDate.diff_in_days(end, BusinessDate(
                date(end.year, 1, 1))))                         # here the last day is automatically not counted

            years_in_between = end.year - self.year - 1

            return years_in_between + rest_year1/(366.0 if is_leap_year(self.year) else 365.0) + rest_year2/(366.0 if is_leap_year(end.year) else 365.0)


        #elif end.year - self.year == 1:
        #   if BusinessDate.is_leap_year(self.year):
        #       return BusinessDate.diff_in_days(self, BusinessDate.from_date(date(self.year, 12, 31))) / 366.0 + \
        #              BusinessDate.diff_in_days(BusinessDate.from_date(date(self.year, 12, 31)), end) / 365.0
        #   elif BusinessDate.is_leap_year(end.year):
        #       return BusinessDate.diff_in_days(self, BusinessDate.from_date(date(self.year, 12, 31))) / 365.0 + \
        #              BusinessDate.diff_in_days(BusinessDate.from_date(date(self.year, 12, 31)), end) / 366.0
        #   else:
        #       return BusinessDate.diff_in_days(self, end) / 365.0
        #else:
          #  raise NotImplementedError('Act/Act day count not implemented for periods spanning three years or more.')

    def get_30E_360(self, end):
        """
        implements the 30E/360 Day Count Convention (4.16(g) 2006 ISDA Definitons)
        """

        y1, m1, d1 = self.to_ymd()
        #adjust to date immediately following the the last day
        y2, m2, d2 = end.add_days(0).to_ymd()

        d1 = min(d1, 30)
        d2 = min(d2, 30)

        return (360*(y2-y1)+30*(m2-m1)+(d2-d1))/360.0

    def get_30E_360_ISDA(self, end):
        """
        implements the 30E/360 (ISDA) Day Count Convention (4.16(h) 2006 ISDA Definitions)
        :param end:
        :return:
        """
        y1, m1, d1 = self.to_ymd()
        #ajdust to date immediately following the last day
        y2, m2, d2 = end.add_days(0).to_ymd()

        if (m1 == 2 and d1 >= 28) or d1 == 31:
            d1 = 30
        if (m2 == 2 and d2 >= 28) or d2 == 31:
            d2 = 30

        return (360*(y2-y1)+30*(m2-m1)+(d2-d1))/360.0


    # --- business day adjustment methods ------------------------------------

    def adjust_previous(self, holidays_obj=None):
        """
        adjusts to Business Day Convention "Preceding" (4.12(a) (iii) 2006 ISDA Definitions).
        """
        while not BusinessDate.is_business_day(self, holidays_obj):
            self = BusinessDate.add_days(self, -1)
        return self

    def adjust_follow(self, holidays_obj=None):
        """
        adjusts to Business Day Convention "Following" (4.12(a) (i) 2006 ISDA Definitions).
        """
        while not BusinessDate.is_business_day(self, holidays_obj):
            self = BusinessDate.add_days(self, 1)
        return self

    def adjust_mod_follow(self, holidays_obj=None):
        """
        adjusts to Business Day Convention "Modified [Following]" (4.12(a) (ii) 2006 ISDA Definitions).
        """
        month = self.month
        new = BusinessDate.adjust_follow(self, holidays_obj)
        if month != new.month:
            new = BusinessDate.adjust_previous(self, holidays_obj)
        self = new
        return self

    def adjust_mod_previous(self, holidays_obj=None):
        """
        ajusts to Business Day Convention "Modified Preceding" (not in 2006 ISDA Definitons).
        """
        month = self.month
        new = BusinessDate.adjust_previous(self, holidays_obj)
        if month != new.month:
            new = BusinessDate.adjust_follow(self, holidays_obj)
        self = new
        return self

    def adjust_start_of_month(self, holidays_obj=None):
        self = BusinessDate.from_date(date(self.year, self.month, 1))
        self = self.adjust_follow(holidays_obj)
        return self

    def adjust_end_of_month(self, holidays_obj=None):
        self = BusinessDate.end_of_month(self.year, self.month)
        self = self.adjust_previous(holidays_obj)
        return self

    def adjust_imm(self, holidays_obj=None):
        self = BusinessDate.end_of_quarter(self.year, self.month)
        self = BusinessDate.from_date(date(self.year, self.month, 15))
        while weekday(self.year, self.month, self.day) == WEDNESDAY:
            BusinessDate.add_days(self, 1)
        return self

    def adjust_cds_imm(self, holidays_obj=None):
        eoq = BusinessDate.end_of_quarter(self.year, self.month)
        self = BusinessDate.from_date(date(eoq.year, eoq.month, 20))
        return self


class BusinessPeriod(BasePeriod):

    def __new__(cls, *args, **kwargs):
        new = super(BusinessPeriod, cls).__new__(cls)
        return new

    def __init__(self, period_in='', holiday=None, years=0, months=0, days=0, businessdays=0):
        """
        class managing date periods like days, weeks, years etc.

        :param period_in:
        :param holiday:
        :param years:
        :param months:
        :param days:
        :param businessdays:

        representation of a time BusinessPeriod, similar to dateutils.relativedelta, but with additional business day logic
        """

        super(BusinessPeriod, self).__init__()
        if isinstance(period_in, BusinessPeriod):
            years = period_in.years
            months = period_in.months
            days = period_in.days
            businessdays = period_in.businessdays
        elif isinstance(period_in, timedelta):
            days += timedelta.days
        elif isinstance(period_in, (list, tuple)):
            if len(period_in) == 2:
                y, m, d = BusinessDate.diff(period_in[0], period_in[1])
                years += y
                months += m
                days += d
        elif isinstance(period_in, str):
            if period_in.startswith('-'):
                p = BusinessPeriod(period_in[1:])
                years -= p.years
                months -= p.months
                days -= p.days
                businessdays -= p.businessdays
            elif period_in.upper() == 'ON':
                businessdays += 1
            elif period_in.upper() == 'TN':
                businessdays += 2
            elif period_in.upper() == 'DD':
                businessdays += 3
            elif period_in.upper().find('B') > 0:
                businessdays += int(period_in.upper().split('B', 2)[0])
            else:
                y, m, d = BusinessPeriod.parse(period_in)
                years += y
                months += m
                days += d
        if holiday is None:
            self.holiday = DEFAULT_HOLIDAYS
        else:
            self.holiday = holiday
        self.years = years
        self.months = months
        self.days = days
        self.businessdays = businessdays

    # --- constructor methods ------------------------------------------------
    @classmethod
    def from_string(cls, period_in):
        return BusinessPeriod(period_in)

    # --- validation and information methods ---------------------------------
    @classmethod
    def parse(cls, period_str):
        p = period_str.upper()
        Y, Q, M, W, D = '00000'
        if p.find('Y') > 0:
            [Y, p] = p.split('Y', 2)
        if p.find('Q') > 0:
            [Q, p] = p.split('Q', 2)
        if p.find('M') > 0:
            [M, p] = p.split('M', 2)
        if p.find('W') > 0:
            [W, p] = p.split('W', 2)
        if p.find('D') > 0:
            [D, p] = p.split('D', 2)
        assert Y.isdigit() and Q.isdigit() and M.isdigit() and W.isdigit() and D.isdigit()
        y = int(Y)
        m = int(Q) * 3 + int(M)
        d = int(W) * 7 + int(D)
        return (y, m, d)

    @classmethod
    def is_businessperiod(cls, in_period):
        """
        :param in_period: object to be checked
        :type in_period: object, str, timedelta
        :return: True if cast works
        :rtype: Boolean

        checks is argument con becasted to BusinessPeriod
        """
        try:  # to be removed
            if in_period.upper() == '0D':
                return True
            else:
                p = BusinessPeriod(str(in_period))
                return not (p.days == 0 and p.months == 0 and p.years == 0 and p.businessdays == 0)
        except:
            return False

    # --- property methods ---------------------------------------------------

    # --- operator methods ---------------------------------------------------
    def __repr__(self):
        return self.to_string()

    def __str__(self):
        #        return self.__class__.__name__ + '(' + self.to_string() + ')'
        return self.to_string()

    def __abs__(self):
        self.years = abs(self.years)
        self.months = abs(self.months)
        self.days = abs(self.days)
        self.businessdays = abs(self.businessdays)

    def __cmp__(self, other):
        assert type(self) == type(other), "types don't match %s" % str((type(self), type(other)))
        d = BusinessDate()
        return BusinessDate.diff_in_days(BusinessDate.add_period(d, self), BusinessDate.add_period(d, other))

    def __eq__(self, other):
        if isinstance(other, type(self)):
            return 0.0 == self.__cmp__(other)
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __nonzero__(self):
        return True if self.years or self.months or self.days or self.businessdays else False

    def __add__(self, other):
        if isinstance(other, (list, tuple)):
            return [self.__add__(o) for o in other]
        elif isinstance(other, BusinessPeriod):
            return BusinessPeriod(self).add_businessperiod(other)
        elif BusinessPeriod.is_businessperiod(other):
            return self + BusinessPeriod(other)
        else:
            raise TypeError

    def __sub__(self, other):
        per = self.__rsub__(other)
        return BusinessPeriod(years=-per.years, months=-per.months, days=-per.days, businessdays=-per.businessdays)

    def __rsub__(self, other):
        if isinstance(other, (list, tuple)):
            return [self.__rsub__(o) for o in other]
        elif BusinessPeriod.is_businessperiod(other):
            p = BusinessPeriod(other)
            y = self.years + p.years
            m = self.months + p.months
            d = self.days + p.days
            b = self.businessdays + p.businessdays
            other = BusinessPeriod(years=y, months=m, days=d, businessdays=b)
        else:
            raise TypeError
        return other

    def __mul__(self, other):
        if isinstance(other, (list, tuple)):
            return [self.__mul__(o) for o in other]
        if not isinstance(other, (int, long)):
            pass
        assert isinstance(other, (int, long)), "expected int or long but got %s" % str(type(other))
        y = self.years * other
        m = self.months * other
        d = self.days * other
        b = self.businessdays * other
        return BusinessPeriod(years=y, months=m, days=d, businessdays=b)

    def __rmul__(self, other):
        return self.__mul__(other)

    # --- calculation methods ------------------------------------------------
    def add_years(self, years_int):
        self.years += years_int
        return self

    def add_months(self, months_int):
        self.months += months_int
        return self

    def add_days(self, days_int):
        self.days += days_int
        return self

    def add_businessdays(self, days_int):
        self.businessdays += days_int
        return self

    def add_businessperiod(self, p):
        self.years += p.years
        self.months += p.months
        self.days += p.days
        self.businessdays += p.businessdays
        return self

    # --- cast methods -------------------------------------------------------
    def to_date(self, start_date=None):
        return self.to_businessdate(start_date).to_date()

    def to_datetime(self, start_date=None):
        return self.to_bankdate(start_date).to_datetime()

    def to_businessdate(self, start_date=None):
        if start_date:
            return BusinessDate.add_period(start_date, self)
        else:
            return BusinessDate.add_period(BusinessDate(), self)

    def to_businessperiod(self, start_date=None):
        return self

    def to_string(self):
        period_str = ''
        if self.years:
            period_str += str(self.years) + 'Y'
        if self.months:
            period_str += str(self.months) + 'M'
        if self.days:
            period_str += str(self.days) + 'D'
        if self.businessdays:
            period_str += str(self.businessdays) + 'B'
        if not period_str:
            period_str += '0D'
        return period_str


class BusinessRange(list):
    def __init__(self, start, stop=None, step=None, rolling=None):
        """
        range like class to build date list

        :param start: date to begin schedule, if stop not given, start will be used as stop and
            default in rolling to BusinessDate()
        :type start: BusinessDate or int or str
        :param stop: date to stop before, if not given, start will be used for stop instead
        :type stop: BusinessDate or int or str
        :param step: period to step schedule, if not given 1 year is default
        :type step: BusinessPeriod or str
        :param rolling: date to roll on (forward and backward) between start and stop,
            if not given default will be start
        :type rolling: BusinessDate or int or str

        range like class to build BusinessDate schedule from rolling date and BusinessPeriod
        """
        if stop is None:
            stop = start
            start = BusinessDate()
        if step is None:
            step = BusinessPeriod(years=1)
        if rolling is None:
            rolling = start
        # make proper businessdate objects
        if not isinstance(start, BusinessDate):
            if isinstance(start, BusinessPeriod):
                start = start.to_businessdate()
            else:
                start = BusinessDate(start)
        if not isinstance(rolling, BusinessDate):
            if isinstance(rolling, BusinessPeriod):
                rolling = rolling.to_businessdate()
            else:
                rolling = BusinessDate(rolling)
        if not isinstance(stop, BusinessDate):
            if isinstance(stop, BusinessPeriod):
                stop = stop.to_businessdate()
            else:
                stop = BusinessDate(stop)
        if not isinstance(step, BusinessPeriod):
            if isinstance(step, BusinessDate):
                step = step.to_businessperiod()
            else:
                step = BusinessPeriod(step)
        # roll schedule
        current = BusinessDate(rolling)
        schedule = [BusinessDate(rolling)]
        # roll backward
        current = BusinessDate.add_period(current, step)
        while current < start:
            current = BusinessDate.add_period(current, step)
        while current < stop:
            schedule.append(current)
            current = BusinessDate.add_period(current, step)
        # roll forward
        back_step = -1 * BusinessPeriod(step)
        current = BusinessDate(rolling)
        current = BusinessDate.add_period(current, back_step)
        while stop <= current:
            current = BusinessDate.add_period(current, back_step)
        while start <= current:
            schedule.append(current)
            current = BusinessDate.add_period(current, back_step)
        # remove rolldate if rolldate is enddate or later
        if not start <= rolling < stop:
            schedule.remove(rolling)
        # push to super
        super(BusinessRange, self).__init__(set(schedule))
        self.sort()

    def adjust(self, convention=None, holidays_obj=None):
        if convention is None:
            convention = 'mod_follow'
        adj_func = getattr(BusinessDate, 'adjust_' + convention.lower())
        adj_list = [adj_func(d, holidays_obj) for d in self]
        del self[:]
        super(BusinessRange, self).extend(adj_list)
        return self

    def adjust_previous(self, holidays_obj=None):
        return self.adjust('previous', holidays_obj)

    def adjust_follow(self, holidays_obj=None):
        return self.adjust('follow', holidays_obj)

    def adjust_mod_previous(self, holidays_obj=None):
        return self.adjust('mod_previous', holidays_obj)

    def adjust_mod_follow(self, holidays_obj=None):
        return self.adjust('mod_follow', holidays_obj)

    def adjust_start_of_month(self, holidays_obj=None):
        return self.adjust('start_of_month', holidays_obj)

    def adjust_end_of_month(self, holidays_obj=None):
        return self.adjust('end_of_month', holidays_obj)

    def adjust_imm(self, holidays_obj=None):
        return self.adjust('imm', holidays_obj)

    def adjust_cds_imm(self, holidays_obj=None):
        return self.adjust('cds_imm', holidays_obj)


class BusinessSchedule(BusinessRange):
    def __init__(self, start, end, step, roll=None):
        """
        class to build date schedules incl. start and end date

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
        if not roll:
            roll = end
        super(BusinessSchedule, self).__init__(start, end, step, roll)
        if not isinstance(start, BusinessDate):
            if isinstance(start, BusinessPeriod):
                start = start.to_businessdate()
            else:
                start = BusinessDate(start)
        if not isinstance(end, BusinessDate):
            if isinstance(end, BusinessPeriod):
                end = end.to_businessdate()
            else:
                end = BusinessDate(end)
        if start not in self:
            self.insert(0, start)
        if end not in self:
            self.append(end)

    def first_stub_long(self):
        if len(self)>2:
            self.pop(1)
        return self

    def last_stub_long(self):
        if len(self)>2:
            self.pop(-2)
        return self


def easter(year):
    """
    This method was ported from the work done by GM Arts,
    on top of the algorithm by Claus Tondering, which was
    based in part on the algorithm of Ouding (1940), as
    quoted in "Explanatory Supplement to the Astronomical
    Almanac", P.  Kenneth Seidelmann, editor.

    More about the algorithm may be found at:

    http://users.chariot.net.au/~gmarts/eastalg.htm

    and

    http://www.tondering.dk/claus/calendar.html

    """

    # g - Golden year - 1
    # c - Century
    # h - (23 - Epact) mod 30
    # i - Number of days from March 21 to Paschal Full Moon
    # j - Weekday for PFM (0=Sunday, etc)
    # p - Number of days from March 21 to Sunday on or before PFM
    #     (-6 to 28 methods 1 & 3, to 56 for method 2)
    # e - Extra days to add for method 2 (converting Julian
    #     date to Gregorian date)

    y = year
    g = y % 19
    e = 0
    c = y // 100
    h = (c - c // 4 - (8 * c + 13) // 25 + 19 * g + 15) % 30
    i = h - (h // 28) * (1 - (h // 28) * (29 // (h + 1)) * ((21 - g) // 11))
    j = (y + y // 4 + i + 2 - c + c // 4) % 7

    # p can be from -6 to 56 corresponding to dates 22 March to 23 May
    # (later dates apply to method 2, although 23 May never actually occurs)
    p = i - j + e
    d = 1 + (p + 27 + (p + 6) // 40) % 31
    m = 3 + (p + 26) // 30
    return date(int(y), int(m), int(d))


def target_days(year):
    self = dict()
    self[date(year, 1, 1)] = "New Year's Day"
    e = easter(year)
    self[e + timedelta(-2)] = "Black Friday"
    self[e + timedelta(1)] = "Easter Monday"
    self[date(year, 5, 1)] = "Labour Day"
    self[date(year, 12, 25)] = "First Christmas Day"
    self[date(year, 12, 26)] = "Second Christmas Day"
    return self
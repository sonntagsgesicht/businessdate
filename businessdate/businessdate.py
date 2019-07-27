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


from datetime import date, datetime

from . import conventions
from . import daycount
from .ymd import is_leap_year, days_in_year, days_in_month, end_of_quarter_month
from .basedate import BaseDate, BaseDateFloat, BaseDateDatetimeDate
from .businessholidays import TargetHolidays
from .businessperiod import BusinessPeriod


class BusinessDate(BaseDate):
    #: base date
    BASE_DATE = date.today()  # BusinessDate() initializes with date of today
    #: string: basic date format as string
    DATE_FORMAT = '%Y%m%d'
    #: list: list of dates of default holiday calendar
    DEFAULT_HOLIDAYS = TargetHolidays()

    def __new__(cls, year=None, month=0, day=0):
        r"""
        fundamental date class

        :param year: input value to create BusinessDate instance
        :type year: int, float, string or datetime.date
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

        if isinstance(year, str):
            year, month, day = cls._parse_date_string(year, default=(year, month, day))

        if isinstance(year, date):
            year, month, day = year.year, year.month, year.day

        if isinstance(year, int) and month and day:
            if issubclass(BaseDate, BaseDateFloat):
                return cls.from_ymd(year, month, day)
            elif issubclass(BaseDate, BaseDateDatetimeDate):
                return super(BusinessDate, cls).__new__(cls, year, month, day)

        if isinstance(year, (int, float)) and 1 < year < 10000101:  # excel representation before 1000 a.d.
            if issubclass(BaseDate, BaseDateFloat):
                return super(BusinessDate, cls).__new__(cls, year)
            elif issubclass(BaseDate, BaseDateDatetimeDate):
                return cls.from_float(year)

        if isinstance(year, (int, float)) and 10000101 <= year:  # start 20191231 representation from 1000 a.d.
            ymd = str(year)
            year, month, day = int(ymd[:4]), int(ymd[4:6]), int(ymd[6:])
            return cls.from_ymd(year, month, day)

        if isinstance(year, (list, tuple)):
            return list(map(BusinessDate, year))

        if year is None:
            return cls(cls.BASE_DATE)

        # try to split complex or period input, e.g. '0B1D2BMOD20191231' or '3Y2M1D' or '-2B'
        return cls._from_complex_input(str(year))

    @classmethod
    def _parse_date_string(cls, date_str, default=None):
        date_str = str(date_str)
        if date_str.count('-'):
            str_format = '%Y-%m-%d'
        elif date_str.count('.'):
            str_format = '%d.%m.%Y'
        elif date_str.count('/'):
            str_format = '%m/%d/%Y'
        elif len(date_str) == 8 and date_str.isdigit():
            str_format = '%Y%m%d'
        else:
            str_format = ''
        if str_format:
            date_date = datetime.strptime(date_str, str_format)
            return date_date.year, date_date.month, date_date.day

        if default is None:
            raise ValueError("The input %s has not the right format for %s" % (date_str, cls.__name__))
        else:
            return default

    @classmethod
    def _from_complex_input(cls, date_str):
        date_str = str(date_str).upper()
        convention, origin, holidays = None, None, None

        # first, extract origin
        if len(date_str) > 8:
            try:
                datetime.strptime(date_str[-8:], '%Y%m%d')
                origin = date_str[-8:]
                date_str = date_str[:-8]
            except ValueError:
                # no date found a the end of the string
                pass

        # second, extract
        for a in sorted(dir(conventions), key=len, reverse=True):
            if date_str.find(a.upper()) > 0:
                convention = a
                date_str = date_str[:-len(a)]
                break

        # third, parse spot, period and final
        pfields = date_str.strip('0123456789+-B')
        spot, period, final = date_str, '', ''
        if pfields:
            x = pfields[-1]
            period, final = date_str.split(x, 1)
            period += x
            if date_str.find('B') > 0:
                spot, period = period.split('B', 1)
                spot += 'B'
            else:
                spot, period = '', date_str

        # third, build BusinessDate and adjust by conventions to periods
        res = cls(origin)
        if spot:
            res = res.adjust(convention, holidays).add_period(spot, holidays)
        if period:
            res = res.add_period(period, holidays)
        if final:
            res = res.adjust(convention, holidays).add_period(final, holidays)
        return res

    @classmethod
    def is_businessdate(cls, in_date):
        """
        checks whether the provided date is a date
        :param BusinessDate, int or float in_date:
        :return bool:
        """
        if not isinstance(in_date, (date, BaseDate)):
            try:  # to be removed
                cls(in_date)
            except ValueError:
                return False
        return True

    def __copy__(self):
        return self.__deepcopy__()

    def __deepcopy__(self, memodict={}):
        return BusinessDate(date(*self.to_ymd()))

    # --- operator methods ---------------------------------------------------

    def __add__(self, other):
        """
            addition of BusinessDate.

        :param object other: can be BusinessPeriod or
        any thing that might be casted to it. Or a list of them.
        """
        if isinstance(other, (list, tuple)):
            return [self + pd for pd in other]
        if BusinessPeriod.is_businessperiod(other):
            return self.add_period(other)
        else:
            raise TypeError('addition of BusinessDates cannot handle objects of type %s.' % other.__class__.__name__)

    def __sub__(self, other):
        """
            subtraction of BusinessDate.

        :param object other: can be other BusinessDate, BusinessPeriod or
        any thing that might be casted to those. Or a list of them.
        """
        if isinstance(other, (list, tuple)):
            return [self - pd for pd in other]
        if BusinessPeriod.is_businessperiod(other):
            return self + (-1 * BusinessPeriod(other))
        elif BusinessDate.is_businessdate(other):
            y, m, d = self.diff_in_ymd(BusinessDate(other))
            return BusinessPeriod(years=y, months=m, days=d)
        else:
            raise TypeError('subtraction of BusinessDates cannot handle objects of type %s.' % other.__class__.__name__)

    def __str__(self):
        date_format = self.__class__.DATE_FORMAT
        return self.to_date().strftime(date_format)

    def __repr__(self):
        return self.__class__.__name__ + "('%s')" % str(self)

    # --- validation and information methods ------------------------

    def is_leap_year(self):
        """
        returns True for leap year and False otherwise

        :param int year: calendar year
        :return bool:
        """
        return is_leap_year(self.year)

    def days_in_year(self):
        """
        returns number of days in the given calendar year

        :param int year: calendar year
        :return int:
        """

        return days_in_year(self.year)

    def days_in_month(self):
        """
        returns number of days for the given year and month

        :param int year: calendar year
        :param int month: calendar month
        :return int:
        """

        return days_in_month(self.year, self.month)

    def end_of_month(self):
        return BusinessDate(self.year, self.month, self.days_in_month())

    def end_of_quarter(self):
        return BusinessDate(self.year, end_of_quarter_month(self.month), 0o1).end_of_month()

    def is_business_day(self, holidays_obj=None):
        """
        :param list holidays_obj : datetime.date list defining business holidays
        :return: bool

        method to check if a date falls neither on weekend nor is holiday
        """
        holidays_obj = self.__class__.DEFAULT_HOLIDAYS if holidays_obj is None else holidays_obj
        return conventions.is_business_day(self.to_date(), holidays_obj)

    # --- calculation methods --------------------------------------------

    def add_years(self, years_int):
        """
        addition of a number of years

        :param int years_int:
        :return BusinessDate:
        """
        y, m, d = self.to_ymd()
        y += years_int
        if not is_leap_year(y) and m == 2:
            d = min(28, d)
        return self.__class__.from_ymd(y, m, d)

    def add_months(self, month_int):
        """
        addition of a number of months

        :param BusinessDate d:
        :param int month_int:
        :return BusinessDate:
        """
        res = self
        month_int += res.month
        while month_int > 12:
            res = res.add_years(1)
            month_int -= 12
        while month_int < 1:
            res = res.add_years(-1)
            month_int += 12
        l = days_in_month(res.year, month_int)
        return res.__class__.from_ymd(res.year, month_int, min(l, res.day))

    def add_business_days(self, days_int, holidays_obj=None):
        """
        private method for the addition of business days, used in the addition of a BusinessPeriod only

        :param BusinessDate d:
        :param int days_int:
        :param list holidays_obj:
        :return: BusinessDate
        """

        holidays_obj = self.__class__.DEFAULT_HOLIDAYS if holidays_obj is None else holidays_obj

        res = self.__deepcopy__()
        if days_int >= 0:
            count = 0
            while count < days_int:
                res = res.add_days(1)
                if res.is_business_day(holidays_obj):
                    count += 1
        else:
            count = 0
            while count > days_int:
                res = res.add_days(-1)
                if res.is_business_day(holidays_obj):
                    count -= 1

        return res

    def add_ymd(self, years=0, months=0, days=0):
        if self.month == 2 and self.day == 29:
            years += int(months // 12)
            months = int(months % 12)
            return self.add_months(months).add_years(years).add_days(days)
        else:
            return self.add_years(years).add_months(months).add_days(days)

    def add_period(self, period_obj, holidays_obj=None):
        p = BusinessPeriod(period_obj)
        res = self
        res = res.add_business_days(p.businessdays, holidays_obj)
        res = res.add_ymd(p.years, p.months, p.days)
        return res

    def diff_in_ymd(self, end_date):
        """
        difference expressed as a tuple of years, months, days
        (see also the python lib dateutils.relativedelta)

        :param BusinessDate start_date:
        :param BusinessDate end_date:
        :return (int, int, int):
        """

        if end_date < self:
            y, m, d = end_date.diff_in_ymd(self)
            return -y, -m, -d
        y = end_date.year - self.year
        m = end_date.month - self.month

        while m < 0:
            y -= 1
            m += 12
        # never used, even by 100% test coverage
        # while m > 12:
        #     y += 1
        #     m -= 12

        s = self.add_ymd(y, m, 0)
        d = s.diff_in_days(end_date)

        if d < 0:
            m -= 1
            if m < 0:
                y -= 1
                m += 12
            s = self.add_ymd(y, m, 0)

        d = s.diff_in_days(end_date)

        return -int(y), -int(m), -int(d)

    # --- day count fraction methods -----------------------------------------

    def get_day_count(self, end, convention='act_36525'):
        convention = convention.lower()
        dc_func = getattr(daycount, 'get_' + convention, None)
        if dc_func is None:
            for c in '/-_. ':
                convention = convention.replace(c, '')
            dc_func = getattr(daycount, convention)
        return dc_func(self.to_date(), end.to_date())

    def get_30_360(self, end):
        return self.get_day_count(end, '30_360')

    def get_act_36525(self, end):
        return self.get_day_count(end, 'ACT_36525')

    def get_act_365(self, end):
        return self.get_day_count(end, 'ACT_365')

    def get_act_360(self, end):
        return self.get_day_count(end, 'ACT_360')

    def get_act_act(self, end):
        return self.get_day_count(end, 'ACT_ACT')

    def get_30e_360(self, end):
        return self.get_day_count(end, '30E_360')

    def get_30e_360_isda(self, end):
        return self.get_day_count(end, '30E_360_ISDA')

    # --- business day adjustment methods ------------------------------------

    def adjust(self, convention=None, holidays_obj=None):
        if convention is None:
            return self.__copy__()
        convention = convention.lower()
        adj_func = getattr(conventions, 'adjust_' + convention, None)
        if adj_func is None:
            for c in '/-_. ':
                convention = convention.replace(c,'')
            adj_func = getattr(conventions, convention)
        holidays_obj = self.__class__.DEFAULT_HOLIDAYS if holidays_obj is None else holidays_obj
        return BusinessDate(adj_func(self.to_date(), holidays_obj))

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

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


from datetime import date, datetime, timedelta

from methods.adjust import is_business_day, adjust_no, adjust_previous, adjust_follow, adjust_mod_previous, \
    adjust_mod_follow, adjust_start_of_month, adjust_end_of_month, adjust_imm, adjust_cds_imm
from methods.daycount import get_act_act, get_30_360, get_act_36525, get_act_360, get_act_365, \
    get_30e_360, get_30e_360_isda
from methods.ymd import is_leap_year, days_in_year, days_in_month, end_of_quarter_month
from methods.holidays import target_days
from basedate import BaseDate, BaseDateFloat, BaseDateDatetimeDate


class BusinessHolidays(list):
    """
    holiday calendar class
    """

    def __init__(self, iterable=()):
        if iterable:
            iterable = [bd.to_date() for bd in map(BusinessDate, iterable)]
        super(BusinessHolidays, self).__init__(iterable)


class TargetHolidays(BusinessHolidays):
    """
    holiday calendar class for ecb target2 holidays
    """

    def __contains__(self, item):
        if not super(TargetHolidays, self).__contains__(date(item.year, 1, 1)):
            # add tar days if not done jet
            self.extend(target_days(item.year).keys())
        return super(TargetHolidays, self).__contains__(item)


class BusinessDate(BaseDate):
    #: base date
    BASE_DATE = date.today()  # BusinessDate() initializes with date of today
    #: string: basic date format as string
    DATE_FORMAT = '%Y%m%d'
    #: list: list of dates of default holiday calendar
    DEFAULT_HOLIDAYS = TargetHolidays()

    def __new__(cls, date_value=None, *args):
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

        if issubclass(BaseDate, BaseDateFloat):
            if isinstance(date_value, (int, float)) and 1 < date_value < 500 * 365.250:
                return super(BusinessDate, cls).__new__(cls, date_value)
        elif issubclass(BaseDate, BaseDateDatetimeDate):
            if args:
                return super(BusinessDate, cls).__new__(cls, date_value, args[0], args[1])

        if date_value is None:
            new_date = BusinessDate(cls.BASE_DATE)
        elif args:
            y, (m, d) = date_value, args
            new_date = BusinessDate.from_ymd(y, m, d)
        elif isinstance(date_value, int):
            new_date = BusinessDate.from_int(date_value)
        elif isinstance(date_value, float):
            new_date = BusinessDate.from_float(date_value)
        elif isinstance(date_value, str):
            new_date = BusinessDate.from_string(str(date_value))
        elif isinstance(date_value, (date, datetime)):
            new_date = BusinessDate.from_date(date_value)
        elif isinstance(date_value, list):
            new_date = [BusinessDate(d) for d in date_value]
        else:
            raise ValueError("Can't build BusinessDate from %s of type %s" % (str(date_value), str(type(date_value))))

        return new_date

    def __copy__(self):
        return self.__deepcopy__()

    def __deepcopy__(self, memodict={}):
        return BusinessDate(date(*self.to_ymd()))

    # --- operator methods ---------------------------------------------------

    def __add__(self, other):
        """
            addition of BusinessDate.

        :param BusinessDate or BusinessPeriod or str other: can be BusinessPeriod or
        any thing that might be casted to it.
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

        :param object other: can be other BusinessDate, BusinessPeriod or any thing that might be casted to those.
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
        return self.to_string()

    def __repr__(self):
        return self.__class__.__name__ + "('" + self.to_string() + "')"

    # --- constructor methods ------------------------------------------------

    @classmethod
    def from_businessdate(cls, d):
        """
        copy constructor

        :param BusinessDate d:
        :return bankdate:
        """
        return d.__deepcopy__()

    @classmethod
    def from_string(cls, date_str):
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
        else:
            msg = "the date string %s has not the right format for %s" % (date_str, cls.__name__)
            raise ValueError(msg)
        return cls.from_date(datetime.strptime(date_str, str_format))

    @classmethod
    def from_int(cls, date_int):
        if 1 < date_int < 200 * 365.25:
            return cls.from_excel(date_int)
        return cls.from_string(str(date_int))

    @classmethod
    def from_float(cls, date_float):
        return cls.from_int(int(date_float))

    # --- cast methods -------------------------------------------------------

    def to_datetime(self, origin_date=None):
        return self.to_date()

    def to_businessdate(self, origin_date=None):
        return self

    def to_businessperiod(self, origin_date=None):
        if origin_date is None:
            origin_date = BusinessDate()
        y, m, d = origin_date.diff_in_ymd(self)
        return BusinessPeriod(years=y, months=m, days=d)

    def to_string(self, date_format=None):
        """
        return BusinessDate as 'date.strftime(DATE_FORMAT)'

        :return string:
        """
        if date_format is None:
            date_format = self.__class__.DATE_FORMAT

        return self.to_date().strftime(date_format)

    def to_int(self):
        return int(self.to_excel())

    def to_float(self):
        return float(self.to_excel())

    # --- validation and information methods ------------------------

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

    @staticmethod
    def is_businessdate(in_date):
        """
        checks whether the provided date is a date
        :param BusinessDate, int or float in_date:
        :return bool:
        """
        if not isinstance(in_date, (date, BaseDate)):
            try:  # to be removed
                BusinessDate(in_date)
            except ValueError:
                return False
        return True

    @staticmethod
    def end_of_month(year, month):
        return BusinessDate.from_date(date(year, month, days_in_month(year, month)))

    @staticmethod
    def end_of_quarter(year, month):
        return BusinessDate.end_of_month(year, end_of_quarter_month(month))

    def is_business_day(self, holidays_obj=None):
        """
        :param list holidays_obj : datetime.date list defining business holidays
        :return: bool

        method to check if a date falls neither on weekend nor is holiday
        """
        holidays_obj = self.__class__.DEFAULT_HOLIDAYS if holidays_obj is None else holidays_obj
        return is_business_day(self.to_date(), holidays_obj)

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
            years += months // 12
            months %= 12
            return self.add_months(months).add_years(years).add_days(days)
        else:
            return self.add_years(years).add_months(months).add_days(days)

    def add_period(self, period_obj, holidays_obj=None):
        p = BusinessPeriod(period_obj)
        res = self.add_ymd(p.years, p.months, p.days)
        return res.add_business_days(p.businessdays, holidays_obj)

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
        while m > 12:
            y += 1
            m -= 12

        s = self.add_ymd(y,m,0)
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
        dc_func = globals()['get_' + convention.lower()]
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

    def adjust(self, convention='no', holidays_obj=None):
        adj_func = globals()['adjust_' + convention.lower()]
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


class BusinessPeriod(object):
    def __init__(self, period_in='', years=0, months=0, days=0, businessdays=0):
        """
        class managing date periods like days, weeks, years etc.

        :param period_in:
        :param years:
        :param months:
        :param days:
        :param businessdays:

        representation of a time BusinessPeriod,
        similar to dateutils.relativedelta,
        but with additional business day logic
        """

        super(BusinessPeriod, self).__init__()
        if isinstance(period_in, BusinessPeriod):
            years += period_in.years
            months += period_in.months
            days += period_in.days
            businessdays = period_in.businessdays
        elif isinstance(period_in, timedelta):
            days += timedelta.days
        elif isinstance(period_in, str):
            if period_in.upper() == '':
                pass
            elif period_in.upper() == '0D':
                pass
            elif period_in.upper() == 'ON':
                businessdays += 1
            elif period_in.upper() == 'TN':
                businessdays += 2
            elif period_in.upper() == 'DD':
                businessdays += 3
            else:
                sgn, p = (-1, period_in[1:]) if period_in.startswith('-') else (1, period_in)
                y, m, d, b = BusinessPeriod.parse_ymd(p)
                years += sgn * y
                months += sgn * m
                days += sgn * d
                businessdays += sgn * b

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
    def parse_ymd(cls, period_str):
        p = period_str.upper()
        b, y, q, m, w, d = '000000'
        if p.find('B') > 0:
            b, p = p.split('B', 2)
        if p.find('Y') > 0:
            y, p = p.split('Y', 2)
        if p.find('Q') > 0:
            q, p = p.split('Q', 2)
        if p.find('M') > 0:
            m, p = p.split('M', 2)
        if p.find('W') > 0:
            w, p = p.split('W', 2)
        if p.find('D') > 0:
            d, p = p.split('D', 2)
        if not all(x.isdigit() for x in (b, y, q, m, w, d)):
            raise ValueError("Unable to parse %s as %s" % (period_str, cls.__name__))
        b = int(b)
        y, m, d = int(y), int(q) * 3 + int(m), int(w) * 7 + int(d)
        y += m // 12
        m %= 12
        if b and any((y, m, d)):
            raise ValueError("Unable to parse %s as %s" % (period_str, cls.__name__))
        return y, m, d, b

    @classmethod
    def is_businessperiod(cls, in_period):
        """
        :param in_period: object to be checked
        :type in_period: object, str, timedelta
        :return: True if cast works
        :rtype: Boolean

        checks is argument can be casted to BusinessPeriod
        """
        if in_period in ('', '0D', BusinessPeriod()):
            return True
        try:  # to be removed
            return BusinessPeriod(in_period).__nonzero__()
        except ValueError:
            return False

    # --- property methods ---------------------------------------------------

    # --- operator methods ---------------------------------------------------

    def __repr__(self):
        return self.__class__.__name__ + "('" + self.to_string() + "')"

    def __str__(self):
        return self.to_string()

    def __abs__(self):
        self.years = abs(self.years)
        self.months = abs(self.months)
        self.days = abs(self.days)
        self.businessdays = abs(self.businessdays)

    def __cmp__(self, other):
        """ compare BusinessPeriods, comparison by (years*12+months)*31+days

        :param BusinessPeriod other:
        :return: int
        """
        assert type(self) == type(other), "types don't match %s" % str((type(self), type(other)))
        s = (self.years * 12 + self.months) * 31 + self.days
        o = (other.years * 12 + other.months) * 31 + other.days
        return s - o

    def __eq__(self, other):
        if isinstance(other, type(self)):
            attr = 'years', 'months', 'days', 'businessdays'
            return all(getattr(self, a) == getattr(other, a) for a in attr)
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __le__(self, other):
        return self.__cmp__(other) <= 0

    def __lt__(self, other):
        return self.__cmp__(other) < 0

    def __ge__(self, other):
        return self.__cmp__(other) >= 0

    def __gt__(self, other):
        return self.__cmp__(other) > 0

    def __hash__(self):
        return hash(repr(self))

    def __nonzero__(self):
        return any((self.years, self.months, self.days, self.businessdays))

    def __add__(self, other):
        if isinstance(other, (list, tuple)):
            return [self + o for o in other]
        elif BusinessPeriod.is_businessperiod(other):
            return self.add_businessperiod(BusinessPeriod(other))
        else:
            raise TypeError('addition of BusinessPeriod cannot handle objects of type %s.' % other.__class__.__name__)

    def __sub__(self, other):
        if isinstance(other, (list, tuple)):
            return [self - o for o in other]
        elif BusinessPeriod.is_businessperiod(other):
            return self.add_businessperiod(-1 * BusinessPeriod(other))
        else:
            raise TypeError(
                'subtraction of BusinessPeriod cannot handle objects of type %s.' % other.__class__.__name__)

    def __mul__(self, other):
        if isinstance(other, (list, tuple)):
            return [self * o for o in other]
        if isinstance(other, int):
            y = other * self.years
            m = other * self.months
            d = other * self.days
            b = other * self.businessdays
            return BusinessPeriod(years=y, months=m, days=d, businessdays=b)
        else:
            raise TypeError("expected int or long but got %s" % str(type(other)))

    def __rmul__(self, other):
        return self.__mul__(other)

    # --- calculation methods ------------------------------------------------

    def add_years(self, years_int):
        y = self.years + years_int
        m = self.months
        d = self.days
        b = self.businessdays
        return self.__class__(years=y, months=m, days=d, businessdays=b)

    def add_months(self, months_int):
        y = self.years
        m = self.months + months_int
        d = self.days
        b = self.businessdays
        return self.__class__(years=y, months=m, days=d, businessdays=b)

    def add_days(self, days_int):
        y = self.years
        m = self.months
        d = self.days + days_int
        b = self.businessdays
        return self.__class__(years=y, months=m, days=d, businessdays=b)

    def add_businessdays(self, businessdays_int):
        y = self.years
        m = self.months
        d = self.days
        b = self.businessdays + businessdays_int
        return self.__class__(years=y, months=m, days=d, businessdays=b)

    def add_businessperiod(self, p):
        y = self.years + p.years
        m = self.months + p.months
        d = self.days + p.days
        b = self.businessdays + p.businessdays
        return self.__class__(years=y, months=m, days=d, businessdays=b)

    # --- cast methods -------------------------------------------------------

    def to_date(self, start_date=None):
        return self.to_businessdate(start_date).to_date()

    def to_datetime(self, start_date=None):
        return self.to_businessdate(start_date).to_datetime()

    def to_businessdate(self, start_date=None):
        if start_date:
            return start_date + self
        else:
            return BusinessDate() + self

    def to_businessperiod(self, start_date=None):
        return self

    def to_string(self):
        period_str = ''
        if self.businessdays:
            period_str += str(self.businessdays) + 'B'
        if self.years:
            period_str += str(self.years) + 'Y'
        if self.months:
            period_str += str(self.months) + 'M'
        if self.days:
            period_str += str(self.days) + 'D'
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

        range like class to build BusinessDate list from rolling date and BusinessPeriod

        First, :code:`rolling` and :code:`step` defines a infinite grid of dates.
        Second, this grid is sliced by :code:`start` (included , if meeting the grid) and
        :code:`end` (excluded).

        """

        # set default args and build range grid
        start, stop, step, rolling = self._default_args(start, stop, step, rolling)
        schedule = self._build_grid(start, stop, step, rolling)

        # push to super and sort
        super(BusinessRange, self).__init__(set(schedule))
        self.sort()

    @staticmethod
    def _default_args(start, stop, step, rolling):
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
        return BusinessDate(start), BusinessDate(stop), BusinessPeriod(step), BusinessDate(rolling)

    @staticmethod
    def _build_grid(start, stop, step, rolling):
        # setup grid and turn step into positive direction
        grid = list()
        step = step if rolling <= rolling + step else -1 * step

        # roll backward before start
        i = 0
        current = rolling + step * i
        while start <= current:
            i -= 1
            current = rolling + step * i

        # fill grid from start until end
        current = rolling + step * i
        while current < stop:
            current = rolling + step * i
            if start <= current < stop:
                grid.append(current)
            i += 1

        return grid

    def adjust(self, convention='mod_follow', holidays_obj=None):
        adj_list = [d.adjust(convention, holidays_obj) for d in self]
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
        super(BusinessSchedule, self).__init__(start, end, step, roll)
        if start not in self:
            self.insert(0, start)
        if end not in self:
            self.append(end)

    def first_stub_long(self):
        if len(self) > 2:
            self.pop(1)
        return self

    def last_stub_long(self):
        if len(self) > 2:
            self.pop(-2)
        return self

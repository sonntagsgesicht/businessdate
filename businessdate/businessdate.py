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

import methods.adjust
import methods.daycount
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

        if isinstance(year, (date, datetime)):
            year, month, day = year.year, year.month, year.day

        if isinstance(year, (int, float)) and month and day:
            if issubclass(BaseDate, BaseDateFloat):
                return cls.from_ymd(year, month, day)
            elif issubclass(BaseDate, BaseDateDatetimeDate):
                return super(BusinessDate, cls).__new__(cls, year, month, day)

        if isinstance(year, (int, float)) and 1 < year < 10000101:  # excel representation before 1000 a.d.
            if issubclass(BaseDate, BaseDateFloat):
                return super(BusinessDate, cls).__new__(cls, year)
            elif issubclass(BaseDate, BaseDateDatetimeDate):
                return cls.from_excel(year)

        if isinstance(year, (int, float)) and 10000101 <= year:  # start 20191231 representation from 1000 a.d.
            ymd = str(year)
            year, month, day = int(ymd[:4]), int(ymd[4:6]), int(ymd[6:])
            if issubclass(BaseDate, BaseDateFloat):
                return cls.from_ymd(year, month, day)
            elif issubclass(BaseDate, BaseDateDatetimeDate):
                return super(BusinessDate, cls).__new__(cls, year, month, day)

        if isinstance(year, list):
            return [BusinessDate(d) for d in year]

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
        for a in sorted(dir(methods.adjust), lambda a,b: len(b)-len(a)):
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
        return BusinessDate(self.year, end_of_quarter_month(self.month), 01).end_of_month()

    def is_business_day(self, holidays_obj=None):
        """
        :param list holidays_obj : datetime.date list defining business holidays
        :return: bool

        method to check if a date falls neither on weekend nor is holiday
        """
        holidays_obj = self.__class__.DEFAULT_HOLIDAYS if holidays_obj is None else holidays_obj
        return methods.adjust.is_business_day(self.to_date(), holidays_obj)

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
        while m > 12:
            y += 1
            m -= 12

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
        # dc_func = globals()['get_' + convention.lower()]
        dc_func = getattr(methods.daycount,'get_' + convention.lower(), None)
        if dc_func is None:
            dc_func = getattr(methods.daycount, convention.lower().strip('-_/ '))
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
        adj_func = getattr(methods.adjust,'adjust_' + convention.lower(), None)
        if adj_func is None:
            adj_func = getattr(methods.adjust, convention.lower().strip('-_/ '))
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
        if period_in and any((years, months, days, businessdays)):
            raise ValueError(
                "Either string or argument input only for %s" % self.__class__.__name__)

        super(BusinessPeriod, self).__init__()
        if isinstance(period_in, BusinessPeriod):
            years = period_in.years
            months = period_in.months
            days = period_in.days
            businessdays = period_in.businessdays
        elif isinstance(period_in, timedelta):
            days = timedelta.days
        elif isinstance(period_in, str):
            if period_in.upper() == '':
                pass
            elif period_in.upper() == '0D':
                pass
            elif period_in.upper() == 'ON':
                businessdays = 1
            elif period_in.upper() == 'TN':
                businessdays = 2
            elif period_in.upper() == 'DD':
                businessdays = 3
            else:
                s, y, q, m, w, d, f = BusinessPeriod._parse_ymd(period_in)
                # no final businesdays allowed
                if f:
                    raise ValueError("Unable to parse %s as %s" % (period_in, self.__class__.__name__))
                # except the first non vanishing of y,q,m,w,d must have positive sign
                sgn = [x / abs(x) for x in (y, q, m, w, d) if x]
                if [x for x in sgn[1:] if x < 0]:
                    raise ValueError(
                        "Except at the begining no signs allowed in %s as %s" % (period_in, self.__class__.__name__))
                y, q, m, w, d = (abs(x) for x in (y, q, m, w, d))
                # consolidate a quarter as three month and a week as seven days
                m += q * 3
                d += w * 7
                # use sign of first non vanishing of y,q,m,w,d
                sgn = sgn[0] if sgn else 1
                businessdays, years, months, days = s, sgn * y, sgn * m, sgn * d

        if months >= 12:
            years += months // 12
            months %= 12
        if months <= -12:
            months, years = -months, -years
            years += months // 12
            months %= 12
            months, years = -months, -years

        ymd = years, months, days
        if businessdays and any(ymd):
            raise ValueError("Either (years,months,days) or businessdays must be zero for %s" % self.__class__.__name__)
        if len(set(x / abs(x) for x in ymd if x)) > 1:
            raise ValueError(
                "(years, months, days)=%s must have equal sign for %s" % (str(ymd), self.__class__.__name__))

        self.years = years
        self.months = months
        self.days = days
        self.businessdays = businessdays

    # --- validation and information methods ---------------------------------

    @classmethod
    def _parse_ymd(cls, period_str):
        """
        can even parse strings like '-1B-2Y-4Q+5M' but also '0B', '-1Y2M3D' as well.

        :param period_str:
        :return:
        """
        def _parse(p, letter):
            if p.find(letter) > 0:
                s, p = p.split(letter, 1)
                s = s[1:] if s.startswith('+') else s
                sgn, s = (-1, s[1:]) if s.startswith('-') else (1, s)
                if not s.isdigit():
                    raise ValueError("Unable to parse %s in %s as %s" % (s, p, cls.__name__))
                return sgn * int(s), p
            return 0, p

        p = period_str.upper()
        s, p = _parse(p, 'B')
        y, p = _parse(p, 'Y')
        q, p = _parse(p, 'Q')
        m, p = _parse(p, 'M')
        w, p = _parse(p, 'W')
        d, p = _parse(p, 'D')
        f, p = _parse(p, 'B')
        if not p == '':
            raise ValueError("Unable to parse %s as %s" % (p, cls.__name__))
        return s, y, q, m, w, d, f

    @classmethod
    def is_businessperiod(cls, in_period):
        """
        :param in_period: object to be checked
        :type in_period: object, str, timedelta
        :return: True if cast works
        :rtype: Boolean

        checks is argument can be casted to BusinessPeriod
        """
        if in_period is None:
            return False
        if isinstance(in_period, (int, float, list, set, dict, tuple)):
            return False
        if isinstance(in_period, (timedelta, BusinessPeriod)):
            return True
        if in_period in ('', '0D', 'ON', 'TN', 'DD'):
            return True
        if isinstance(in_period, str):
            if in_period.isdigit():
                return False
            if in_period.upper().strip('+-0123456789BYQMWD'):
                return False
            try:  # to be removed
                BusinessPeriod._parse_ymd(in_period)
            except ValueError:
                return False
            return True
        return False

    # --- operator methods ---------------------------------------------------

    def __repr__(self):
        return self.__class__.__name__ + "('%s')" % str(self)

    def __str__(self):
        period_str = ''
        if self.businessdays:
            period_str = str(self.businessdays) + 'B'
        else:
            period_str = '-' if self.years < 0 or self.months < 0 or self.days < 0 else ''
            if self.years:
                period_str += str(abs(self.years)) + 'Y'
            if self.months:
                period_str += str(abs(self.months)) + 'M'
            if self.days:
                period_str += str(abs(self.days)) + 'D'

        if not period_str:
            period_str = '0D'
        return period_str

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
            p = BusinessPeriod(other)
            y = self.years + p.years
            m = self.months + p.months
            d = self.days + p.days
            b = self.businessdays + p.businessdays
            return self.__class__(years=y, months=m, days=d, businessdays=b)
        else:
            raise TypeError(
                'addition of BusinessPeriod cannot handle objects of type %s.' % other.__class__.__name__)

    def __sub__(self, other):
        if isinstance(other, (list, tuple)):
            return [self - o for o in other]
        elif BusinessPeriod.is_businessperiod(other):
            return self + (-1 * BusinessPeriod(other))
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

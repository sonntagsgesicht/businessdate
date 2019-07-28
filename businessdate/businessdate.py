# -*- coding: utf-8 -*-
#
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
from .basedate import BaseDateFloat, BaseDateDatetimeDate
from .businessholidays import TargetHolidays
from .businessperiod import BusinessPeriod


class BusinessDate(BaseDateDatetimeDate):

    BASE_DATE = date.today()
    DATE_FORMAT = '%Y%m%d'
    DAY_COUNT = 'act_36525'
    DEFAULT_HOLIDAYS = TargetHolidays()

    _adj_func = {
        'no': conventions.adjust_no,
        'previous': conventions.adjust_previous,
        'prev': conventions.adjust_previous,
        'prv': conventions.adjust_previous,
        'mod_previous': conventions.adjust_mod_previous,
        'modprevious': conventions.adjust_mod_previous,
        'modprev': conventions.adjust_mod_previous,
        'modprv': conventions.adjust_mod_previous,
        'follow': conventions.adjust_follow,
        'flw': conventions.adjust_follow,
        'mod_follow': conventions.adjust_mod_follow,
        'modfollow': conventions.adjust_mod_follow,
        'modflw': conventions.adjust_mod_follow,
        'start_of_month': conventions.adjust_start_of_month,
        'startofmonth': conventions.adjust_start_of_month,
        'som': conventions.adjust_start_of_month,
        'end_of_month': conventions.adjust_end_of_month,
        'endofmonth': conventions.adjust_end_of_month,
        'eom': conventions.adjust_end_of_month,
        'imm': conventions.adjust_imm,
        'cds_imm': conventions.adjust_cds_imm,
        'cdsimm': conventions.adjust_cds_imm,
        'cds': conventions.adjust_cds_imm,
    }
    _dc_func = {
        '30_360': daycount.get_30_360,
        '30360': daycount.get_30_360,
        'thirty360': daycount.get_30_360,
        '30e_360': daycount.get_30e_360,
        '30e360': daycount.get_30e_360,
        'thirtye360': daycount.get_30e_360,
        '30e_360_isda': daycount.get_30e_360_isda,
        '30e360isda': daycount.get_30e_360_isda,
        'thirtye360isda': daycount.get_30e_360_isda,
        'act_360': daycount.get_act_360,
        'act360': daycount.get_act_360,
        'act_365': daycount.get_act_365,
        'act365': daycount.get_act_365,
        'act_36525': daycount.get_act_36525,
        'act_365.25': daycount.get_act_36525,
        'act36525': daycount.get_act_36525,
        'act_act': daycount.get_act_act,
        'actact': daycount.get_act_act,
    }

    def __new__(cls, year=None, month=0, day=0):
        """ date class to perform calculations coming from financial businesses

        :param year: number of year or some other input value to create BusinessDate instance.
         When applying other input, this can be either `int`, `float`, `datetime.date` or `string`
         which will be parsed and transformed into equivalent int tuple `(year,month,day)`
         (See :ref:`tutorial` for details).
        :param int month: number of month in year 1 ... 12
         (default: 0, required to be 0 when other input of year is used)
        :param int days: number of day in month 1 ... 31
         (default: 0, required to be 0 when other input of year is used)

        """

        if isinstance(year, str):
            year, month, day = cls._parse_date_string(year, default=(year, month, day))

        if isinstance(year, (date, BaseDateFloat, BaseDateDatetimeDate, BusinessDate)):
            year, month, day = year.year, year.month, year.day

        if isinstance(year, (int, float)) and 10000101 <= year:  # start 20191231 representation from 1000 a.d.
            ymd = str(year)
            year, month, day = int(ymd[:4]), int(ymd[4:6]), int(ymd[6:])

        if isinstance(year, int) and month and day:
            if issubclass(cls, BaseDateFloat):
                return cls.from_ymd(year, month, day)
            return super(BusinessDate, cls).__new__(cls, year, month, day)

        if isinstance(year, (int, float)) and 1 < year < 10000101:  # excel representation before 1000 a.d.
            if issubclass(cls, BaseDateDatetimeDate):
                return cls.from_float(year)
            return super(BusinessDate, cls).__new__(cls, year)

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
        for a in sorted(cls._adj_func.keys(), key=len, reverse=True):
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
            if convention:
                res = res.adjust(convention, holidays)
            res = res.add_period(spot, holidays)
        if period:
            res = res.add_period(period, holidays)
        if final:
            if convention:
                res = res.adjust(convention, holidays)
            res = res.add_period(final, holidays)
        return res

    @classmethod
    def is_businessdate(cls, in_date):
        """ checks whether the provided date is a date """
        if not isinstance(in_date, (date, BaseDateFloat, BaseDateDatetimeDate)):
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
        if BusinessDate.is_businessdate(other):
            y, m, d = self.diff_in_ymd(BusinessDate(other))
            return BusinessPeriod(years=y, months=m, days=d)
        raise TypeError('subtraction of BusinessDates cannot handle objects of type %s.' % other.__class__.__name__)

    def __str__(self):
        date_format = self.__class__.DATE_FORMAT
        return self.to_date().strftime(date_format)

    def __repr__(self):
        return self.__class__.__name__ + "(%s)" % str(self)

    # --- validation and information methods ------------------------

    def is_leap_year(self):
        """ returns True for leap year and False otherwise """
        return is_leap_year(self.year)

    def days_in_year(self):
        """ returns number of days in the given calendar year """
        return days_in_year(self.year)

    def days_in_month(self):
        """ returns number of days for the month """
        return days_in_month(self.year, self.month)

    def end_of_month(self):
        """ returns the day of the end of the month as `BusinessDate` object"""
        return BusinessDate(self.year, self.month, self.days_in_month())

    def end_of_quarter(self):
        """ returns the day of the end of the quarter as `BusinessDate` object"""
        return BusinessDate(self.year, end_of_quarter_month(self.month), 0o1).end_of_month()

    def is_business_day(self, holidays=None):
        """ returns true if date falls neither on weekend nor is in holidays (if given as container object) """
        holidays = self.__class__.DEFAULT_HOLIDAYS if holidays is None else holidays
        return conventions.is_business_day(self.to_date(), holidays)

    # --- calculation methods --------------------------------------------

    def _add_years(self, years_int):
        y, m, d = self.to_ymd()
        y += years_int
        if not is_leap_year(y) and m == 2:
            d = min(28, d)
        return self.__class__.from_ymd(y, m, d)

    def _add_months(self, month_int):
        res = self
        month_int += res.month
        while month_int > 12:
            res = res._add_years(1)
            month_int -= 12
        while month_int < 1:
            res = res._add_years(-1)
            month_int += 12
        l = days_in_month(res.year, month_int)
        return res.__class__.from_ymd(res.year, month_int, min(l, res.day))

    def _add_business_days(self, days_int, holidays=None):
        holidays = self.__class__.DEFAULT_HOLIDAYS if holidays is None else holidays

        res = self.__deepcopy__()
        if days_int >= 0:
            count = 0
            while count < days_int:
                res = res._add_days(1)
                if res.is_business_day(holidays):
                    count += 1
        else:
            count = 0
            while count > days_int:
                res = res._add_days(-1)
                if res.is_business_day(holidays):
                    count -= 1

        return res

    def _add_ymd(self, years=0, months=0, days=0):
        if self.month == 2 and self.day == 29:
            years += int(months // 12)
            months = int(months % 12)
            return self._add_months(months)._add_years(years)._add_days(days)
        return self._add_years(years)._add_months(months)._add_days(days)

    def add_period(self, period_obj, holidays=None):
        """ adds a `BusinessPeriod` object or anythings that create one and returns `BusinessDate` object.

        It is simply adding the number of `years`, `months` and `days` or.
        if `businessdays` given, number of business days,
        i.e. days neither weekend nor in holidays (see also `BusinessDate.is_businessdate()`)
        """

        p = BusinessPeriod(period_obj)
        res = self
        res = res._add_business_days(p.businessdays, holidays)
        res = res._add_ymd(p.years, p.months, p.days)
        return res

    def diff_in_ymd(self, end_date):
        """ calculates the distance to a `BusinessDate`, expressed as a tuple of years, months, days.

        (see also the python lib dateutils.relativedelta)
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

        s = self._add_ymd(y, m, 0)
        d = s._diff_in_days(end_date)

        if d < 0:
            m -= 1
            if m < 0:
                y -= 1
                m += 12
            s = self._add_ymd(y, m, 0)

        d = s._diff_in_days(end_date)

        return -int(y), -int(m), -int(d)

    # --- business day adjustment and day count fraction methods -----------------------------------------

    def get_day_count(self, end, convention=''):
        """ counts the days as a year fraction to given date following the specified convention.

        For possible conventions invoke `BusinessDate().get_day_count(BusinessDate(), 'list')`.

        For more details on the conventions see module `businessdate.daycount`.
        """
        dc_func = self.__class__._dc_func
        default_cf_func = dc_func[self.__class__.DAY_COUNT]
        if not convention:
            s = '\n' \
                'In order to get the year fraction according a day count convention' \
                'use `BusinessDate().get_day_count(BusinessDate(), convention)` \n' \
                'and provide one of the following convention key words: \n'
            print(s)
            for k,v in dc_func.items():
                print('  ' + ("'%s'"%k).ljust(16) + '' + v.__doc__)
            print('\n Default value is %s.' %self.__class__.DAY_COUNT)
            return default_cf_func(self.to_date(), BusinessDate(end).to_date())
        return dc_func[convention.lower()](self.to_date(), BusinessDate(end).to_date())

    def adjust(self, convention='', holidays=None):
        """ returns an adjusted `BusinessDate` if it was not a business day following the specified convention.

        For details on business days see 'BusinessDate.is_businessday()`.

        For possible conventions invoke `BusinessDate().adjust()`

        For more details on the conventions see module `businessdate.conventions`)
        """
        adj_func = self.__class__._adj_func
        if not convention:
            s = '\n' \
                'In order to adjust according a business day convention' \
                'use `BusinessDate().adjust(convention, holidays=None)` \n' \
                'and provide one of the following convention key words: \n'
            print(s)
            for k,v in adj_func.items():
                print('  ' + ("'%s'"%k).ljust(16) + '' + v.__doc__)
            print('')
            return self
        holidays = self.__class__.DEFAULT_HOLIDAYS if holidays is None else holidays
        return BusinessDate(adj_func[convention.lower()](self.to_date(), holidays))

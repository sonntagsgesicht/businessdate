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


from datetime import timedelta


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
                sgn = [int(x / abs(x)) for x in (y, q, m, w, d) if x]
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
            years += int(months // 12)
            months = int(months % 12)
        if months <= -12:
            months, years = -months, -years
            years += int(months // 12)
            months = int(months % 12)
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
        if not isinstance(other, BusinessPeriod):
            raise TypeError(
                "Can't compare since type %s is not an instance of BusinessPeriod." % other.__class__.__name__)
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

    def __bool__(self):
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
            raise TypeError("expected int but got %s" % other.__class__.__name__)

    def __rmul__(self, other):
        return self.__mul__(other)

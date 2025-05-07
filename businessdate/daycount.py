# -*- coding: utf-8 -*-

# businessdate
# ------------
# Python library for generating business dates for fast date operations
# and rich functionality.
#
# Author:   sonntagsgesicht, based on a fork of Deutsche Postbank [pbrisk]
# Version:  0.5, copyright Wednesday, 18 September 2019
# Website:  https://github.com/sonntagsgesicht/businessdate
# License:  Apache License 2.0 (see LICENSE file)


from datetime import date
from warnings import warn
from .ymd import is_leap_year


def diff_in_days(start, end):
    """ calculates days between start and end date """
    if hasattr(start, 'to_date'):
        start = start.to_date()
    if hasattr(end, 'to_date'):
        end = end.to_date()
    return float((end-start).days)


def get_30_360(start, end):
    """ implements 30/360 Day Count Convention. """
    # see QuantLib.Thirty360.USA
    start_day = min(start.day, 30)
    end_day = 30 if (start_day == 30 and end.day == 31) else end.day
    return (360 * (end.year - start.year) + 30 * (end.month - start.month) + (end_day - start_day)) / 360.0


def get_30_360b(start, end):
    """ implements 30/360 Bond Basis Count Convention. """
    # see QuantLib.Thirty360.BondBasis
    start_day = min(start.day, 30)
    end_day = 30 if (start_day == 30 and end.day == 31) else end.day
    return (360 * (end.year - start.year) + 30 * (end.month - start.month) + (end_day - start_day)) / 360.0


def get_30_360_icma(start, end):
    """ implements 30/360 ICMA Count Convention. """
    # see QuantLib.Thirty360.ISMA
    start_day = min(start.day, 30)
    end_day = 30 if (start_day == 30 and end.day == 31) else end.day
    return (360 * (end.year - start.year) + 30 * (end.month - start.month) + (end_day - start_day)) / 360.0


def get_30_360_isda(start, end):
    """ implements 30/360 ISDA Count Convention. """
    # see QuantLib.Thirty360.ISDA
    start_day = min(start.day, 30)
    if start.month == 2 and (start.day == 29 or (start.day == 28 and not is_leap_year(start.year))):
        start_day = 30

    end_day = min(end.day, 30)
    if end.month == 2  and (end.day == 29 or (end.day == 28 and not is_leap_year(end.year))):
        end_day = 30

    return (360 * (end.year - start.year) + 30 * (end.month - start.month) + (end_day - start_day)) / 360.0


def get_30_360_nasd(start, end):
    """ implements 30/360 NASD Count Convention. """
    # see QuantLib.Thirty360.NASD
    start_day = min(start.day, 30)
    end_day = 30 if (start_day == 30 and end.day == 31) else end.day
    return (360 * (end.year - start.year) +
            30 * (end.month - start.month) + (end_day - start_day)) / 360.0


def get_30e_360(start, end):
    """ implements the 30E/360 Day Count Convention. """
    # see QuantLib.Thirty360.European

    y1, m1, d1 = start.timetuple()[:3]
    # adjust to date immediately following the the last day
    y2, m2, d2 = end.timetuple()[:3]

    d1 = min(d1, 30)
    d2 = min(d2, 30)

    return (360 * (y2 - y1) + 30 * (m2 - m1) + (d2 - d1)) / 360.0


def get_30e_360b(start, end):
    """ implements the 30E/360 Bond Basis Day Count Convention. """
    # see QuantLib.Thirty360.EurobondBasis

    y1, m1, d1 = start.timetuple()[:3]
    # adjust to date immediately following the last day
    y2, m2, d2 = end.timetuple()[:3]

    d1 = min(d1, 30)
    d2 = min(d2, 30)

    return (360 * (y2 - y1) + 30 * (m2 - m1) + (d2 - d1)) / 360.0


def get_30e_360g(start, end):
    """ implements the 30E/360 German Day Count Convention. """
    # see QuantLib.Thirty360.German
    return get_30_360_isda(start, end)


def get_30e_360i(start, end):
    """ implements the 30E/360 Italian Day Count Convention. """
    # see QuantLib.Thirty360.Italian

    y1, m1, d1 = start.timetuple()[:3]
    # adjust to date immediately following the last day
    y2, m2, d2 = end.timetuple()[:3]

    if (m1 == 2 and d1 >= 28) or d1 == 31:
        d1 = 30
    if (m2 == 2 and d2 >= 28) or d2 == 31:
        d2 = 30

    return (360 * (y2 - y1) + 30 * (m2 - m1) + (d2 - d1)) / 360.0


def get_act_360(start, end):
    """ implements Act/360 day count convention. """
    return diff_in_days(start, end) / 360.0


def get_act_365(start, end):
    """ implements Act/365 day count convention. """
    return diff_in_days(start, end) / 365.0


def get_act_36525(start, end):
    """ implements Act/365.25 Day Count Convention """
    return diff_in_days(start, end) / 365.25


def get_act_act(start, end):
    """ implements Act/Act day count convention. """
    return get_act_act_isda(start, end)


def get_act_act_isda(start, end):
    """ implements Act/Act day count convention as defined by ISDA. """

    # QuantLib.ActualActual.ISDA

    # if the period does not lie within a year split the days in the period as following:
    #           remaining days of start year / years in between / days in the end year
    # REMARK: following the before mentioned Definition the first day of the period is included whereas the
    # last day will be excluded
    # What remains to check now is only whether the start and end year are leap or non-leap years. The quotients
    # can be easily calculated and for the years in between they are always one (365/365 = 1; 366/366 = 1)

    if end.year - start.year == 0:
        if is_leap_year(start.year):
            return diff_in_days(start, end) / 366.0  # leap year: 366 days
        return diff_in_days(start, end) / 365.0  # non-leap year: 365 days

    rest_year1 = diff_in_days(start, date(start.year, 12, 31)) + 1  # since the first day counts
    rest_year2 = abs(diff_in_days(end, date(end.year, 1, 1)))  # here the last day is automatically not counted
    years_in_between = end.year - start.year - 1

    return years_in_between + rest_year1 / (366.0 if is_leap_year(start.year) else 365.0) + rest_year2 / (
        366.0 if is_leap_year(end.year) else 365.0)


def get_act_act_bond(start, end):
    """ implements Act/Act day count convention known as bond basis. """
    # QuantLib.ActualActual.Bond
    return get_act_act(start, end)


class icma:

    def __init__(self, frequency = 1, rolling = None):
        """ implements ICMA day count conventions.

        :param frequency: coupon frequency. Either integer 1, 2, 4, 12 or
            string starting with 'a', 's', 'q', 'm'
            (optional: default is 1)
        :param rolling: rolling date for reference periods
            (optional: default is **None**,
            i.e. rolling date will be coupon end date )

        >>> from businessdate import BusinessDate
        >>> today = BusinessDate()
        >>> from businessdate.daycount import icma
        >>> yf = icma(2)

        >>> s, e = today, today + '12m'
        >>> yf.get_act_act(s, e)
        1.0

        >>> yf.get_30_360(s, e)
        1.0

        >>> s, e = today, today + '9m'
        >>> icma(4).get_act_act(s, e)
        0.75

        >>> icma().get_30_360(s, e)
        0.75

        """
        if isinstance(frequency, str):
            frequency = {'a': 1, 's': 2, 'q': 4, 'm': 12}.get(frequency[0])
        if frequency not in (1, 2, 4, 12):
            msg = ("frequency must be one of 1, 2, 4 or 12 or "
                   "start with 'a' 's', 'q' or 'm'")
            raise ValueError(msg)
        self.frequency = frequency
        self.rolling = rolling

    def get_act_act(self, start, end):
        def yf(s, e):
            if start <= s and e <= end:
                return 1 / self.frequency
            y = diff_in_days(max(start, s), min(end, e))
            return y / diff_in_days(s, e) / self.frequency

        from businessdate import BusinessRange, BusinessPeriod

        step = BusinessPeriod(months=12 // self.frequency)
        rolling = end if self.rolling is None else self.rolling
        r = BusinessRange(start - step, end + step, step, rolling=rolling)
        return sum(yf(s, e) for s, e in zip(r, r[1:]))

    def get_30_360(self, start, end):
        return get_30_360_icma(start, end)

    @staticmethod
    def gather_frequency(start, end):
        """gather coupon frequency from reference period

        :param start: period start date
        :param end: period end date
        :return: int in (1, 2, 4, 12)
        """
        frequency = 12 // int(round(12 * diff_in_days(start, end) / 365.0))
        if frequency not in (1, 2, 4, 12):
            frequency = 4 if frequency < 6 else 12
        return frequency


def get_act_act_icma(start, end, *, frequency=None, rolling=None):
    """ implements Act/Act day count convention as defined by ICMA/ISMA. """
    if frequency is None:
        frequency = icma.gather_frequency(start, end)
    return icma(frequency, rolling).get_act_act(start, end)


def _ql_get_act_act_icma(start, end, period_start=None, period_end=None):
    """ implements Act/Act ICMA day count convention. """
    # QuantLib.ActualActual.Old_ISMA_Impl
    if start == end:
        return 0.0
    if start > end:
        return -_ql_get_act_act_icma(end, start, period_start, period_end)

    if period_start is None:
        period_start = start
    if period_end is None:
        period_end = end

    # assert period_start < period_end

    period_days = diff_in_days(period_start, period_end)
    if period_days < 16:
        # QuantLib fallback
        period_days = diff_in_days(period_start, period_start + '1y')

    frequency = 12 // int(round(12 * period_days / 365.0))

    # shift ref period left around end
    if start < end <= period_start < period_end:
        i = 0
        while end < period_start:
            period_end = period_start
            period_start -= f"{(i + 1) * 12 // frequency}m"
            i += 1

    # shift ref period right around start
    if period_start < period_end <= start < end:
        i = 0
        while period_end < start:
            period_start = period_end
            period_end += f"{(i + 1) * 12 // frequency}m"
            i += 1

    # calc yf
    def _yf(s, e, ps, pe, f):
        y = diff_in_days(s, e) / diff_in_days(ps, pe) / f
        msg = f"QL: {s} - {e} ; {ps} - {pe} ; {f} ; {y}"
        # print(msg)
        return y

    # regular state
    if period_start <= start < end <= period_end:
        # regular state
        return _yf(start, end, period_start, period_end, frequency)

    # irregular start
    if start < period_start < end <= period_end:
        part = _yf(period_start, end, period_start, period_end, frequency)
        i = 0
        new_start = period_start
        while True:
            # new_start = period_start - f"{(i + 1) * 12 // frequency}m"
            # new_end = period_start - f"{i * 12 // frequency}m"
            # perhaps wrong but meets QuantLib
            new_end = new_start
            new_start -= f"{12 // frequency}m"
            if new_start < start:
                break
            part += 1 / frequency
            i += 1
        part += _yf(start, new_end, new_start, new_end, frequency)
        return part

    # irregular end
    if False and period_start <= start < period_end < end:
        part = _yf(start, period_end, period_start, period_end, frequency)
        i = 0
        while True:
            new_start = period_end + f"{i * 12 // frequency}m"
            new_end = period_end + f"{(i + 1) * 12 // frequency}m"
            if end < new_end:
                break
            part += 1 / frequency
            i += 1
        part += _yf(new_start, end, new_start, new_end, frequency)
        return part

    raise ValueError('wrong dates')


def _ql_get_act_act_isma(start, end, period_start=None, period_end=None):
    """ implements Act/Act ICMA day count convention. """
    # QuantLib.ActualActual.Old_ISMA_Impl
    self = _ql_get_act_act_isma
    if start == end:
        return 0.0
    if start > end:
        return - self(end, start, period_start, period_end)

    if period_start is None:
        period_start = start
    if period_end is None:
        period_end = end

    period_days = diff_in_days(period_start, period_end)
    months = int(round(12 * period_days / 365.0))
    if months == 0:
        period_start = start
        period_end = start + '1y'
        period_days = diff_in_days(period_start, period_end)
        months = 12

    period = months / 12

    if end <= period_end:
        # here period_end is a future (notional?) payment date
        if period_start <= start:
            # here period_start is the last (maybe notional)
            # payment date.
            # period_start <= start <= end <= period_end
            # [maybe the equality should be enforced, since
            # period_start < start <= end < period_end
            # could give wrong results] ???
            return period * diff_in_days(start, end) / period_days
        else:
            # here period_start is the next (maybe notional)
            # payment date and period_end is the second next
            # (maybe notional) payment date.
            # start < period_start < period_end
            # AND end <= period_end
            # this case is long first coupon

            # the last notional payment date
            previous = period_start - f"{months}m"
            if period_start < end:
                return (self(start, period_start, previous, period_start) +
                        self(period_start, end, period_start, period_end))
            else:
                return self(start, end, previous, period_start)
    else:
        # here period_end is the last (notional?) payment date
        # start < period_end < end AND period_start < period_end

        # assert period_start <= start
        # now it is: period_start <= start < period_end < end

        # the part from start to period_end
        part = self(start, period_end, period_start, period_end)

        # the part from period_end to end
        # count how many regular periods are in [period_end, end],
        # then add the remaining time
        i=0
        while True:
            new_start = period_end + f"{months * i}m"
            new_end = period_end + f"{months * (i + 1)}m"
            if end < new_end:
                break
            else:
                part += period
                i += 1
        part += self(new_start, end, new_start, new_end)
        return part


def get_act_act_euro(start, end):
    """ implements Act/Act day count convention known as euro bond. """
    # QuantLib.ActualActual.Euro
    warn("uses 'get_act_act' as fallback")
    return get_act_act(start, end)


def get_act_act_hist(start, end):
    """ implements Act/Act day count convention known as historical. """
    # QuantLib.ActualActual.Historical
    warn("uses 'get_act_act' as fallback")
    return get_act_act(start, end)


def get_act_act_365(start, end):
    """ implements Act/Act day count convention known as 365 basis. """
    # QuantLib.ActualActual.Actual365
    warn("uses 'get_act_act' as fallback")
    return get_act_act(start, end)


def get_act_act_afb(start, end):
    """ implements Act/Act day count convention as defined by AFB. """
    # QuantLib.ActualActual.AFB
    warn("uses 'get_act_act' as fallback")
    return get_act_act(start, end)


def get_simple(start, end):
    """ implements simple day count convention as defined by QuantLib. """
    """as defined in QuantLib"""
    return get_30_360(start, end)


def get_rational_period(start, end):
    """rational year fractions by ignoring days"""
    years = end.year - start.year
    months = end.month - start.month
    if months < 0:
        years -= 1
        months += 12
    days = end.day - start.day
    months += int(days / 365.25)
    return years + months / 12

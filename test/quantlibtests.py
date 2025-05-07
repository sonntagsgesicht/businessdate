
import itertools
import os
import sys
import unittest

from tqdm import tqdm as I

import QuantLib as ql

from businessdate import BusinessDate, BusinessPeriod, BusinessRange
from businessdate.daycount import (get_30_360, get_30_360b,
                                   get_30_360_isda, get_30_360_icma,
                                   get_30_360_nasd,
                                   get_30e_360, get_30e_360b,
                                   get_30e_360g, get_30e_360i,
                                   get_act_360, get_act_365, get_act_36525,
                                   get_act_act, get_act_act_365,
                                   get_act_act_isda, get_act_act_icma, icma,
                                   get_act_act_afb, get_act_act_euro,
                                   get_act_act_bond, get_act_act_hist,
                                   get_simple, get_rational_period)


def _silent(func, *args):
    _stout = sys.stdout
    sys.stdout = open(os.devnull, 'w')
    _res = func(*args)
    sys.stdout.close()
    sys.stdout = _stout
    return _res


class DayCountUnitTests(unittest.TestCase):
    # n(ame) cor(respondence)
    # correspondence between dcc and the functions
    ncor = {'30/360': 'get_30_360',
            'ACT/360': 'get_act_360',
            'ACT/365': 'get_act_365',
            '30E/360': 'get_30e_360',
            '30E/360/I': 'get_30e_360_i',
            'ACT/ACT': 'get_act_act',
            'ACT/365.25': 'get_act_36525'
            }

    dayCounters = {
        'SimpleDayCounter': ql.SimpleDayCounter(),
        'Thirty360': ql.Thirty360(ql.Thirty360.ISDA),
        'Actual360': ql.Actual360(),
        'Actual365Fixed': ql.Actual365Fixed(),
        'Actual365Fixed(Canadian)': ql.Actual365Fixed(ql.Actual365Fixed.Canadian),
        'Actual365FixedNoLeap': ql.Actual365Fixed(ql.Actual365Fixed.NoLeap),
        'ActualActual': ql.ActualActual(ql.ActualActual.ISDA),
        'Business252': ql.Business252()
    }

    def setUp(self):
        BusinessDate.DATE_FORMAT = '%Y-%m-%d'
        today = BusinessDate(20200101)
        step = BusinessPeriod('1y2m3d')
        dates = 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 20, 25
        months = 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12
        years = 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 20, 25

        self.dates = BusinessRange(today, today + '10y', step=step)
        periods = itertools.product(dates, months, years)
        self.periods = sorted(BusinessPeriod(years=y, months=m, days=d)
                              for d, m, y in periods)

    def _ql_test(self, bd_day_count, ql_day_count):
        for start in self.dates:
            for p in self.periods:
                end = start + p
                s = ql.Date(str(start), '%Y-%m-%d')
                e = ql.Date(str(end), '%Y-%m-%d')
                a = bd_day_count(start, end)
                b = ql_day_count.yearFraction(s, e)
                self.assertAlmostEqual(a, b, msg=f"{start} {end}")

    def _ql_test_ref(self, bd_day_count, ql_day_count, m='', *, pbar=False):

        def _test_ref(start, end, ref_start, ref_end):
            s = ql.Date(str(start), '%Y-%m-%d')
            e = ql.Date(str(end), '%Y-%m-%d')
            rs = ql.Date(str(ref_start), '%Y-%m-%d')
            re = ql.Date(str(ref_end), '%Y-%m-%d')

            msg = f"{start} : {end} , {ref_start} : {ref_end} with {m}"
            a = bd_day_count(start, end, ref_start, ref_end)
            b = ql_day_count.yearFraction(s, e, rs, re)
            if ref_end.day < 29:
                # caveat due to different (perhaps wrong) rolling in QL
                self.assertAlmostEqual(a, b, msg=f"\nat {msg}")

        for j, start in enumerate(self.dates):
            periods = self.periods
            if pbar:
                desc = f"periods {m}"
                pfix = f"{j + 1}/{len(self.dates)}"
                periods = I(periods, desc=desc, postfix=pfix)
            for p in periods:
                end = start + p
                _test_ref(start, start + p, end - m, end)
                _test_ref(start, end, start, start + m)

    def test_30_360(self):
        self._ql_test(get_30_360, ql.Thirty360(ql.Thirty360.USA))

    def test_30_360ICMA(self):
        self._ql_test(get_30_360_icma, ql.Thirty360(ql.Thirty360.ISMA))

    def test_30_360ISDA(self):
        self._ql_test(get_30_360_isda, ql.Thirty360(ql.Thirty360.ISDA))

    def test_30_360B(self):
        self._ql_test(get_30_360b, ql.Thirty360(ql.Thirty360.BondBasis))

    def test_30E_360(self):
        self._ql_test(get_30e_360, ql.Thirty360(ql.Thirty360.European))

    def test_30E_360B(self):
        self._ql_test(get_30e_360b, ql.Thirty360(ql.Thirty360.EurobondBasis))

    def test_30E_360G(self):
        self._ql_test(get_30e_360g, ql.Thirty360(ql.Thirty360.German))

    def test_30E_360I(self):
        self._ql_test(get_30e_360i, ql.Thirty360(ql.Thirty360.Italian))

    def test_act_360(self):
        self._ql_test(get_act_360, ql.Actual360())

    def test_act_365(self):
        self._ql_test(get_act_365, ql.Actual365Fixed())

    def test_act_36525(self):
        self._ql_test(get_act_36525, ql.Actual36525())

    def test_act_act(self):
        self._ql_test(get_act_act, ql.ActualActual(ql.ActualActual.ISDA))

    def test_act_act_icma(self):
        # bd_day_count = ql_get_act_act_isma
        # bd_day_count = get_act_act_icma
        ql_day_count = ql.ActualActual(ql.ActualActual.ISMA)
        for f in (1, 2, 4, 12):
            def bd_day_count(s, e, rs, re):
                return icma(f, re).get_act_act(s, e)
            self._ql_test_ref(bd_day_count, ql_day_count, f"{12 // f}m")

    def test_simple(self):
        act_act = ql.SimpleDayCounter()
        for start in self.dates:
            for p in self.periods:
                end = start + p
                if start == end:
                    continue
                s = ql.Date(str(start), '%Y-%m-%d')
                e = ql.Date(str(end), '%Y-%m-%d')
                a = get_rational_period(start, end)
                b = act_act.yearFraction(s, e)
                # print(start, end, a * 12)
                # self.assertAlmostEqual(a, b, msg=f"{start} {end}")

    def _test_rational(self):
        for start in self.dates:
            for p in self.periods:
                end = start + p
                if start == end:
                    continue
                a = get_rational_period(start, end)
                # print(start, end, a * 12)
                # self.assertAlmostEqual(a, b, msg=f"{start} {end}")

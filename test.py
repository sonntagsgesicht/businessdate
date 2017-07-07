# -*- coding: utf-8 -*-

#  businessdate
#  -----------
#  A fast, efficient Python library for generating business dates inherited
#  from float for fast date operations. Typical banking business methods
#  are provided like business holidays adjustment, day count fractions.
#  Beside dates generic business periods offer to create time periods like
#  '10Y', '3 Months' or '2b'. Periods can easily added to business dates.
#
#  Author:  pbrisk <pbrisk_at_github@icloud.com>
#  Website: https://github.com/pbrisk/businessdate
#  License: APACHE Version 2 License (see LICENSE file)

import os
import unittest

from datetime import datetime, date, timedelta

from businessdate.basedate import BaseDate, DAYS_IN_YEAR, from_ymd_to_excel, from_excel_to_ymd
from businessdate.businessdate import easter, target_days
from businessdate import BusinessDate, BusinessPeriod, BusinessRange, BusinessSchedule, BusinessHolidays


class BaseDateUnitTest(unittest.TestCase):
    def setUp(self):
        self.pairs = list()  # to store date(as string), exceldate[int](as string)
        f = open("test_data/excel_date_test_data.csv")
        for line in f:
            self.pairs.append(line.split(';'))
        f.close()

    def test_from_ymd_to_excel(self):
        for pair in self.pairs:
            d, m, y = [int(part) for part in pair[0].split('.')]
            i = int(pair[1])
            self.assertEqual(i, from_ymd_to_excel(y, m, d))

    def test_from_excel_to_ymd(self):
        for pair in self.pairs:
            d, m, y = [int(part) for part in pair[0].split('.')]
            i = int(pair[1])
            self.assertEqual((y, m, d), from_excel_to_ymd(i))

    def test_base_date(self):
        import businessdate
        businessdate.businessdate.BASE_DATE = '20160606'
        self.assertEqual(businessdate.BusinessDate(), businessdate.BusinessDate('20160606'))
        businessdate.businessdate.BASE_DATE = date.today()


class DayCountUnitTests(unittest.TestCase):
    # n(ame) cor(respocence)
    # correspondence between dcc and the functions
    ncor = {'30/360': 'get_30_360',
            'ACT/360': 'get_act_360',
            'ACT/365': 'get_act_365',
            '30E/360': 'get_30E_360',
            'ACT/ACT': 'get_act_act',
            'ACT/365.25': 'get_act_36525'
            }

    def setUp(self):
        self.testfile = open('test_data/daycount_test_data.csv')
        self.header = self.testfile.readline().rstrip().split(';')
        self.test_data = list()
        for line in self.testfile:
            self.test_data.append(line.rstrip().split(';'))
        self.startdate_idx = self.header.index('StartDate')
        self.enddate_idx = self.header.index('EndDate')

    def test_get_30_360(self):
        methodname = '30/360'
        method_idx = self.header.index(methodname)
        f = BusinessDate.__dict__[DayCountUnitTests.ncor[methodname]]
        for data in self.test_data:
            start_date = BusinessDate(data[self.startdate_idx])
            end_date = BusinessDate(data[self.enddate_idx])
            self.assertAlmostEqual(f(start_date, end_date), float(data[method_idx]))

    def test_get_30E_360(self):
        methodname = '30E/360'
        method_idx = self.header.index(methodname)
        f = BusinessDate.__dict__[DayCountUnitTests.ncor[methodname]]
        for data in self.test_data:
            start_date = BusinessDate(data[self.startdate_idx])
            end_date = BusinessDate(data[self.enddate_idx])
            self.assertAlmostEqual(f(start_date, end_date), float(data[method_idx]))

    def test_get_act_act(self):
        methodname = 'ACT/ACT'
        method_idx = self.header.index(methodname)
        f = BusinessDate.__dict__[DayCountUnitTests.ncor[methodname]]
        for data in self.test_data:
            start_date = BusinessDate(data[self.startdate_idx])
            end_date = BusinessDate(data[self.enddate_idx])
            self.assertAlmostEqual(f(start_date, end_date), float(data[method_idx]))

    def test_get_ACT_360(self):
        methodname = 'ACT/360'
        method_idx = self.header.index(methodname)
        f = BusinessDate.__dict__[DayCountUnitTests.ncor[methodname]]
        for data in self.test_data:
            start_date = BusinessDate(data[self.startdate_idx])
            end_date = BusinessDate(data[self.enddate_idx])
            self.assertAlmostEqual(f(start_date, end_date), float(data[method_idx]))

    def test_get_ACT_365(self):
        methodname = 'ACT/365'
        method_idx = self.header.index(methodname)
        f = BusinessDate.__dict__[DayCountUnitTests.ncor[methodname]]
        for data in self.test_data:
            start_date = BusinessDate(data[self.startdate_idx])
            end_date = BusinessDate(data[self.enddate_idx])
            self.assertAlmostEqual(f(start_date, end_date), float(data[method_idx]))

    def test_get_ACT_36525(self):
        methodname = 'ACT/365.25'
        method_idx = self.header.index(methodname)
        f = BusinessDate.__dict__[DayCountUnitTests.ncor[methodname]]
        for data in self.test_data:
            start_date = BusinessDate(data[self.startdate_idx])
            end_date = BusinessDate(data[self.enddate_idx])
            self.assertAlmostEqual(f(start_date, end_date), float(data[method_idx]))


class BusinessHolidaysUnitTests(unittest.TestCase):
    def setUp(self):
        self.holidays = BusinessHolidays()
        self.easter = dict()
        self.easter[2015] = date(2015, 04, 05)
        self.easter[2016] = date(2016, 03, 27)
        self.easter[2017] = date(2017, 04, 16)
        self.easter[2018] = date(2018, 04, 01)
        self.easter[2019] = date(2019, 04, 21)
        self.easter[2020] = date(2020, 04, 12)
        self.target = dict()
        for y in self.easter:
            self.target[y] = [date(y, 01, 01), date(y, 05, 01), date(y, 12, 25), date(y, 12, 26)]
            self.target[y].append(self.easter[y] - timedelta(2))
            self.target[y].append(self.easter[y] + timedelta(1))

    def test_easter(self):
        for y in self.easter:
            self.assertEqual(easter(y), self.easter[y])

    def test_target_days(self):
        for y in self.target:
            t = target_days(y)
            d = date(y, 01, 01) - timedelta(1)
            while d < date(y + 1, 01, 01):
                if d in self.target[y]:
                    self.assertTrue(d in t)
                else:
                    self.assertTrue(d not in t)
                d += timedelta(1)

    def test_business_holidays(self):
        self.assertTrue(date(2016, 01, 01) in self.holidays)
        self.assertFalse(date(2016, 01, 02) in self.holidays)
        self.assertTrue(date(2016, 01, 02) not in self.holidays)
        self.assertTrue(date(2016, 03, 25) in self.holidays)
        self.assertTrue(date(2016, 03, 28) in self.holidays)
        self.assertTrue(date(2016, 05, 01) in self.holidays)


class BusinessDateUnitTests(unittest.TestCase):
    def setUp(self):
        self.dec31 = BusinessDate(20151231)
        self.jan01 = BusinessDate(20160101)
        self.jan02 = BusinessDate(20160102)
        self.jan04 = BusinessDate(20160104)
        self.jan29 = BusinessDate(20160129)
        self.jan31 = BusinessDate(20160131)
        self.feb01 = BusinessDate(20160201)
        self.feb28 = BusinessDate(20160228)
        self.feb29 = BusinessDate(20160229)
        self.mar31 = BusinessDate(20160331)
        self.jun30 = BusinessDate(20160630)
        self.sep30 = BusinessDate(20160930)

        self.dates = [self.dec31, self.jan01, self.jan02, self.jan04, self.jan29, self.jan31,
                      self.feb01, self.feb28, self.feb29, self.mar31, self.jun30, self.sep30]

    def test_constructors(self):
        self.assertEqual(BusinessDate(date.today()), BusinessDate())
        self.assertEqual(self.jan02, BusinessDate('2016-01-02'))
        self.assertEqual(self.jan02, BusinessDate('01/02/2016'))
        self.assertEqual(self.jan02, BusinessDate('02.01.2016'))
        self.assertEqual(self.jan02, BusinessDate(42371))
        self.assertEqual(self.jan02, BusinessDate(42371.0))
        self.assertEqual(self.jan02, BusinessDate(735965))
        self.assertEqual(self.jan02, BusinessDate(735965.0))
        self.assertEqual([self.jan01, self.jan02], BusinessDate([20160101, 42371]))

    def test_to_string(self):
        self.assertEqual(self.jan02.to_string(), '20160102')
        self.assertEqual(BusinessDate(42371).to_string(), '20160102')

    def test_properties(self):
        self.assertEqual(self.jan01.day, 01)
        self.assertEqual(self.jan01.month, 01)
        self.assertEqual(self.jan01.year, 2016)

    def test_operators(self):
        self.assertEqual(self.jan01 + '2D', self.jan02 + '1D')
        self.assertEqual(self.jan01 - '1D', self.jan02 - '2D')
        self.assertEqual(self.jan02 - '1D' + '1M', self.feb01)
        self.assertRaises(TypeError, lambda: '1D' + self.jan02)
        self.assertEqual(self.jan01 - BusinessPeriod('1D'), self.jan02 - '2D')
        self.assertRaises(TypeError, lambda: BusinessPeriod('1D') + self.jan02)
        self.assertRaises(TypeError, lambda: BusinessPeriod('1D') - self.jan01)
        self.assertEqual(self.dec31.add_period(BusinessPeriod('2B', BusinessHolidays())),
                         self.dec31.add_period(BusinessPeriod('2B'), BusinessHolidays([self.jan02])))

    def test_validations(self):
        self.assertTrue(BusinessDate.is_businessdate(18991229))
        self.assertTrue(BusinessDate.is_businessdate(20160131))
        self.assertTrue(BusinessDate.is_businessdate(20160228))
        self.assertTrue(BusinessDate.is_businessdate(20160229))
        self.assertFalse(BusinessDate.is_businessdate(20160230))
        self.assertFalse(BusinessDate.is_businessdate(20160231))
        self.assertTrue(BusinessDate.is_businessdate(20150228))
        self.assertFalse(BusinessDate.is_businessdate(20150229))
        self.assertFalse(BusinessDate.is_businessdate('xyz'))
        self.assertFalse(BusinessDate.is_businessdate(-125))
        self.assertFalse(BusinessDate.is_businessdate(-20150228))

    def test_calculations(self):
        self.assertEqual(self.jan01.add_days(1), self.jan02)
        self.assertEqual(self.jan01.add_months(1), self.feb01)
        self.assertEqual(self.jan01.add_years(1).to_string(), '20170101')
        self.assertEqual(self.jan01.add_period('2D'), self.jan02 + BusinessPeriod('1D'))
        self.assertEqual(self.jan02.add_period('-2D'), self.jan01 - BusinessPeriod('1D'))
        self.assertEqual(self.jan02.add_period('-1b'), self.jan01 - BusinessPeriod('1b'))
        self.assertNotEqual(BusinessDate(20160630).add_period(BusinessPeriod('2B')),
                            BusinessDate(20160630).add_period(BusinessPeriod('2B', BusinessHolidays(['20160704']))))
        self.assertEqual(self.jan01 + '1b', self.jan02 + '1b')

    def test_cast_to(self):
        self.assertTrue(isinstance(self.jan01.to_date(), date))
        self.assertTrue(isinstance(self.jan01.to_businessdate(), BusinessDate))
        self.assertTrue(isinstance(self.jan01.to_businessperiod(), BusinessPeriod))
        self.assertTrue(isinstance(self.jan01.to_excel(), int))
        self.assertTrue(isinstance(self.jan01.to_ordinal(), int))
        self.assertTrue(isinstance(self.jan01.to_string(), str))
        self.assertTrue(isinstance(self.jan01.to_ymd(), tuple))

    def test_cast_from(self):
        for d in self.dates:
            self.assertEqual(BusinessDate.from_date(d.to_date()), d)
            self.assertEqual(BusinessDate.from_businessdate(d), d)
            self.assertEqual(BusinessDate.from_excel(d.to_excel()), d)
            self.assertEqual(BusinessDate.from_ordinal(d.to_ordinal()), d)
            self.assertEqual(BusinessDate.from_string(d.to_string()), d)
            self.assertEqual(BusinessDate.from_ymd(*d.to_ymd()), d)

    def test_day_count(self):  # The daycount methods are also tested separately
        delta = float((self.mar31.to_date() - self.jan01.to_date()).days)
        total = float(((self.jan01 + '1y').to_date() - self.jan01.to_date()).days)
        self.assertAlmostEqual(self.jan01.get_30_360(self.mar31), 90. / 360.)
        self.assertAlmostEqual(self.jan01.get_act_360(self.mar31), delta / 360.)
        self.assertAlmostEqual(self.jan01.get_act_365(self.mar31), delta / 365.)
        self.assertAlmostEqual(self.jan01.get_act_36525(self.mar31), delta / 365.25)
        self.assertAlmostEqual(self.jan01.get_act_act(self.mar31), delta / total)

    def test_business_day_adjustment(self):
        self.assertEqual(self.jan01.adjust_follow(), BusinessDate(20160104))
        self.assertEqual(self.jan01.adjust_mod_follow(), BusinessDate(20160104))
        self.assertEqual(self.jan01.adjust_previous(), BusinessDate(20151231))
        self.assertEqual(self.jan01.adjust_mod_previous(), BusinessDate(20160104))
        self.assertEqual(self.jan01.adjust_start_of_month(), BusinessDate(20160104))
        self.assertEqual(self.jan01.adjust_end_of_month(), BusinessDate(20160129))
        self.assertEqual(self.jan01.adjust_imm(), BusinessDate(20160115))
        self.assertEqual(self.jan01.adjust_cds_imm(), BusinessDate(20160120))

    def test_business_day_is(self):
        self.assertFalse(self.jan01.is_business_day())
        self.assertTrue(BusinessDate.is_leap_year(2016))
        self.assertTrue(BusinessDate.is_businessdate('20160101'))
        self.assertFalse(BusinessDate.is_businessdate('ABC'))
        self.assertFalse(BusinessDate.is_businessdate('20160230'))
        self.assertTrue(BusinessDate.is_businessdate('20160229'))
        self.assertFalse(BusinessDate.is_businessdate('20150229'))


class BusinessPeriodUnitTests(unittest.TestCase):
    def setUp(self):
        self._1y = BusinessPeriod('1y')
        self._3m = BusinessPeriod('1m')
        self._1y6m = BusinessPeriod('1y6m')
        self._1b = BusinessPeriod('1b')
        self._2y = BusinessPeriod('2y')
        self._3y = BusinessPeriod('3y')
        self._5y = BusinessPeriod('5y')
        self._2q = BusinessPeriod('2q')
        self._2w = BusinessPeriod('2w')

    def test_constructors(self):
        self.assertEqual(self._1y, BusinessPeriod(years=1))
        self.assertEqual(self._1y6m, BusinessPeriod(years=1, months=6))
        self.assertEqual(self._1y6m, BusinessPeriod('6m', years=1))
        self.assertEqual(-1 * self._1y6m, BusinessPeriod('-6m', years=-1))
        self.assertEqual(self._2q, BusinessPeriod(months=6))

    def test_properties(self):
        self.assertEqual(self._1y.years, 1)
        self.assertEqual(self._1y.months, 0)
        self.assertEqual(self._1y.days, 0)
        self.assertEqual(-1 * self._1y.years, -1)
        self.assertEqual(-1 * self._1y.days, 0)
        self.assertEqual(self._1b.businessdays, 1)

    def test_operators(self):
        self.assertEqual(self._2y.__cmp__(BusinessPeriod('10Y')), 2922.0)
        self.assertNotEqual(self._2y, self._5y)
        self.assertEqual(BusinessPeriod('5y'), self._5y)

    def test_validations(self):
        self.assertTrue(BusinessPeriod.is_businessperiod('1y'))
        self.assertTrue(BusinessPeriod.is_businessperiod('-1y'))
        self.assertFalse(BusinessPeriod.is_businessperiod('1y-6m'))

    def test_calculations(self):
        self.assertEqual(self._2y + self._3y, self._5y)
        self.assertEqual(self._1y + '6m', self._1y6m)
        self.assertRaises(TypeError, lambda: '6m' + self._1y)

    def test_cast(self):
        self.assertEqual(BusinessPeriod.from_string('1y'), BusinessPeriod(years=1))
        self.assertEqual(self._1y.to_businessdate(BusinessDate(20150101)), BusinessDate(20160101))
        self.assertEqual(self._1y6m.to_businessdate(BusinessDate(20150101)), BusinessDate(20160701))
        self.assertEqual(self._1y.to_businessdate(BusinessDate(20160229)), BusinessDate(20170228))
        self.assertEqual(self._1y.to_date(BusinessDate(20160229)), date(2017, 02, 28))
        self.assertEqual(self._1y.to_businessperiod(BusinessDate(20160229)), self._1y)
        self.assertEqual(self._1y.to_string(), '1Y')
        self.assertEqual(self._2q.to_string(), '6M')
        self.assertEqual(self._2w.to_string(), '14D')


class BusinessRangeUnitTests(unittest.TestCase):
    def setUp(self):
        self.sd = BusinessDate(20151231)
        self.ed = BusinessDate(20201231)

    def test_constructors(self):
        br = BusinessRange(self.sd, self.ed)
        self.assertEqual(len(br), 5)
        self.assertEqual(br[0], self.sd)
        self.assertEqual(br[-1], BusinessDate.add_years(self.ed, -1))

        br = BusinessRange(self.sd, self.ed)
        b2 = BusinessRange(self.sd, self.ed, '1y', self.ed)
        ck = BusinessRange(self.sd, self.ed, '1y', self.sd)
        ex = BusinessRange(self.sd, self.ed, '1y', self.ed + '1y')
        sx = BusinessRange(self.sd, self.ed, '1y', self.sd - '1y')
        self.assertEqual(br, b2)
        self.assertEqual(b2, ck)
        self.assertEqual(ck, ex)
        self.assertEqual(ex, sx)


class BusinessScheduleUnitTests(unittest.TestCase):
    def setUp(self):
        self.sd = BusinessDate(20151231)
        self.ed = BusinessDate(20201231)
        self.pr = BusinessPeriod('1y')

    def test_constructors(self):
        bs = BusinessSchedule(self.sd, self.ed, self.pr)
        ck = BusinessSchedule(self.sd, self.ed, self.pr, self.ed)
        for b, c in zip(bs, ck):
            self.assertEqual(b, BusinessDate(c))
        self.assertEqual(len(bs), 6)
        self.assertEqual(bs[0], self.sd)
        self.assertEqual(bs[-1], self.ed)

        bs = BusinessSchedule(20150331, 20160930, '3M', 20160415)
        ck = BusinessDate([20150331, 20150415, 20150715, 20151015, 20160115, 20160415, 20160715, 20160930])
        self.assertEqual(bs, ck)

        bs.adjust()
        ck = BusinessDate([20150331, 20150415, 20150715, 20151015, 20160115, 20160415, 20160715, 20160930])
        self.assertEqual(bs, ck)

        bs = BusinessSchedule(20150101, 20170101, '3M', 20170101)
        ck = BusinessDate([20150101, 20150401, 20150701, 20151001, 20160101, 20160401, 20160701, 20161001, 20170101])
        self.assertEqual(bs, ck)

    def test_methods(self):
        bs = BusinessSchedule(20150331, 20160930, '3M', 20160415).first_stub_long()
        ck = BusinessDate([20150331, 20150715, 20151015, 20160115, 20160415, 20160715, 20160930])
        self.assertEqual(bs, ck)

        bs.last_stub_long()
        ck = BusinessDate([20150331, 20150715, 20151015, 20160115, 20160415, 20160930])
        self.assertEqual(bs, ck)


class BusinessHolidayUnitTests(unittest.TestCase):
    def setUp(self):
        self.bd = BusinessDate(19730226)
        self.list = [str(i) + '0301' for i in range(1973, 2016)]

    def test_holiday(self):
        h = BusinessHolidays(self.list)
        for l in self.list:
            self.assertTrue(BusinessDate(l) in h)
        self.assertNotEqual(self.bd.add_period('3b', h), self.bd.add_period('3b'))


class OldDateUnitTests(unittest.TestCase):
    def test__diff(self):
        d1 = BusinessDate.from_ymd(2016, 1, 31)
        d2 = BusinessDate.from_ymd(2017, 11, 1)

        diff = BusinessDate.diff(d1, d2)
        diff = BusinessPeriod(years=diff[0], months=diff[1], days=diff[2])
        self.assertEqual('1Y9M1D', diff.to_string())

        d1 = BusinessDate.from_ymd(2016, 2, 29)
        d2 = BusinessDate.from_ymd(2017, 3, 1)

        diff = BusinessDate.diff(d1, d2)
        diff = BusinessPeriod(years=diff[0], months=diff[1], days=diff[2])
        self.assertEqual('1Y1D', diff.to_string())

        d2 = BusinessDate.from_ymd(2017, 2, 28)

        diff = BusinessDate.diff(d1, d2)
        diff = BusinessPeriod(years=diff[0], months=diff[1], days=diff[2])
        self.assertEqual('1Y', diff.to_string())

        d1 = BusinessDate.from_ymd(2016, 11, 15)
        d2 = BusinessDate.from_ymd(2017, 1, 15)

        diff = BusinessDate.diff(d1, d2)
        diff = BusinessPeriod(years=diff[0], months=diff[1], days=diff[2])
        self.assertEqual('2M', diff.to_string())

        d1 = BusinessDate.from_ymd(2015, 7, 31)
        d2 = BusinessDate.from_ymd(2017, 2, 20)

        diff = BusinessDate.diff(d1, d2)
        diff = BusinessPeriod(years=diff[0], months=diff[1], days=diff[2])
        self.assertEqual('1Y6M20D', diff.to_string())


class OldBusinessDateUnitTests(unittest.TestCase):
    """tests the date class """

    def test_type(self):
        s = BusinessDate('20011110')
        e = BusinessDate('20011112')
        self.assertEqual(type(e), type(s))
        self.assertTrue(isinstance(s, BaseDate))

    def test_diff_in_years(self):
        s = BusinessDate('20011110')
        e = BusinessDate('20011112')
        self.assertEqual(BusinessDate.diff_in_years(s, e), 2 / DAYS_IN_YEAR)
        self.assertEqual(BusinessDate.diff_in_years(BusinessDate('20161101'),
                                                    BusinessDate('20171102')), 366 / DAYS_IN_YEAR)

    def test_diff_in_days(self):
        s = BusinessDate('20011110')
        e = BusinessDate('20011112')
        self.assertEqual(BusinessDate.diff_in_days(s, e), 2)

    def test_add(self):
        s = BusinessDate('20011110')
        e = BusinessDate('20011112')
        self.assertEqual(BusinessDate.add_days(s, e.day), BusinessDate('20011122'))
        self.assertEqual(BusinessDate.add_months(s, 1), BusinessDate('20011210'))
        self.assertEqual(BusinessDate.add_years(s, 1), BusinessDate('20021110'))

    def test_diff(self):
        s = BusinessDate('20160101')
        self.assertEqual(BusinessDate.diff_in_days(s, BusinessDate('20160102')), BusinessPeriod(days=1).days)

    def test_bdc(self):
        self.assertEqual(BusinessDate.adjust_mod_follow(BusinessDate('20160312')), BusinessDate('20160314'))
        self.assertEqual(BusinessDate.is_business_day(BusinessDate('20160312')), False)

    def test_dcc(self):
        self.assertEqual(BusinessDate.get_act_36525(BusinessDate('20170101'),
                                                    BusinessDate('20180101')), 365.0 / 365.25)

    def test_holidays(self):
        self.assertEqual(BusinessDate.is_business_day(BusinessDate('20170101')), False)


class OldBusinessPeriodUnittests(unittest.TestCase):
    def test_add(self):
        p = BusinessPeriod(years=1, months=2, days=3)
        self.assertRaises(TypeError, lambda: p + 2)
        p = BusinessPeriod(years=1, months=2, days=3)
        self.assertEqual(p.add_months(1), BusinessPeriod(years=1, months=3, days=3))
        self.assertEqual(p.add_years(10), BusinessPeriod(years=11, months=3, days=3))

    def test_to_date(self):
        p = BusinessPeriod(years=1, months=2, days=3)
        self.assertEqual(p.to_businessdate(BusinessDate('20160101')), BusinessDate('20170304'))

    def test_wrapper_methods(self):
        p = BusinessPeriod(years=1, months=1, days=1)
        self.assertEqual(p.add_years(p.years).add_months(p.months).add_days(p.days),
                         BusinessPeriod(years=2, months=2, days=2))
        self.assertEqual(p * 2, BusinessPeriod(years=4, months=4, days=4))
        self.assertEqual(BusinessDate.add_period(BusinessDate('20160110'), BusinessPeriod(days=-1)),
                         BusinessDate('20160109'))


if __name__ == "__main__":

    import sys
    start_time = datetime.now()

    print('')
    print('======================================================================')
    print('')
    print('run %s' % __file__)
    print('in %s' % os.getcwd())
    print('started  at %s' % str(start_time))
    print('')
    print('----------------------------------------------------------------------')
    print('')

    suite = unittest.TestLoader().loadTestsFromModule(__import__("__main__"))
    testrunner = unittest.TextTestRunner(stream=sys.stdout , descriptions=2, verbosity=2)
    testrunner.run(suite)

    print('')
    print('======================================================================')
    print('')
    print('ran %s' % __file__)
    print('in %s' % os.getcwd())
    print('started  at %s' % str(start_time))
    print('finished at %s' % str(datetime.now()))
    print('')
    print('----------------------------------------------------------------------')
    print('')

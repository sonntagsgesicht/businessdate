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
import sys
import unittest

from datetime import datetime, date, timedelta

from businessdate import BusinessDate, BusinessPeriod, BusinessRange, BusinessSchedule, BusinessHolidays

from businessdate.holidays import easter, target_days
from businessdate.basedate import BaseDateFloat, BaseDateDatetimeDate
from businessdate.ymd import from_ymd_to_excel, from_excel_to_ymd, \
    is_valid_ymd, end_of_quarter_month, days_in_month, \
    days_in_year, is_leap_year


def _silent(func, *args):
    _stout = sys.stdout
    sys.stdout = open(os.devnull, 'w')
    _res = func(*args)
    sys.stdout = _stout
    return _res


class BaseDateUnitTest(unittest.TestCase):
    def setUp(self):
        self.pairs = list()  # to store date(as string), exceldate[int](as string)
        f = open("test_data/excel_date_test_data.csv")
        for line in f:
            dmy, i = line.strip().split(';', 1)
            d, m, y = dmy.split('.', 2)
            ymd = int(y), int(m), int(d)
            self.pairs.append((ymd, int(i)))
        f.close()
        self.invalid = (2019, 13, 1), (2019, 11, 31), (2019, 12, -1), (2019, -12, 1), (1800, 13, 1)

    def test_ymd(self):
        for ymd in self.invalid:
            y, m, d = ymd
            self.assertFalse(is_valid_ymd(*ymd))
            self.assertRaises(ValueError, from_ymd_to_excel, y, m, d)

        for ymd, f in self.pairs:
            y, m, d = ymd
            self.assertTrue(is_valid_ymd(*ymd))

            leap = y % 4 == 0 and (not y % 100 == 0 or y == 2000)
            self.assertEqual(leap, is_leap_year(y))
            self.assertEqual(366 if leap else 365, days_in_year(y))

            self.assertEqual(f, from_ymd_to_excel(*ymd))
            self.assertEqual(ymd, from_excel_to_ymd(f))

            quarter = m if m % 3 == 0 else m + 3 - m % 3
            self.assertEqual(quarter, end_of_quarter_month(m))

            days = 30 if m in (4, 6, 9, 11) else 31 if m is not 2 else 29 if leap else 28
            self.assertEqual(days, days_in_month(y, m))

    def test_base_date_float(self):
        for ymd, f in self.pairs:
            bd = BaseDateFloat(f)

            self.assertEqual(f, bd)

            self.assertEqual(ymd, (bd.year, bd.month, bd.day))

            self.assertEqual(bd, BaseDateFloat.from_float(f))
            self.assertEqual(f, bd.to_float())

            self.assertEqual(f, BaseDateFloat.from_ymd(*ymd))
            self.assertEqual(ymd, bd.to_ymd())

            self.assertEqual(f, BaseDateFloat.from_date(date(*ymd)))
            self.assertEqual(date(*ymd), bd.to_date())

            a, b = bd, BaseDateFloat(f + 1)
            self.assertEqual(b, a._add_days(1))
            self.assertEqual(a, b._add_days(-1))

            self.assertTrue(bd._add_days(0)._ymd is None)

            y, m, d = ymd
            self.assertEqual(d, bd._add_days(0).day)
            self.assertEqual(m, bd._add_days(0).month)
            self.assertEqual(y, bd._add_days(0).year)

            self.assertEqual(1, a._diff_in_days(b))
            self.assertEqual(-1, b._diff_in_days(a))

            self.assertEqual(5, BaseDateFloat.from_ymd(2016, 12, 31).weekday())

    def test_base_date_datetime(self):
        for ymd, f in self.pairs:
            bd = BaseDateDatetimeDate(*ymd)

            self.assertEqual(date(*ymd), bd)

            self.assertEqual(ymd, (bd.year, bd.month, bd.day))

            self.assertEqual(bd, BaseDateDatetimeDate.from_float(f))
            self.assertEqual(f, bd.to_float())

            self.assertEqual(bd, BaseDateDatetimeDate.from_ymd(*ymd))
            self.assertEqual(ymd, bd.to_ymd())

            self.assertEqual(bd, BaseDateDatetimeDate.from_date(date(*ymd)))
            self.assertEqual(date(*ymd), bd.to_date())

            a, b = bd, BaseDateDatetimeDate.from_date(date(*ymd) + timedelta(1))
            self.assertEqual(b, a._add_days(1))
            self.assertEqual(a, b._add_days(-1))
            self.assertEqual(1, a._diff_in_days(b))
            self.assertEqual(-1, b._diff_in_days(a))

            self.assertEqual(5, BaseDateFloat.from_ymd(2016, 12, 31).weekday())


class DayCountUnitTests(unittest.TestCase):
    # n(ame) cor(respondence)
    # correspondence between dcc and the functions
    ncor = {'30/360': 'get_30_360',
            'ACT/360': 'get_act_360',
            'ACT/365': 'get_act_365',
            '30E/360': 'get_30e_360',
            '30E/360/ISDA': 'get_30e_360_isda',
            'ACT/ACT': 'get_act_act',
            'ACT/365.25': 'get_act_36525'
            }

    def setUp(self):
        testfile = open('test_data/daycount_test_data.csv')

        header = testfile.readline().rstrip().split(';')

        start = header.index('StartDate')
        header.pop(start)
        period = header.index('Period')
        header.pop(period)
        end = header.index('EndDate')
        header.pop(end)

        self.test_data = list()
        for line in testfile:
            data = line.rstrip().split(';')
            start_date = BusinessDate(data.pop(start))
            _ = BusinessPeriod(data.pop(period))
            end_date = BusinessDate(data.pop(end))
            daycount = dict(zip(header, data))
            self.test_data.append((start_date, end_date, daycount))

    def test_day_count(self):
        for start, end, daycount in self.test_data:
            for k, v in daycount.items():
                self.assertAlmostEquals(float(v), start.get_day_count(end, DayCountUnitTests.ncor[k].lstrip('get_')))


class BusinessHolidaysUnitTests(unittest.TestCase):
    def setUp(self):
        self.holidays = BusinessHolidays(target_days(2016))
        self.easter = dict()
        self.easter[2015] = date(2015, 4, 5)
        self.easter[2016] = date(2016, 3, 27)
        self.easter[2017] = date(2017, 4, 16)
        self.easter[2018] = date(2018, 4, 1)
        self.easter[2019] = date(2019, 4, 21)
        self.easter[2020] = date(2020, 4, 12)
        self.target = dict()
        for y in self.easter:
            self.target[y] = [date(y, 1, 1), date(y, 5, 1), date(y, 12, 25), date(y, 12, 26)]
            self.target[y].append(self.easter[y] - timedelta(2))
            self.target[y].append(self.easter[y] + timedelta(1))

    def test_easter(self):
        for y in self.easter:
            self.assertEqual(easter(y), self.easter[y])

    def test_target_days(self):
        for y in self.target:
            t = target_days(y)
            d = date(y, 1, 1) - timedelta(1)
            while d < date(y + 1, 1, 1):
                if d in self.target[y]:
                    self.assertTrue(d in t)
                else:
                    self.assertTrue(d not in t)
                d += timedelta(1)

    def test_business_holidays(self):
        self.assertTrue(BusinessDate(20160101).to_date() in self.holidays)
        self.assertFalse(BusinessDate(20160102).to_date() in self.holidays)
        self.assertTrue(BusinessDate(20160102).to_date() not in self.holidays)
        self.assertTrue(BusinessDate(20160325).to_date() in self.holidays)
        self.assertTrue(BusinessDate(20160328).to_date() in self.holidays)
        self.assertTrue(BusinessDate(20160501).to_date() in self.holidays)


class BusinessDateUnitTests(unittest.TestCase):
    def setUp(self):
        self.jan29_15 = BusinessDate(20150129)
        self.feb28_15 = BusinessDate(20150228)
        self.dec31_15 = BusinessDate(20151231)
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

        self.dates = [self.jan29_15, self.feb28_15, self.dec31_15,
                      self.jan01, self.jan02, self.jan04, self.jan29, self.jan31,
                      self.feb01, self.feb28, self.feb29, self.mar31, self.jun30, self.sep30]

    def test_base_date(self):
        BusinessDate.BASE_DATE = '20160606'
        self.assertEqual(BusinessDate(), BusinessDate('20160606'))
        BusinessDate.BASE_DATE = date.today()

    def test_parse(self):
        self.assertRaises(ValueError, BusinessDate._parse_date_string, 'sdfasd')
        self.assertRaises(ValueError, BusinessDate, 'rtzwrwetzwe')

    def test_constructors(self):
        self.assertEqual(BusinessDate(date.today()), BusinessDate())
        self.assertEqual(self.jan02, BusinessDate('2016-01-02'))
        self.assertEqual(self.jan02, BusinessDate('01/02/2016'))
        self.assertEqual(self.jan02, BusinessDate('02.01.2016'))
        self.assertEqual(self.jan02, BusinessDate(42371))
        self.assertEqual(self.jan02, BusinessDate(42371.0))
        self.assertEqual([self.jan01, self.jan02], BusinessDate([20160101, 42371]))

    def test_to_string(self):
        self.assertEqual(self.jan02, BusinessDate(str(self.jan02)))
        self.assertEqual(str(self.jan02), '20160102')
        self.assertEqual(repr(self.jan02), "BusinessDate('20160102')")
        self.assertEqual(str(BusinessDate(42371)), '20160102')
        self.assertEqual(self.jan02, eval(repr(self.jan02)))

    def test_properties(self):
        self.assertEqual(self.jan01.day, 1)
        self.assertEqual(self.jan01.month, 1)
        self.assertEqual(self.jan01.year, 2016)

    def test_operators(self):
        self.assertEqual(self.jan01 + '2D', self.jan02 + '1D')
        self.assertEqual(self.jan01 - '1D', self.jan02 - '2D')
        self.assertEqual(self.jan02 - '1D' + '1M', self.feb01)
        self.assertRaises(TypeError, lambda: '1D' + self.jan02)
        self.assertEqual(self.jan01 - BusinessPeriod('1D'), self.jan02 - '2D')
        self.assertRaises(TypeError, lambda: BusinessPeriod('1D') + self.jan02)
        self.assertRaises(TypeError, lambda: BusinessPeriod('1D') - self.jan01)
        self.assertEqual(self.dec31_15.add_period(BusinessPeriod('2B'), BusinessHolidays()),
                         self.dec31_15.add_period(BusinessPeriod('2B'), BusinessHolidays([self.jan02])))

        d = BusinessDate(20160229)
        self.assertEqual(d + '1y' + '1m', BusinessDate(20170328))
        self.assertEqual(d + '1m' + '1y', BusinessDate(20170329))
        self.assertEqual(d + '1y1m', BusinessDate(20170329))

        self.assertEqual(d + ['1y', '1m'], [BusinessDate(20170228), BusinessDate(20160329)])
        self.assertEqual(d - ['-1y', '-1m'], [BusinessDate(20170228), BusinessDate(20160329)])

    def test_validations(self):
        # self.assertTrue(BusinessDate.is_businessdate(18991229))
        self.assertTrue(BusinessDate.is_businessdate(19000102))
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

        self.assertEqual(365, BusinessDate(20150101).days_in_year())
        self.assertEqual(366, BusinessDate(20160101).days_in_year())
        self.assertEqual(366, BusinessDate(20000101).days_in_year())

        self.assertEqual(31, BusinessDate(20150101).days_in_month())
        self.assertEqual(31, BusinessDate(20160101).days_in_month())
        self.assertEqual(31, BusinessDate(20000101).days_in_month())

        self.assertEqual(28, BusinessDate(20150201).days_in_month())
        self.assertEqual(29, BusinessDate(20160201).days_in_month())
        self.assertEqual(29, BusinessDate(20000201).days_in_month())

        self.assertEqual(BusinessDate(20150131), BusinessDate(20150101).end_of_month())
        self.assertEqual(BusinessDate(20160229), BusinessDate(20160201).end_of_month())
        self.assertEqual(BusinessDate(20000331), BusinessDate(20000311).end_of_month())

        self.assertEqual(BusinessDate(20150331), BusinessDate(20150101).end_of_quarter())
        self.assertEqual(BusinessDate(20160331), BusinessDate(20160201).end_of_quarter())
        self.assertEqual(BusinessDate(20000331), BusinessDate(20000311).end_of_quarter())

        self.assertTrue(BusinessDate(19000102).is_business_day())
        self.assertFalse(BusinessDate(20160101).is_business_day())
        self.assertFalse(BusinessDate(20160131).is_business_day())
        self.assertFalse(BusinessDate(20160228).is_business_day())
        self.assertTrue(BusinessDate(20160324).is_business_day())
        self.assertFalse(BusinessDate(20160325).is_business_day())
        self.assertFalse(BusinessDate(20160326).is_business_day())
        self.assertFalse(BusinessDate(20160327).is_business_day())
        self.assertFalse(BusinessDate(20160328).is_business_day())
        self.assertTrue(BusinessDate(20160329).is_business_day())
        self.assertTrue(BusinessDate(20160330).is_business_day())
        self.assertFalse(BusinessDate(20160501).is_business_day())

    def test_calculations(self):
        self.assertEqual(self.jan01._add_days(1), self.jan02)
        self.assertEqual(self.jan01._add_months(1), self.feb01)
        self.assertEqual(str(self.jan01._add_years(1)), '20170101')
        self.assertEqual(self.jan01.add_period('2D'), self.jan02 + BusinessPeriod('1D'))
        self.assertEqual(self.jan02.add_period('-2D'), self.jan01 - BusinessPeriod('1D'))
        self.assertEqual(self.jan02.add_period('-1b'), self.jan01 - BusinessPeriod('1b'))
        #        self.assertNotEqual(BusinessDate(20160630).add_period(BusinessPeriod('2B')),
        #                            BusinessDate(20160630).add_period(BusinessPeriod('2B'), BusinessHolidays(['20160704'])))
        self.assertNotEqual(BusinessDate(20160630).add_period(BusinessPeriod('2B')),
                            BusinessDate(20160630).add_period(BusinessPeriod('2B'),
                                                              BusinessHolidays(BusinessDate(['20160704']))))
        n = 111
        a, b = BusinessDate(), BusinessDate() + BusinessPeriod(days=n)
        self.assertEqual(n, a._diff_in_days(b))
        self.assertEqual(-n, b._diff_in_days(a))

        a, b = BusinessDate(), BusinessDate() + BusinessPeriod(years=1, months=27, days=46)
        self.assertEqual(1234, a._diff_in_days(b))
        self.assertEqual(-1234, b._diff_in_days(a))

        self.assertRaises(TypeError, BusinessDate().__add__, 'rtzwrwetzwe')
        self.assertRaises(TypeError, BusinessDate().__sub__, 'rtzwrwetzwe')
        self.assertEqual(self.jan01 + '1b', self.jan02 + '1b')

        d, p = BusinessDate('20160229'), BusinessPeriod('1Y1M1D')
        self.assertEqual((d + p - d), p, (d + p - d, d, p, d + p))
        d, p = BusinessDate('20150129'), BusinessPeriod('1Y2M1D')
        self.assertEqual((d + p - d), p, (d + p - d, d, p, d + p))
        d, p = BusinessDate('20150129'), BusinessPeriod('1Y1M1D')
        self.assertEqual((d + p - d), p, (d + p - d, d, p, d + p))
        # non idepotent pairs
        d, p = BusinessDate('20150129'), BusinessPeriod('1M29D')
        # self.assertEqual((d + p - d), p, (d + p - d, d, p, d + p))
        d, p = BusinessDate('20160129'), BusinessPeriod('1M29D')
        # self.assertEqual((d + p - d), p, (d + p - d, d, p, d + p))

    def test_more_calculations(self):

        periods = list()
        for y in range(5):
            for m in range(13):
                for d in list(range(5)) + list(range(25, 33)) + list(range(58, 66)):
                    periods.append(BusinessPeriod(str(y) + 'y' + str(m) + 'm' + str(d) + 'd'))

        for d in self.dates:
            for p in periods:
                dp = d + p
                q = dp - d
                dq = d + q
                if p.days < 28:
                    self.assertEqual(q, p, (q, d, p, dp))
                elif p.days < 59 and not 28 <= p.days - q.days <= 32:  # and not q == p:
                    self.assertEqual(q, p, (q, d, p, dp))
                    # print(d, p, dp, q)
                # elif 59 <= p.days and not 28 <= p.days - q.days <= 32 and not q == p:
                #     print d, p, dp, q
                # only idempotent pairs work always (e.g. above)
                self.assertEqual(dq, dp, (dq, d, p, dp, q))
                self.assertEqual((dq - d), q, (dq - d, d, q, dq))

        a = BusinessDate('20150228')
        for y in range(3):
            for m in range(0, 7, 5):
                for d in range(0, 13, 5):
                    b = a + BusinessPeriod(years=y, months=m, days=d)
                    self.assertEqual(-b._diff_in_days(a), a._diff_in_days(b))

    def test_cast_to(self):
        self.assertTrue(isinstance(self.jan01.to_date(), date))
        self.assertTrue(isinstance(self.jan01, BusinessDate))
        self.assertTrue(isinstance(self.jan01 - BusinessDate(), BusinessPeriod))
        self.assertTrue(isinstance(self.jan01.to_float(), int))
        # removed ordinal support
        # self.assertTrue(isinstance(self.jan01.to_ordinal(), int))
        self.assertTrue(isinstance(str(self.jan01), str))
        self.assertTrue(isinstance(self.jan01.to_ymd(), tuple))

    def test_cast_from(self):
        for d in self.dates:
            self.assertEqual(BusinessDate(d.to_date()), d)
            self.assertEqual(d.__copy__(), d)
            self.assertEqual(BusinessDate(d.to_float()), d)
            self.assertEqual(BusinessDate(str(d)), d)
            self.assertEqual(BusinessDate(*d.to_ymd()), d)

    def test_day_count(self):  # The daycount methods are also tested separately
        delta = float((self.mar31.to_date() - self.jan01.to_date()).days)
        total = float(((self.jan01 + '1y').to_date() - self.jan01.to_date()).days)

        self.assertAlmostEqual(_silent(self.jan01.get_day_count, self.mar31), delta / 365.25)
        self.assertAlmostEqual(self.jan01.get_day_count(self.mar31, 'ACT_36525'), delta / 365.25)
        self.assertAlmostEqual(self.jan01.get_day_count(self.mar31, '30_360'), 90. / 360.)
        self.assertAlmostEqual(self.jan01.get_day_count(self.mar31, 'ACT_ACT'), delta / total)
        self.assertAlmostEqual(self.jan01.get_day_count(self.mar31, 'ACTACT'), delta / total)

        self.assertAlmostEqual(self.jan01.get_day_count(self.mar31, '30_360'), 90. / 360.)
        self.assertAlmostEqual(self.jan01.get_day_count(self.mar31, '30e_360'), 0.24722222)
        self.assertAlmostEqual(self.jan01.get_day_count(self.mar31, '30e_360_isda'), 0.247222222)
        self.assertAlmostEqual(self.jan01.get_day_count(self.mar31, 'act_360'), delta / 360.)
        self.assertAlmostEqual(self.jan01.get_day_count(self.mar31, 'act_365'), delta / 365.)
        self.assertAlmostEqual(self.jan01.get_day_count(self.mar31, 'act_36525'), delta / 365.25)
        self.assertAlmostEqual(self.jan01.get_day_count(self.mar31, 'act_act'), delta / total)

    def test_business_day_adjustment(self):
        self.assertEqual(_silent(self.jan01.adjust), BusinessDate(20160101))
        self.assertEqual(_silent(self.jan01.adjust,''), BusinessDate(20160101))
        self.assertEqual(self.jan01.adjust('NO'), BusinessDate(20160101))
        # self.assertEqual(no(self.jan01.to_date(), BusinessDate.DEFAULT_HOLIDAYS), BusinessDate(20160101).to_date())

        self.assertEqual(self.jan01.adjust('FOLLOW'), BusinessDate(20160104))
        self.assertEqual(self.jan01.adjust('FLW'), BusinessDate(20160104))
        # self.assertEqual(follow(self.jan01.to_date(), BusinessDate.DEFAULT_HOLIDAYS), BusinessDate(20160104).to_date())

        self.assertEqual(self.jan01.adjust('mod_follow'), BusinessDate(20160104))
        self.assertEqual(self.jan01.adjust('modflw'), BusinessDate(20160104))
        # self.assertEqual(modfollow(self.jan01.to_date(), BusinessDate.DEFAULT_HOLIDAYS),
        #                 BusinessDate(20160104).to_date())

        self.assertEqual(self.jan01.adjust('previous'), BusinessDate(20151231))
        self.assertEqual(self.jan01.adjust('prev'), BusinessDate(20151231))
        self.assertEqual(self.jan01.adjust('prv'), BusinessDate(20151231))
        # self.assertEqual(previous(self.jan01.to_date(), BusinessDate.DEFAULT_HOLIDAYS),
        #                 BusinessDate(20151231).to_date())

        self.assertEqual(self.jan01.adjust('mod_previous'), BusinessDate(20160104))
        self.assertEqual(self.jan01.adjust('modprev'), BusinessDate(20160104))
        self.assertEqual(self.jan01.adjust('modprv'), BusinessDate(20160104))
        # self.assertEqual(modprevious(self.jan01.to_date(), BusinessDate.DEFAULT_HOLIDAYS),
        #                 BusinessDate(20160104).to_date())

        self.assertEqual(self.jan01.adjust('start_of_month'), BusinessDate(20160104))
        self.assertEqual(self.jan01.adjust('som'), BusinessDate(20160104))
        # self.assertEqual(modprevious(self.jan01.to_date(), BusinessDate.DEFAULT_HOLIDAYS),
        #                 BusinessDate(20160104).to_date())

        self.assertEqual(self.jan01.adjust('end_of_month'), BusinessDate(20160129))
        self.assertEqual(self.jan01.adjust('eom'), BusinessDate(20160129))
        # self.assertEqual(modprevious(self.jan01.to_date(), BusinessDate.DEFAULT_HOLIDAYS),
        #                 BusinessDate(20160104).to_date())

        self.assertEqual(self.jan01.adjust('imm'), BusinessDate(20160315))
        self.assertEqual(BusinessDate(20160601).adjust('imm'), BusinessDate(20160616))
        # self.assertEqual(imm(self.jan01.to_date(), BusinessDate.DEFAULT_HOLIDAYS), BusinessDate(20160315).to_date())

        self.assertEqual(self.jan01.adjust('cds_imm'), BusinessDate(20160320))
        self.assertEqual(self.jan01.adjust('cds'), BusinessDate(20160320))

    def test_business_day_is(self):
        self.assertFalse(self.jan01.is_business_day())
        self.assertTrue(BusinessDate(2016, 1, 1).is_leap_year())
        self.assertTrue(BusinessDate.is_businessdate('20160101'))
        self.assertFalse(BusinessDate.is_businessdate('ABC'))
        self.assertFalse(BusinessDate.is_businessdate('20160230'))
        self.assertTrue(BusinessDate.is_businessdate('20160229'))
        self.assertFalse(BusinessDate.is_businessdate('20150229'))

    def test_is_business_date(self):
        d = self.dec31_15
        holi = BusinessHolidays()
        bdate = BusinessDate.from_ymd(2016, 1, 1)
        is_bday_empty_calendar = bdate.is_business_day(holi)
        self.assertTrue(is_bday_empty_calendar)
        is_bday_default_calendar = bdate.is_business_day()
        self.assertFalse(is_bday_default_calendar)

        target_a = BusinessDate.from_ymd(2016, 1, 4)
        a = d._add_business_days(2, holi)
        self.assertEqual(target_a, a)
        target_b = BusinessDate.from_ymd(2016, 1, 5)
        b = d._add_business_days(2)  # default holidays contains the target days, i.e. the 1.1.2016
        self.assertEqual(target_b, b)

    def test_from_businesperiod_str(self):
        self.assertEqual(BusinessDate() + '1B', BusinessDate('1B'))
        self.assertEqual(BusinessDate() + '1w', BusinessDate('1w'))
        self.assertEqual(BusinessDate().adjust('mod_follow'),
                         BusinessDate('0BMODFLW'))
        self.assertEqual(BusinessDate('20171231').adjust('mod_follow'),
                         BusinessDate('0BMODFLW20171231'))
        self.assertEqual(BusinessDate('20171231').adjust('mod_follow') + '3D',
                         BusinessDate('0B3DMODFOLLOW20171231'))
        self.assertRaises(ValueError, BusinessDate, '0X3D')
        self.assertEqual((BusinessDate('20171231').adjust('mod_follow') + '3D').adjust('mod_follow'),
                         BusinessDate('0B3D0BMODFOLLOW20171231'))
        self.assertEqual(BusinessDate('20171231') + '1w', BusinessDate('1w20171231'))
        self.assertEqual((BusinessDate('20171231').adjust('previous') + '3D').adjust('previous'),
                         BusinessDate('0B3D0BPREV20171231'))
        self.assertEqual((BusinessDate('20171231').adjust('previous') + '3D').adjust('previous'),
                         BusinessDate('0B3D0BPREVIOUS20171231'))
        self.assertEqual((BusinessDate('20171231').adjust('mod_follow') + '3D').adjust('mod_follow'),
                         BusinessDate('0B3D0BMODFOLLOW20171231'))
        self.assertEqual((BusinessDate('20171231').adjust('mod_follow') + '3D').adjust('mod_follow'),
                         BusinessDate('0B3D0BMODFLW20171231'))


class BusinessPeriodUnitTests(unittest.TestCase):
    def setUp(self):
        self._1b = BusinessPeriod('1b')
        self._1y = BusinessPeriod('1y')
        self._3m = BusinessPeriod('3m')
        self._1y6m = BusinessPeriod('1y6m')
        self._1b = BusinessPeriod('1b')
        self._2y = BusinessPeriod('2y')
        self._3y = BusinessPeriod('3y')
        self._5y = BusinessPeriod('5y')
        self._2q = BusinessPeriod('2q')
        self._2w = BusinessPeriod('2w')

    def test_parse(self):
        f = lambda x: '%sb%sy%sq%sm%sw%sd%sb' % tuple(x)
        d = lambda x: tuple(map(int, x))
        for p in ('1000000', '0100000', '0010000', '0001000', '0000100', '0000010', '0000001'):
            self.assertEquals(d(p), BusinessPeriod._parse_ymd(f(p)))
        for p in ('1000001', '0100001', '1010001', '1101011', '0110100', '0010010', '1111111'):
            self.assertEquals(d(p), BusinessPeriod._parse_ymd(f(p)))

    def test_constructors(self):
        self.assertEqual(self._1y, BusinessPeriod(years=1))
        self.assertEqual(self._1y6m, BusinessPeriod(years=1, months=6))
        # self.assertEqual(self._1y6m, BusinessPeriod('6m', years=1))
        self.assertEqual(self._1y6m, BusinessPeriod('18m'))
        # self.assertEqual(-1 * self._1y6m, BusinessPeriod('-6m', years=-1))
        self.assertEqual(self._2q, BusinessPeriod(months=6))
        self.assertEqual(BusinessPeriod(timedelta(100)), BusinessPeriod(days=100))
        self.assertEqual(BusinessPeriod('0D'), BusinessPeriod())
        self.assertEqual(BusinessPeriod('ON'), BusinessPeriod(businessdays=1))
        self.assertEqual(BusinessPeriod('TN'), BusinessPeriod(businessdays=2))
        self.assertEqual(BusinessPeriod('DD'), BusinessPeriod(businessdays=3))
        self.assertEqual(BusinessPeriod('-1M'), BusinessPeriod(months=-1))
        self.assertEqual(BusinessPeriod('-12M'), BusinessPeriod(years=-1))
        self.assertEqual(BusinessPeriod('-18M'), BusinessPeriod(years=-1, months=-6))
        self.assertEqual(BusinessPeriod(months=-18), BusinessPeriod(years=-1, months=-6))

        self.assertRaises(ValueError, BusinessPeriod, '6m', years=1)
        self.assertRaises(ValueError, BusinessPeriod, 'XSDW')
        self.assertRaises(ValueError, BusinessPeriod, '2DW')
        self.assertRaises(ValueError, BusinessPeriod, '2B2D')
        # self.assertRaises(ValueError, BusinessPeriod, '2D0B')
        self.assertRaises(ValueError, BusinessPeriod, '2D1B')
        self.assertRaises(ValueError, BusinessPeriod, '1B2D1B')
        self.assertRaises(ValueError, BusinessPeriod, '1Y-2W1D')
        self.assertRaises(ValueError, BusinessPeriod, years=-1, months=1)

    def test_properties(self):
        self.assertEqual(self._1y.years, 1)
        self.assertEqual(self._1y.months, 0)
        self.assertEqual(self._1y.days, 0)
        self.assertEqual(-1 * self._1y.years, -1)
        self.assertEqual(-1 * self._1y.days, 0)
        self.assertEqual(self._1b.businessdays, 1)

    def test_operators(self):
        self.assertFalse(BusinessPeriod('0D'))
        self.assertTrue(BusinessPeriod('1D'))
        self.assertNotEqual(BusinessPeriod("3M"), BusinessPeriod("1M"))
        self.assertNotEqual(BusinessPeriod("31D"), BusinessPeriod("1M"))
        self.assertEqual(BusinessPeriod("3M"), BusinessPeriod("1M") + "2m")
        self.assertEqual(BusinessPeriod("1Y"), BusinessPeriod("12M"))
        self.assertEqual(BusinessPeriod("1Y"), BusinessPeriod("12M0D"))
        self.assertTrue(self._2y < '10Y')
        self.assertTrue(self._2y < BusinessPeriod('10Y'))
        self.assertTrue(self._2y < BusinessPeriod('1m') * 12 * 2 + '1d')
        self.assertFalse(self._3y < BusinessPeriod('1Y'))
        self.assertEqual(self._2y.__cmp__(BusinessPeriod('10Y')), -2976.0)
        self.assertNotEqual(self._2y, self._5y)
        self.assertEqual(BusinessPeriod('5y'), self._5y)

        abs(BusinessPeriod('-2d'))
        self.assertEqual(BusinessPeriod('5y2q3w1d'), -1 * BusinessPeriod('-5y2q3w1d'))
        self.assertEqual(BusinessPeriod('5y2q3w1d'), abs(BusinessPeriod('-5y2q3w1d')))
        self.assertEqual(BusinessPeriod('1b'), -1 * BusinessPeriod('-1b'))
        self.assertEqual(BusinessPeriod('1b'), abs(BusinessPeriod('-1b')))

        self.assertEqual(BusinessPeriod() + ['1d', '2d'], [BusinessPeriod('1d'), BusinessPeriod('2d')])
        self.assertEqual(BusinessPeriod() - ['-1d', '-2d'], [BusinessPeriod('1d'), BusinessPeriod('2d')])
        self.assertEqual(BusinessPeriod('3y2m1d') * 2, BusinessPeriod('6y4m2d'))
        self.assertEqual(BusinessPeriod('1d') * (2, 1), [BusinessPeriod('2d'), BusinessPeriod('1d')])

        self.assertRaises(TypeError, BusinessPeriod('1d').__mul__, '2')

    def test_validations(self):
        for p in ('', '0D', 'ON', 'TN', 'DD'):
            self.assertTrue(BusinessPeriod.is_businessperiod(p))
        self.assertTrue(BusinessPeriod.is_businessperiod(timedelta(1)))
        self.assertTrue(BusinessPeriod.is_businessperiod(BusinessPeriod('1D')))
        self.assertTrue(BusinessPeriod.is_businessperiod('1y'))
        self.assertTrue(BusinessPeriod.is_businessperiod('1y'))
        self.assertTrue(BusinessPeriod.is_businessperiod('1y'))
        self.assertTrue(BusinessPeriod.is_businessperiod('1y'))
        self.assertTrue(BusinessPeriod.is_businessperiod('-1y'))
        self.assertTrue(BusinessPeriod.is_businessperiod('1y-6m'))
        self.assertTrue(BusinessPeriod.is_businessperiod('-2b1y6m'))
        self.assertTrue(BusinessPeriod.is_businessperiod('-2b-1y6m'))
        self.assertTrue(BusinessPeriod.is_businessperiod('-2b-1y6m-2b'))

        self.assertFalse(BusinessPeriod.is_businessperiod(None))
        self.assertFalse(BusinessPeriod.is_businessperiod('123'))
        self.assertFalse(BusinessPeriod.is_businessperiod(123))
        self.assertFalse(BusinessPeriod.is_businessperiod(True))
        self.assertFalse(BusinessPeriod.is_businessperiod('2D3D'))

        self.assertRaises(TypeError, BusinessPeriod().__cmp__, None)
        self.assertRaises(TypeError, BusinessPeriod().__cmp__, 123)
        self.assertFalse(BusinessPeriod() == '2D3D')

        self.assertTrue(BusinessPeriod() <= BusinessPeriod('3D'))
        self.assertFalse(BusinessPeriod('6D') <= BusinessPeriod('3D'))

        self.assertTrue(BusinessPeriod() < BusinessPeriod('3D'))
        self.assertFalse(BusinessPeriod('6D') < BusinessPeriod('3D'))

        self.assertFalse(BusinessPeriod() >= BusinessPeriod('3D'))
        self.assertTrue(BusinessPeriod('6D') >= BusinessPeriod('3D'))

        self.assertFalse(BusinessPeriod() > BusinessPeriod('3D'))
        self.assertTrue(BusinessPeriod('6D') > BusinessPeriod('3D'))

    def test_calculations(self):
        self.assertEqual(self._2y + self._3y, self._5y)
        self.assertEqual(self._1y + '6m', self._1y6m)
        self.assertEqual(self._1y, BusinessPeriod('1y'))
        self.assertRaises(TypeError, lambda: '6m' + self._1y)
        self.assertEqual(self._1y, self._3y - self._2y)
        self.assertEqual(self._1y, self._3y - '2y')

    def test_cast(self):
        self.assertEqual(BusinessPeriod('1y'), BusinessPeriod(years=1))
        self.assertEqual(BusinessDate(20150101) + self._1y, BusinessDate(20160101))
        self.assertEqual(BusinessDate(20150101) + self._1y6m, BusinessDate(20160701))
        self.assertEqual(BusinessDate(20160229) + self._1y, BusinessDate(20170228))

        self.assertEqual((BusinessDate(20160229) + self._1y).to_date(), date(2017, 2, 28))
        self.assertEqual(BusinessDate(20160229) + self._1y - BusinessDate(20160229), self._1y)

        self.assertEqual(str(self._1b), '1B')
        self.assertEqual(str(self._1y), '1Y')
        self.assertEqual(str(self._2q), '6M')
        self.assertEqual(str(self._2w), '14D')
        self.assertEqual(str(BusinessPeriod('-1y6m')), '-1Y6M')
        self.assertEqual(str(BusinessPeriod('1y6m')), '1Y6M')
        self.assertEqual(str(BusinessPeriod('16m')), '1Y4M')
        self.assertEqual(str(BusinessPeriod('')), '0D')

        self.assertEqual(repr(self._2w), "BusinessPeriod('14D')")
        self.assertEqual(self._1y, eval(repr(self._1y)))

        self.assertNotEqual(hash(BusinessPeriod('3D')), hash(BusinessPeriod('3W')))
        self.assertNotEqual(hash(BusinessPeriod('3D')), hash(BusinessPeriod('1D')))
        self.assertNotEqual(hash(BusinessPeriod('3D')), hash(BusinessPeriod('3B')))


class BusinessRangeUnitTests(unittest.TestCase):
    def setUp(self):
        self.sd = BusinessDate(20151231)
        self.ed = BusinessDate(20201231)

    def test_constructors(self):
        br = BusinessRange(self.sd, self.ed)
        self.assertEqual(len(br), 5)
        self.assertEqual(br[0], self.sd)
        self.assertEqual(br[-1], BusinessDate._add_years(self.ed, -1))

        br = BusinessRange(self.sd, self.ed)
        b2 = BusinessRange(self.sd, self.ed, '1y', self.ed)
        ck = BusinessRange(self.sd, self.ed, '1y', self.sd)
        ex = BusinessRange(self.sd, self.ed, '1y', self.ed + '1y')
        sx = BusinessRange(self.sd, self.ed, '1y', self.sd - '1y')
        self.assertEqual(br, b2)
        self.assertEqual(b2, ck)
        self.assertEqual(ck, ex)
        self.assertEqual(ex, sx)

        bs = BusinessRange(20151231, 20160630, '1M', 20151231)
        ck = BusinessDate([20151231, 20160131, 20160229, 20160331, 20160430, 20160531])
        self.assertEqual(bs, ck)

        bs = BusinessRange(20151231, 20160531, '1M', 20151231)
        ck = BusinessRange(20151231, 20160531, '1M', 20160531)
        self.assertEqual(bs, ck)

        bs = BusinessRange(20151231, 20160531, '1M', 20151231)
        ck = BusinessRange(20151231, 20160531, '-1M', 20151231)
        self.assertEqual(bs, ck)

        BusinessDate.BASE_DATE = 20151231
        bs = BusinessRange(20201231)
        ck = [BusinessDate('20151231'),
              BusinessDate('20161231'),
              BusinessDate('20171231'),
              BusinessDate('20181231'),
              BusinessDate('20191231')]
        self.assertEqual(bs, ck)

    def test_adjust(self):
        bs = BusinessRange(20201231)
        for k, v in BusinessDate._adj_func.items():
            self.assertEquals(bs.adjust(k), BusinessDate(list(map(v, bs))))
        BusinessDate.BASE_DATE = date.today()


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

        _silent(bs.adjust)
        ck = BusinessDate([20150331, 20150415, 20150715, 20151015, 20160115, 20160415, 20160715, 20160930])
        self.assertEqual(bs, ck)

        bs.adjust('imm')
        ck = BusinessDate([20150315, 20150615, 20150915, 20151215, 20160315, 20160616, 20160915, 20160915])
        self.assertEqual(bs, ck)

        bs = BusinessSchedule(20150101, 20170101, '3M', 20170101)
        ck = BusinessDate([20150101, 20150401, 20150701, 20151001, 20160101, 20160401, 20160701, 20161001, 20170101])
        self.assertEqual(bs, ck)

        bs = BusinessSchedule(20151231, 20160630, '1M', 20151231)
        ck = BusinessDate([20151231, 20160131, 20160229, 20160331, 20160430, 20160531, 20160630])
        self.assertEqual(bs, ck)

        bs = BusinessSchedule(20151231, 20160630, '1M', 20151231)
        ck = BusinessSchedule(20151231, 20160630, '-1M', 20151231)
        self.assertEqual(bs, ck)

        bs = BusinessSchedule(20151231, 20160630, '1M', 20151231)
        ck = BusinessSchedule(20151231, 20160630, '-1M', 20160331)
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
        self.list = list(map(BusinessDate, [str(i) + '0301' for i in range(1973, 2016)]))

    def test_holiday(self):
        h = BusinessHolidays(self.list)
        for l in self.list:
            self.assertTrue(BusinessDate(l) in h)
            self.assertTrue(BusinessDate(l).to_date() in h)
        self.assertNotEqual(self.bd.add_period('3b', h), self.bd.add_period('3b'))


class OldDateUnitTests(unittest.TestCase):
    def test__diff(self):
        d1 = BusinessDate.from_ymd(2016, 1, 31)
        d2 = BusinessDate.from_ymd(2017, 11, 1)

        y, m, d = BusinessDate.diff_in_ymd(d2, d1)
        diff = BusinessPeriod(years=y, months=m, days=d)
        self.assertEqual('1Y9M1D', str(diff))

        d1 = BusinessDate.from_ymd(2016, 2, 29)
        d2 = BusinessDate.from_ymd(2017, 3, 1)

        y, m, d = BusinessDate.diff_in_ymd(d2, d1)
        diff = BusinessPeriod(years=y, months=m, days=d)
        self.assertEqual('1Y1D', str(diff))

        d2 = BusinessDate.from_ymd(2017, 2, 28)

        y, m, d = BusinessDate.diff_in_ymd(d2, d1)
        diff = BusinessPeriod(years=y, months=m, days=d)
        self.assertEqual('1Y', str(diff))

        d1 = BusinessDate.from_ymd(2016, 11, 15)
        d2 = BusinessDate.from_ymd(2017, 1, 15)

        y, m, d = BusinessDate.diff_in_ymd(d2, d1)
        diff = BusinessPeriod(years=y, months=m, days=d)
        self.assertEqual('2M', str(diff))

        d1 = BusinessDate.from_ymd(2015, 7, 31)
        d2 = BusinessDate.from_ymd(2017, 2, 20)

        y, m, d = BusinessDate.diff_in_ymd(d2, d1)
        diff = BusinessPeriod(years=y, months=m, days=d)
        self.assertEqual('1Y6M20D', str(diff))


class OldBusinessDateUnitTests(unittest.TestCase):
    """tests the date class """

    def test_type(self):
        s = BusinessDate('20011110')
        e = BusinessDate('20011112')
        self.assertEqual(type(e), type(s))

    def test_diff_in_years(self):
        s = BusinessDate('20011110')
        e = BusinessDate('20011112')
        # removed diff_in_years
        # self.assertEqual(BusinessDate.diff_in_years(s, e), 2 / BusinessDate.DAYS_IN_YEAR)
        # self.assertEqual(BusinessDate.diff_in_years(BusinessDate('20161101'),
        #                                             BusinessDate('20171102')), 366 / BusinessDate.DAYS_IN_YEAR)

    def test_diff_in_days(self):
        s = BusinessDate('20011110')
        e = BusinessDate('20011112')
        self.assertEqual(BusinessDate._diff_in_days(s, e), 2)

    def test_add(self):
        s = BusinessDate('20011110')
        e = BusinessDate('20011112')
        self.assertEqual(BusinessDate._add_days(s, e.day), BusinessDate('20011122'))
        self.assertEqual(BusinessDate._add_months(s, 1), BusinessDate('20011210'))
        self.assertEqual(BusinessDate._add_years(s, 1), BusinessDate('20021110'))

    def test_diff(self):
        s = BusinessDate('20160101')
        self.assertEqual(BusinessDate._diff_in_days(s, BusinessDate('20160102')), BusinessPeriod(days=1).days)

    def test_bdc(self):
        self.assertEqual(BusinessDate.adjust(BusinessDate('20160312'), 'mod_follow'), BusinessDate('20160314'))
        self.assertEqual(BusinessDate.is_business_day(BusinessDate('20160312')), False)

    def test_dcc(self):
        self.assertEqual(
            BusinessDate.get_day_count(BusinessDate('20170101'), BusinessDate('20180101'), 'act_36525'),
            365.0 / 365.25)

    def test_holidays(self):
        self.assertEqual(BusinessDate.is_business_day(BusinessDate('20170101')), False)


class OldBusinessPeriodUnittests(unittest.TestCase):
    def test_add(self):
        p = BusinessPeriod(years=1, months=2, days=3)
        self.assertRaises(TypeError, lambda: p + 2)
        p = BusinessPeriod(years=1, months=2, days=3)
        self.assertEqual(p + '1M', BusinessPeriod(years=1, months=3, days=3))
        self.assertEqual(p + '10Y', BusinessPeriod(years=11, months=2, days=3))

    def test_to_date(self):
        p = BusinessPeriod(years=1, months=2, days=3)
        self.assertEqual(BusinessDate('20160101') + p, BusinessDate('20170304'))

    def test_wrapper_methods(self):
        p = BusinessPeriod(years=1, months=1, days=1)
        self.assertEqual(p + '%sY' % (p.years) + '%sM' % (p.months) + '%sD' % (p.days),
                         BusinessPeriod(years=2, months=2, days=2))
        self.assertEqual(p * 4, BusinessPeriod(years=4, months=4, days=4))
        self.assertEqual(BusinessDate('20160110').add_period(BusinessPeriod(days=-1)), BusinessDate('20160109'))
        self.assertEqual(BusinessDate('20160110') + BusinessPeriod(days=-1), BusinessDate('20160109'))


if __name__ == "__main__":
    import sys

    start_time = datetime.now()

    print('')
    print('======================================================================')
    print('')
    print(('run %s' % __file__))
    print(('in %s' % os.getcwd()))
    print(('started  at %s' % str(start_time)))
    print('')
    print('----------------------------------------------------------------------')
    print('')

    suite = unittest.TestLoader().loadTestsFromModule(__import__("__main__"))
    testrunner = unittest.TextTestRunner(stream=sys.stdout, descriptions=2, verbosity=2)
    testrunner.run(suite)

    print('')
    print('======================================================================')
    print('')
    print(('ran %s' % __file__))
    print(('in %s' % os.getcwd()))
    print(('started  at %s' % str(start_time)))
    print(('finished at %s' % str(datetime.now())))
    print('')
    print('----------------------------------------------------------------------')
    print('')

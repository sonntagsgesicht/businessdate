
.. currentmodule:: businessdate

To start with |businessdate| import it.
Note that, since we work with dates, **datetime.date** might be useful, too.
But not required. Nevertheless **datetime.date** is used inside |BusinessDate| from time to time.

.. paste this into python console to generate code block contents
   from datetime import date
   from businessdate import BusinessDate, BusinessPeriod, BusinessRange, BusinessSchedule

.. testsetup::

    from datetime import date, timedelta
    from businessdate import BusinessDate, BusinessPeriod, BusinessRange, BusinessSchedule

.. doctest::

    >>> from datetime import date, timedelta
    >>> from businessdate import BusinessDate, BusinessPeriod, BusinessRange, BusinessSchedule


Creating Objects
================

BusinessDate
------------

Once the library is loaded, creating business dates as simple as this.

.. paste this into python console to generate code block contents
   BusinessDate(year=2014, month=1, day=11)
   BusinessDate(date(2014,1,11))
   BusinessDate(20140111)
   BusinessDate('20140111')
   BusinessDate('2015-12-31')
   BusinessDate('31.12.2015')
   BusinessDate('12/31/2015')
   BusinessDate(42369)
   BusinessDate(20140101) + BusinessPeriod('1Y3M')
   BusinessDate(20140101) + '1Y3M'
   BusinessDate(20170101) - '1Y1D'
   BusinessDate() == BusinessDate(date.today())
   BusinessDate('1Y3M20140101')

.. doctest::

    >>> BusinessDate(year=2014, month=1, day=11)
    BusinessDate(20140111)

    >>> BusinessDate(date(2014,1,11))
    BusinessDate(20140111)

    >>> BusinessDate(20140111)
    BusinessDate(20140111)

    >>> BusinessDate('20140111')
    BusinessDate(20140111)

    >>> BusinessDate('2015-12-31')
    BusinessDate(20151231)

    >>> BusinessDate('31.12.2015')
    BusinessDate(20151231)

    >>> BusinessDate('12/31/2015')
    BusinessDate(20151231)

    >>> BusinessDate(42369) # number of days since January, 1st 1900
    BusinessDate(20151231)

Even iterators like :class:`list` or :class:`tuple` work well.

.. paste this into python console to generate code block contents
   BusinessDate((20140216, 23011230, 19991111, 20200202))

.. doctest::

    >>> BusinessDate((20140216, 23011230, 19991111, 20200202))
    (BusinessDate(20140216), BusinessDate(23011230), BusinessDate(19991111), BusinessDate(20200202))

Much easier to generate container with periodical items is using |BusinessRange|.

By default an empty |BusinessDate()|
is initiated with the system date as given by *+datetime.date.today()**.
To change this behavior: just set the *classattribute*
|BusinessDate.BASE_DATE| to anything that can be understood as a
business date, i.e. anything that meets |Businessdate.is_businessdate()|.

.. paste this into python console to generate code block contents
   from datetime import date
   from businessdate import BusinessDate
   BusinessDate.BASE_DATE = '20110314'
   BusinessDate()
   BusinessDate.BASE_DATE = None
   BusinessDate().to_date() == date.today()

.. doctest::

   >>> BusinessDate.BASE_DATE = '20110314'
   >>> BusinessDate()
   BusinessDate(20110314)

   >>> BusinessDate.BASE_DATE = None
   >>> BusinessDate().to_date() == date.today()
   True

.. attention::

   Setting |BusinessDate.BASE_DATE| to
   *+datetime.date.today()** is different to setting to **None**
   since *+datetime.date.today()** changes at midnight!


BusinessPeriod
--------------

There are two different categories of periods which can't be mixed.

One classical, given by a number of
`years`, `month`, and `days`.

The second is `business days` or also known as working days,
which are neither weekend days nor holidays.
Holidays as seen as a container (e.g. `list` or `tuple`) of `
:class:`datetime.date` which are understood as holidays.

Explicit keyword arguments of can be used to init an instance.

.. paste this into python console to generate code block contents
   from datetime import date, timedelta
   from businessdate import BusinessDate, BusinessPeriod
   BusinessPeriod(businessdays=10)
   BusinessPeriod(years=2, months=6, days=1)
   BusinessPeriod(years=1, months=6)
   BusinessPeriod(months=18)
   BusinessPeriod(months=1, days=45)
   BusinessPeriod(months=2, days=14)
   BusinessPeriod(months=2, days=15)
   BusinessPeriod(businessdays=1, days=1)

.. doctest::

   >>> BusinessPeriod()
   BusinessPeriod('0D')

   >>> BusinessPeriod(businessdays=10)
   BusinessPeriod('10B')

   >>> BusinessPeriod(years=2, months=6, days=1)
   BusinessPeriod('2Y6M1D')

   >>> BusinessPeriod(months=18)
   BusinessPeriod('1Y6M')

   >>> BusinessPeriod(years=1, months=6)
   BusinessPeriod('1Y6M')


As seen `month` greater than 12 will be reduced to
less or equal to 12 month with according years.

.. doctest::

   >>> BusinessPeriod(months=18)
   BusinessPeriod('1Y6M')

   >>> BusinessPeriod(years=2, months=6, days=1)
   BusinessPeriod('2Y6M1D')

But this cannot be performed for days.

.. doctest::

   >>> BusinessPeriod(months=1, days=45)
   BusinessPeriod('1M45D')

   >>> BusinessPeriod(months=2, days=14)
   BusinessPeriod('2M14D')

   >>> BusinessPeriod(months=2, days=15)
   BusinessPeriod('2M15D')


.. caution::

   As mentioned, classical period input arguments `years`, `month` and `days`
   must not be combined with `businessdays`.

      >>> BusinessPeriod(businessdays=1, days=1)
      Traceback (most recent call last):
        File "<stdin>", line 1, in <module>
        File "/Users/jph/Dropbox/Apps/GitHub/sonntagsgesicht/businessdate/businessdate/businessperiod.py", line 103, in __init__
          raise ValueError("Either (years,months,days) or businessdays must be zero for %s" % self.__class__.__name__)
      ValueError: Either (years,months,days) or businessdays must be zero for BusinessPeriod

Moreover, the difference of two instances of **datetime.date*+ or resp.
a **datetime.timedelta** instance can be used to init, too.

.. paste this into python console to generate code block contents
   from datetime import date, timedelta
   from businessdate import BusinessDate, BusinessPeriod
   a, b = date(2010,6,1), date(2010,12,31)
   b-a
   BusinessPeriod(b-a)
   timedelta(213)
   BusinessPeriod(timedelta(213))

.. doctest::

   >>> june_the_first, december_the_thirty_first = date(2010,6,1), date(2010,12,31)
   >>> december_the_thirty_first-june_the_first
   datetime.timedelta(days=213)

   >>> BusinessPeriod(december_the_thirty_first-june_the_first)
   BusinessPeriod('213D')

   >>> timedelta(213)
   datetime.timedelta(days=213)

   >>> BusinessPeriod(timedelta(213))
   BusinessPeriod('213D')


Similar to |BusinessDate| convenient string input work as well.
Such a string represents again either periods of business days
or classical periods.

.. paste this into python console to generate code block contents
   from datetime import date, timedelta
   from businessdate import BusinessDate, BusinessPeriod
   BusinessPeriod('0b')
   BusinessPeriod('10D')
   BusinessPeriod('1y3m4d')
   BusinessPeriod('18M')
   BusinessPeriod('1Q')
   BusinessPeriod('2w')
   BusinessPeriod('10B')

.. doctest::

   >>> BusinessPeriod('0b')
   BusinessPeriod('0D')

   >>> BusinessPeriod('10D')
   BusinessPeriod('10D')

   >>> BusinessPeriod('1y3m4d')
   BusinessPeriod('1Y3M4D')

   >>> BusinessPeriod('18M')
   BusinessPeriod('1Y6M')

   >>> BusinessPeriod('1Q')
   BusinessPeriod('3M')

   >>> BusinessPeriod('2w')
   BusinessPeriod('14D')

   >>> BusinessPeriod('10B')
   BusinessPeriod('10B')

Inputs like **1Q** and **2W** work, too.
Here **Q** stands for quarters, i.e. 3 months,
and **W** for weeks, i.e. 7 days.

As a convention in financial markets these three additional
shortcuts **ON** for *over night*, **TN** *tomorrow next* and **DD** *double days* exist.

.. paste this into python console to generate code block contents
   from datetime import date, timedelta
   from businessdate import BusinessDate, BusinessPeriod
   BusinessPeriod('ON')
   BusinessPeriod('TN')
   BusinessPeriod('DD')

.. doctest::

   >>> BusinessPeriod('ON')
   BusinessPeriod('1B')

   >>> BusinessPeriod('TN')
   BusinessPeriod('2B')

   >>> BusinessPeriod('DD')
   BusinessPeriod('3B')


The |BusinessPeriod| constructor understands even negative inputs.
Please note the behavior of the preceding sign!

.. paste this into python console to generate code block contents
   from datetime import date, timedelta
   from businessdate import BusinessDate, BusinessPeriod
   BusinessPeriod('-0b')
   BusinessPeriod('-10D')
   BusinessPeriod('-1y3m4d')
   BusinessPeriod('-18M')
   BusinessPeriod('-1Q')
   BusinessPeriod('-2w')
   BusinessPeriod('-10B')
   BusinessPeriod(years=-2, months=-6, days=-1)

.. doctest::

   >>> BusinessPeriod('-0b')
   BusinessPeriod('0D')

   >>> BusinessPeriod('-10D')
   BusinessPeriod('-10D')

   >>> BusinessPeriod('-1y3m4d')
   BusinessPeriod('-1Y3M4D')

   >>> BusinessPeriod('-18M')
   BusinessPeriod('-1Y6M')

   >>> BusinessPeriod('-1Q')
   BusinessPeriod('-3M')

   >>> BusinessPeriod('-2w')
   BusinessPeriod('-14D')

   >>> BusinessPeriod('-10B')
   BusinessPeriod('-10B')

   >>> BusinessPeriod(years=-2, months=-6, days=-1)
   BusinessPeriod('-2Y6M1D')

.. caution::

   Beware of the fact that all non zero attributes must meet the same sign.

      >>> BusinessPeriod(months=1, days=-1)
      Traceback (most recent call last):
        File "<stdin>", line 1, in <module>
        File "/Users/jph/Dropbox/Apps/GitHub/sonntagsgesicht/businessdate/businessdate/businessperiod.py", line 106, in __init__
          "(years, months, days)=%s must have equal sign for %s" % (str(ymd), self.__class__.__name__))
      ValueError: (years, months, days)=(0, 1, -1) must have equal sign for BusinessPeriod
      >>>


.. _create_business_range:

BusinessRange
-------------

Since `BusinessRange` just builds a periodical list of items like a `range` statement,
it meets a similar signature and defaults.

.. testsetup:: rolling

   from businessdate import BusinessDate, BusinessPeriod, BusinessRange, BusinessSchedule
   BusinessDate.BASE_DATE = 20151225

.. paste this into python console to generate code block contents
   from businessdate import BusinessDate, BusinessRange
   BusinessDate.BASE_DATE = 20151225
   BusinessDate()
   start = BusinessDate(20151231)
   end = BusinessDate(20181231)
   rolling = BusinessDate(20151121)
   BusinessRange(start)
   BusinessRange(start) == BusinessRange(BusinessDate(), start, '1d', start)
   len(BusinessRange(start))
   len(BusinessRange(start)) == start.diff_in_days(end)
   start in BusinessRange(start)
   end not in BusinessRange(start)
   annually_range = BusinessRange(start, end, '1y', rolling)
   start in annually_range
   end not in annually_range
   annually_range

.. doctest:: rolling

   >>> BusinessDate()
   BusinessDate(20151225)

   >>> start = BusinessDate(20151231)
   >>> end = BusinessDate(20181231)
   >>> rolling = BusinessDate(20151121)

   >>> BusinessRange(start)
   [BusinessDate(20151225), BusinessDate(20151226), BusinessDate(20151227), BusinessDate(20151228), BusinessDate(20151229), BusinessDate(20151230)]

   >>> BusinessRange(start) == BusinessRange(BusinessDate(), start, '1d', start)
   True

   >>> len(BusinessRange(start))
   6

   >>> len(BusinessRange(start)) == start.diff_in_days(end)
   False

   >>> BusinessDate() in BusinessRange(start)
   True

   >>> start not in BusinessRange(start)
   True

To understand the rolling, think of periodical date pattern
(like a wave) expanding from rolling date to future an past.
Start and end date set boundaries such that all dates between
them are in the business range.

If the start date meets those date, it is included.
But the end date will never be included.

.. doctest:: rolling

   >>> start in BusinessRange(start, end, '1y', end)
   True

   >>> end in BusinessRange(start, end, '1y', end)
   False

   >>> BusinessRange(start, end, '1y', end)
   [BusinessDate(20151231), BusinessDate(20161231), BusinessDate(20171231)]

If the start date does not meet any date in the range, it is not included.

.. doctest:: rolling

   >>> start in BusinessRange(start, end, '1y', rolling)
   False

   >>> end in BusinessRange(start, end, '1y', rolling)
   False

   >>> BusinessRange(start, end, '1y', rolling)
   [BusinessDate(20161121), BusinessDate(20171121), BusinessDate(20181121)]

Rolling on the same `start` and `end` but different `rolling` may lead to
different ranges.

.. doctest:: rolling

   >>> start = BusinessDate(20150129)
   >>> end = BusinessDate(20150602)
   >>> rolling_on_start = BusinessRange(start, end, '1m1d', start)
   >>> rolling_on_end = BusinessRange(start, end, '1m1d', end)

   >>> rolling_on_start == rolling_on_end
   False

   >>> rolling_on_start
   [BusinessDate(20150129), BusinessDate(20150301), BusinessDate(20150331), BusinessDate(20150502)]

   >>> rolling_on_end
   [BusinessDate(20150129), BusinessDate(20150227), BusinessDate(20150331), BusinessDate(20150501)]

Luckily, straight periods, e.g.

   * annually,

   * semi-annually,

   * quarterly,

   * monthly,

   * weekly or

   * daily,

don't mix-up in such a way.

   .. doctest:: rolling

      >>> start = BusinessDate(20200202)
      >>> end = start + BusinessPeriod('1y') * 10
      >>> BusinessRange(start, end, '1y', start) == BusinessRange(start, end, '1y', end)
      True

      >>> end = start + BusinessPeriod('6m') * 10
      >>> BusinessRange(start, end, '6m', start) == BusinessRange(start, end, '6m', end)
      True

      >>> end = start + BusinessPeriod('1q') * 10
      >>> BusinessRange(start, end, '1q', start) == BusinessRange(start, end, '1q', end)
      True

      >>> end = start + BusinessPeriod('1m') * 10
      >>> BusinessRange(start, end, '1m', start) == BusinessRange(start, end, '1m', end)
      True

      >>> end = start + BusinessPeriod('1w') * 10
      >>> BusinessRange(start, end, '1w', start) == BusinessRange(start, end, '1w', end)
      True

      >>> end = start + BusinessPeriod('1d') * 10
      >>> BusinessRange(start, end, '1d', start) == BusinessRange(start, end, '1d', end)
      True

BusinessSchedule
----------------

A |BusinessSchedule|, as inhereted from |BusinessRange|,
provides nearly the same features as |BusinessRange|.
But |BusinessSchedule| lists contain always start date and end date!

Since the first as well as the last period can be very short (short stubs),
they can be trimmed to give a first and/or last period as long stubs.

.. paste this into python console to generate code block contentsrd = BusinessDate(20151121)
   start = BusinessDate(20151231)
   end = BusinessDate(20181231)
   rolling = BusinessDate(20151121)
   BusinessRange(start, end, '1y', rolling)
   BusinessSchedule(start, end, '1y', rolling)
   BusinessSchedule(start, end, '1y', rolling).first_stub_long()
   BusinessSchedule(start, end, '1y', rolling).last_stub_long()
   BusinessSchedule(start, end, '1y', rolling).first_stub_long().last_stub_long()

.. doctest:: rolling

   >>> start = BusinessDate(20151231)
   >>> end = BusinessDate(20181231)
   >>> rolling = BusinessDate(20151121)

   >>> BusinessRange(start, end, '1y', rolling)
   [BusinessDate(20161121), BusinessDate(20171121), BusinessDate(20181121)]

   >>> BusinessSchedule(start, end, '1y', rolling)
   [BusinessDate(20151231), BusinessDate(20161121), BusinessDate(20171121), BusinessDate(20181121), BusinessDate(20181231)]

   >>> BusinessSchedule(start, end, '1y', rolling).first_stub_long()
   [BusinessDate(20151231), BusinessDate(20171121), BusinessDate(20181121), BusinessDate(20181231)]

   >>> BusinessSchedule(start, end, '1y', rolling).last_stub_long()
   [BusinessDate(20151231), BusinessDate(20161121), BusinessDate(20171121), BusinessDate(20181231)]

   >>> BusinessSchedule(start, end, '1y', rolling).first_stub_long().last_stub_long()
   [BusinessDate(20151231), BusinessDate(20171121), BusinessDate(20181231)]


BusinessHolidays
----------------

Since we deal with |BusinessDate| the container class |BusinessHolidays|
is useful as it converts nearly anything input into **datetime.date**.


Provide list of **datetime.date** or anything having attributes `year`, `month` and `days`,
e.g. iterable that yields of |BusinessDate|.

For example you can use projects like `python-holidays <https://pypi.org/project/holidays/>`_
or `workcalendar <https://peopledoc.github.io/workalendar/>`_
which offer holidays in many different countries, regions and calendars.

.. _target_holidays:

Build-in are |TargetHolidays| which are bank holidays in
euro banking system `TARGET <https://en.wikipedia.org/wiki/TARGET2#Holidays>`_.

They serve as default value if no holidays are given.
They can be changed on demand via the class attribute **DEFAULT_HOLIDAYS**
in |BusinessDate|.

.. testsetup:: holidays

   from businessdate import BusinessDate
   default_holidays = BusinessDate.DEFAULT_HOLIDAYS

.. doctest:: holidays

   >>> BusinessDate(20100101) in BusinessDate.DEFAULT_HOLIDAYS
   True

   >>> BusinessDate.DEFAULT_HOLIDAYS = list()
   >>> BusinessDate(20100101) in BusinessDate.DEFAULT_HOLIDAYS
   False

.. testcleanup:: holidays

   BusinessDate.DEFAULT_HOLIDAYS = default_holidays


Calculating Dates and Periods
=============================

.. attention:: Even `adding` and `subtracting` Dates and Periods suggest
   to be a kind of algebraic operation like adding and subtracting
   numbers. But they are not, at least not in a similar way!

Algebraic operations of numbers are known to be

* compatible, e.g. `3 + 3 = 2 * 3 = 2 + 2 + 2`
* associative, e.g. `(1 + 2) + 3 = 1 + (2 + 3)`
* distributive, e.g. `(1 + 1) * 2 = 2 + 2`
* commutative, e.g. `1 + 2 = 2 + 1`

Due to different many days in different months as well as leap years
periods do not act that way on dates.

.. note::

   For example, add 2 month to March, 31th should give May, 31th.
   But adding 2 times 1 month will give May, 30th, since

   March, 31th + 1 month = April, 30th

   April, 30th + 1 month = May, 30th

Even more pitfalls exist when izt comes to calculate dates and calendars.
Fortunately periods acting on them self behave much more like numbers.

All this is build into |BusinessPeriod| and |BusinessDate|.


Adding
------

Date + Period
~~~~~~~~~~~~~

Adding two dates does not any sense. So we can only add a period to a date
to give a new date

   .. doctest::

       >>> BusinessDate(20150612) + BusinessPeriod('6M19D')
       BusinessDate(20151231)


Period + Period
~~~~~~~~~~~~~~~

And two periods to give a new period -
as long as the do not mix business days and classical periods.

   .. doctest::

      >>> BusinessPeriod('6M10D') + BusinessPeriod('9D')
      BusinessPeriod('6M19D')

      >>> BusinessPeriod('9D') + BusinessPeriod('6M10D')
      BusinessPeriod('6M19D')

      >>> BusinessPeriod('5B') + BusinessPeriod('10B')
      BusinessPeriod('15B')


Subtracting
-----------

Date - Date
~~~~~~~~~~~

Surprisingly, the difference of two dates makes sense,
as the distance in numeber of years than months and finaly days
from the early to the later date.

   .. doctest::

      >>> BusinessDate(20151231) - BusinessDate(20150612)
      BusinessPeriod('6M19D')

Those are just the inverse operations

   .. doctest::

      >>> period = BusinessDate(20151231) - BusinessDate(20150612)
      >>> BusinessDate(20151231) == BusinessDate(20150612) + period
      True

But note that these operations are not commutative,
i.e. swapping the order can give something completely different
as the the direction of the point of view is changed.

   .. doctest::

      >>> dec31 = BusinessDate(20151231)
      >>> jun12 = BusinessDate(20150612)

      >>> dec31 - jun12  # it takes 6 months and 19 days from jun12 to dec31
      BusinessPeriod('6M19D')

      >>> jun12 - dec31  # jun12 is 6 months and 18 days before dec31
      BusinessPeriod('-6M18D')

      >>> jan29 = BusinessDate(20150129)
      >>> mar01 = BusinessDate(20150301)

      >>> mar01 - jan29  # from jan29 yoe waits 1 month and 1 day until mar01
      BusinessPeriod('1M1D')

      >>> jan29 - mar01  # but mar01 was 1 month and 3 days before
      BusinessPeriod('-1M3D')

This becomes clear if you check this with your calendar.

   .. image:: ../pix/period_algebra.png
      :alt: diagram of jan29 + 1m1d = mar01 vs mar01 - 1m3d = jan29 (period algebra)

But still we get

   .. doctest::

      >>> BusinessDate(20150612) - BusinessDate(20151231)
      BusinessPeriod('-6M18D')

      >>> BusinessDate(20150612) == BusinessDate(20151231) - BusinessPeriod('6M18D')
      True


Date - Period
~~~~~~~~~~~~~

And again, we can subtract a period from a date to give a new date.

   .. doctest::

      >>> BusinessDate(20151231) - BusinessPeriod('6M18D') == BusinessDate(20150612)
      True

      >>> BusinessDate(20151231) - BusinessPeriod('10b')
      BusinessDate(20151216)


Period + Period
~~~~~~~~~~~~~~~

And straight forward, two periods substracted from each other to give a new period.
Again, as long as the do not mix business days and classical periods.

   .. doctest::

      >>> BusinessPeriod('6M19D') - BusinessPeriod('6M10D')
      BusinessPeriod('9D')

      >>> BusinessPeriod('-6M10D') - BusinessPeriod('-6M19D')
      BusinessPeriod('9D')

      >>> BusinessPeriod('10b') - BusinessPeriod('15b')
      BusinessPeriod('-5B')


Multiplying
-----------

Period * int
~~~~~~~~~~~~

Since an instance of a :class:`BusinessPeriod` stored the number
of `years`, `month`, `days` or `businessdays` as :class:`int`
one multiply this by integer, too.

Note that the number of `month` can be reduced if it's exceeds the number of 12.
But we can not do anything like this with days.

   .. doctest::

      >>> BusinessPeriod('1y2m3d') * 2
      BusinessPeriod('2Y4M6D')

      >>> BusinessPeriod('1y8m200d') * 2
      BusinessPeriod('3Y4M400D')

      >>> y, m, d = 1, 2, 3
      >>> BusinessPeriod(years=y, months=m, days=d) * 2 == BusinessPeriod(years=y*2, months=m*2, days=d*2)
      True

      >>> BusinessPeriod('1y2m3d') * 2 == 2 * BusinessPeriod('1y2m3d')
      True


Comparing
---------

Dates
~~~~~

Calendars assume time to be evolving in strictly one direction, from past to future.
Hence days can be well ordered and so be compared. Same for :class:`BusinessDate`.

   .. doctest::

      >>> BusinessDate(20151231) < BusinessDate(20160101)
      True

      >>> BusinessDate(20151231) == BusinessDate(20160101)
      False

      >>> BusinessDate(20151231) > BusinessDate(20160101)
      False

Periods
~~~~~~~

Two Tuples of three numbers `(a,b,c)` and `(d,e,f)`
have only a natural order if all three numbers meet the same relation, e.g.


   `(a,b,c) < (d,e,f)` if `a < d` and `b < e` and `c < f`

   `(a,b,c) == (d,e,f)` if `a == d` and `b == e` and `c == f`

In case of a two classical period as a `(years, months, days)` the problem can be reduced
by comparing only two numbers `(years*12 + months, days)`.

But leveraging the order of dates, a period `p` can be seen as greater than a period `q`
if for any possible date `d` adding both periods give always the same resulting order in dates.

I.e. we get

   `p < q` if `d + p < d + q` for all dates `d`

Hence, we are left with only *few* situations, which might give for different dates `d` and `d'`

   `d + p < d + q` but `d' + p >= d' + q`

Since `days` vary in different month, periods close to each other are difficult to compare,
e.g. is **1M1D** greater or equal **31D**?

   .. doctest::

      >>> p = BusinessPeriod('1M1D')
      >>> q = BusinessPeriod('31D')

      >>> BusinessDate(20150131) + p < BusinessDate(20150131) + q
      True

      >>> BusinessDate(20150731) + p < BusinessDate(20150731) + q
      False

So, let `(a,b,c)` and `(d,e,f)` be two periods with

   `m = (a - b) * 12 + b - e` and `d = c - f`

as the distance of both measured in `months` and `days`.

The sequence of the number of days in a period of given months with
minimal days as well as max can be derived. The first 13 months listed.

       ======  ===========
       months   num days
       ======  ===========
         1      28 ... 31
         2      59 ... 62
         3      89 ... 92
         4     120 ... 123
         5     150 ... 153
         6     181 ... 184
         7     212 ... 215
         8     242 ... 245
         9     273 ... 276
        10     303 ... 306
        11     334 ... 337
        12     365 ... 366
        13     393 ... 397
       ======  ===========

.. starting at February with 28 days and then adding non leap year days
   of the following months + leap day after 36 month

For those pairs of month and days any comparison of **<** or **>** is not well defined. Hence,

   .. doctest::

      >>> BusinessPeriod('13m') < BusinessPeriod('392d')
      False

      >>> BusinessPeriod('13m') < BusinessPeriod('393d') # not well defined -> None

      >>> BusinessPeriod('13m') < BusinessPeriod('397d') # not well defined -> None

      >>> BusinessPeriod('13m') < BusinessPeriod('398d')
      True

But

   .. doctest::

      >>> BusinessPeriod('13m') <= BusinessPeriod('392d')
      False

      >>> BusinessPeriod('13m') <= BusinessPeriod('393d') # not well defined -> None

      >>> BusinessPeriod('13m') <= BusinessPeriod('397d')
      True

      >>> BusinessPeriod('13m') <= BusinessPeriod('398d')
      True

So comparison of arbitrary instances or :class:`BusinessPeriod` only works for **==**.

   .. doctest::

      >>> BusinessPeriod('ON') == BusinessPeriod('1B')
      True

      >>> BusinessPeriod('7D') == BusinessPeriod('1W')
      True

      >>> BusinessPeriod('30D') == BusinessPeriod('1M')
      False

      >>> BusinessPeriod('1D') == BusinessPeriod('1B')
      False


Adjusting
---------
Dates
~~~~~

When adding a period to a date results on a weekend day
may make no sense in terms of business date.
This happens frequently when a interst payment plan is rolled out.
In such a case all dates which fall either on weekend days
or on holidays have to be moved (`adjusted`) to a business day.

In financial markets different conventions of business day adjustments are kown.
Most of them are part of the `ISDA Definitions <https://www.isda.org/book/2006-isda-definitions/>`_
which are not open to public.
But see `date rolling <https://en.wikipedia.org/wiki/Date_rolling>`_ for more details.

.. doctest::

   >>> weekend_day = BusinessDate(20141129)
   >>> weekend_day.weekday()  # Monday is 0 and Sunday is 6
   5

   >>> weekend_day.adjust('follow')  # move to next business day
   BusinessDate(20141201)

   >>> weekend_day.adjust('previous')  # move to previous business day
   BusinessDate(20141128)

   >>> weekend_day.adjust('mod_follow')  # move to next business day in same month else pervious
   BusinessDate(20141128)

   >>> BusinessDate(20141122).adjust('mod_follow')  # move to next business day in same month else pervious
   BusinessDate(20141124)

   >>> weekend_day.adjust('mod_previous')  # move to previous business day in same month else follow
   BusinessDate(20141128)

   >>> weekend_day.adjust('start_of_month')  # move to first business day in month
   BusinessDate(20141103)

   >>> weekend_day.adjust('end_of_month')  # move to last business day in month
   BusinessDate(20141128)

In order to provide specific holidays a list of
**datetime.date** objects can be given as an extra argument.
It can convenient to use a |BusinessHolidays| instance instead but any
type that implements `__contain__` will work.

.. doctest::

   >>> weekend_day.adjust('follow', holidays=[BusinessDate(20141201)])  # move to next business day
   BusinessDate(20141202)

If no holidays are given the **DEFAULT_HOLIDAYS**  of |BusinessDate| are used.
By default those are the :ref:`TARGET holidays <target_holidays>`.

To view all possible `convention` key words see |BusinessDate().adjust()| documentation.

.. BusinessDate().adjust()

.. In order to adjust according a business day conventionuse `BusinessDate().adjust(convention, holidays=None)`
   and provide one of the following convention key words:

     'no'             does no adjusts.
     'previous'       adjusts to Business Day Convention "Preceding" (4.12(a) (iii) 2006 ISDA Definitions).
     'prev'           adjusts to Business Day Convention "Preceding" (4.12(a) (iii) 2006 ISDA Definitions).
     'prv'            adjusts to Business Day Convention "Preceding" (4.12(a) (iii) 2006 ISDA Definitions).
     'mod_previous'   adjusts to Business Day Convention "Modified Preceding" (not in 2006 ISDA Definitons).
     'modprevious'    adjusts to Business Day Convention "Modified Preceding" (not in 2006 ISDA Definitons).
     'modprev'        adjusts to Business Day Convention "Modified Preceding" (not in 2006 ISDA Definitons).
     'modprv'         adjusts to Business Day Convention "Modified Preceding" (not in 2006 ISDA Definitons).
     'follow'         adjusts to Business Day Convention "Following" (4.12(a) (i) 2006 ISDA Definitions).
     'flw'            adjusts to Business Day Convention "Following" (4.12(a) (i) 2006 ISDA Definitions).
     'mod_follow'     adjusts to Business Day Convention "Modified [Following]" (4.12(a) (ii) 2006 ISDA Definitions).
     'modfollow'      adjusts to Business Day Convention "Modified [Following]" (4.12(a) (ii) 2006 ISDA Definitions).
     'modflw'         adjusts to Business Day Convention "Modified [Following]" (4.12(a) (ii) 2006 ISDA Definitions).
     'start_of_month' adjusts to Business Day Convention "Start of month", i.e. first business day.
     'startofmonth'   adjusts to Business Day Convention "Start of month", i.e. first business day.
     'som'            adjusts to Business Day Convention "Start of month", i.e. first business day.
     'end_of_month'   adjusts to Business Day Convention "End of month", i.e. last business day.
     'endofmonth'     adjusts to Business Day Convention "End of month", i.e. last business day.
     'eom'            adjusts to Business Day Convention "End of month", i.e. last business day.
     'imm'            adjusts to Business Day Convention of  "International Monetary Market".
     'cds_imm'        adjusts to Business Day Convention "Single Name CDS" (not in 2006 ISDA Definitions).
     'cdsimm'         adjusts to Business Day Convention "Single Name CDS" (not in 2006 ISDA Definitions).
     'cds'            adjusts to Business Day Convention "Single Name CDS" (not in 2006 ISDA Definitions).

.. BusinessDate(20151225)

Beside |BusinessDate| there is also |BusinessRange().adjust()| (same for |BusinessSchedule|)
which adjust all items in the |BusinessRange|.

.. doctest:: rolling

   >>> start = BusinessDate(20151231)
   >>> BusinessRange(start)
   [BusinessDate(20151225), BusinessDate(20151226), BusinessDate(20151227), BusinessDate(20151228), BusinessDate(20151229), BusinessDate(20151230)]

   >>> BusinessRange(start).adjust('mod_follow')
   [BusinessDate(20151228), BusinessDate(20151228), BusinessDate(20151228), BusinessDate(20151228), BusinessDate(20151229), BusinessDate(20151230)]


Measuring
---------

Periods
~~~~~~~

Interest rates are agree and settled as annual rate. In contrast to this annual definition,
interest payments are often semi-annually, quarterly or monthly
or even `daily <https://en.wikipedia.org/wiki/Overnight_rate>`_.

In order to calculate an less than annal interest payment from an annual interest rate
the `year fraction` of each particular period is used as

   `interest payment = annual interest rate * year fraction * notional`

The `year fraction` depends on the days between the `start date` and `end date` of a period.
In order to simplify calculation in the past there various financial markets convention
to count days between dates, see detail on
`day count conventions <https://en.wikipedia.org/wiki/Day_count_convention>`_.

The most common `day count conventions`, i.e. `year fraction`,
are available by |BusinessDate().get_day_count()| and |BusinessDate().get_year_fraction()|
(different name but same fuctionality).

To view all possible `convention` see |BusinessDate().get_day_count()|  documentation.

.. doctest::

   >>> start_date = BusinessDate(20190829)
   >>> end_date = start_date + '3M'

   >>> start_date.get_day_count(end_date, 'act_act')
   0.25205479452054796

   >>> start_date.get_day_count(end_date, 'act_36525')
   0.2518822724161533

   >>> start_date.get_day_count(end_date, 'act_365')
   0.25205479452054796

   >>> start_date.get_day_count(end_date, 'act_360')
   0.25555555555555554

   >>> start_date.get_day_count(end_date, '30_360')
   0.25

   >>> start_date.get_day_count(end_date, '30E_360')
   0.25

   >>> start_date.get_day_count(end_date, '30E_360_I')
   0.25

BusinessDate Details
====================

More Creation Patterns
----------------------

More complex creation pattern work, too.
They combine the creation of a date plus a period
with business day adjustemnt conventions at start and/or end of the period.


.. paste this into python console to generate code block contents
   from businessdate import BusinessDate, BusinessPeriod
   BusinessDate.BASE_DATE = 20161009
   BusinessDate()
   # create from period
   BusinessDate(BusinessPeriod(months=1))
   # create from period string
   BusinessDate('1m')
   BusinessDate() + '1m'
   # works with additional date as well
   BusinessDate('1m20161213')
   BusinessDate('20161213') + '1m'
   # even for business days
   BusinessDate('15b')
   BusinessDate() + '15b'
   # add adjustment convention 'end_of_month' with a business date
   BusinessDate('0bEOM')
   BusinessDate('15bEOM')
   # add adjustment convention 'mod_follow' with a business date
   BusinessDate('0bModFlw')
   BusinessDate('15bModFlw')
   # adjustment convention without a business date is ignored
   BusinessDate('EOM')
   BusinessDate('ModFlw')
   # even together with a classical period since the adjustment statement is ambiguous
   # should the start date (spot) or end date be adjusted?
   BusinessDate('1mModFlw')
   # but adding zero business days clarifies it
   BusinessDate('0b1mModFlw')
   BusinessDate('0b1mModFlw') == BusinessDate().adjust('ModFlw') + '1m'
   BusinessDate('1m0bModFlw')
   BusinessDate('1m0bModFlw') == (BusinessDate() + '1m').adjust('ModFlw')
   # clearly business days may be non zero, too
   BusinessDate('15b1mModFlw')
   BusinessDate('15b1mModFlw') == BusinessDate('15b').adjust('ModFlw') + '1m'
   BusinessDate('1m5bModFlw')
   BusinessDate('1m5bModFlw') == (BusinessDate() + '1m').adjust('ModFlw') + '5b'
   # putting all together we get
   BusinessDate('15b1m5bModFlw20161213')
   BusinessDate('15b1m5bModFlw20161213') == ((BusinessDate(20161213)+'15b').adjust('ModFlw') + '1m').adjust('ModFlw') + '5b'

.. testsetup:: complex

   from businessdate import BusinessDate, BusinessPeriod
   BusinessDate.BASE_DATE = 20161009

Create an instance directly from a period or period string.

.. doctest:: complex

   >>> BusinessDate()
   BusinessDate(20161009)

   >>> BusinessDate() + '1m'
   BusinessDate(20161109)

   >>> BusinessDate(BusinessPeriod(months=1))
   BusinessDate(20161109)

   >>> BusinessDate('1m')
   BusinessDate(20161109)

   >>> BusinessDate('15b')
   BusinessDate(20161028)

   >>> BusinessDate() + '15b'
   BusinessDate(20161028)

This works with additional date, too.

.. doctest:: complex

   >>> BusinessDate('1m20161213')
   BusinessDate(20170113)

   >>> BusinessDate('20161213') + '1m'
   BusinessDate(20170113)

Adding the adjustment convention 'end_of_month' with a business date gives the following.

.. doctest:: complex

   >>> BusinessDate('0bEOM')
   BusinessDate(20161031)

   >>> BusinessDate('EOM')
   BusinessDate(20161031)

   >>> BusinessDate().adjust('EOM')
   BusinessDate(20161031)

   >>> BusinessDate('15bEOM')
   BusinessDate(20161121)

   >>> BusinessDate().adjust('EOM') + '15b'
   BusinessDate(20161121)

Adding the adjustment convention 'mod_follow' with a business date lead to this.

.. doctest:: complex

   >>> BusinessDate('0bModFlw')
   BusinessDate(20161010)

   >>> BusinessDate('ModFlw')
   BusinessDate(20161010)

   >>> BusinessDate().adjust('ModFlw')
   BusinessDate(20161010)

   >>> BusinessDate('15bModFlw')
   BusinessDate(20161031)

   >>> BusinessDate().adjust('ModFlw') + '15b'
   BusinessDate(20161031)

But a adjustment convention with a classical period
and without a business date is ignored
since the adjustment statement is ambiguous:

Should the start date (spot) or end date be adjusted?

.. doctest:: complex

   >>> BusinessDate('1mEOM')
   BusinessDate(20161109)

   >>> BusinessDate('1mModFlw')
   BusinessDate(20161109)

Adding zero business days clarifies it!

.. doctest:: complex

   >>> BusinessDate('0b1mModFlw')
   BusinessDate(20161110)

   >>> BusinessDate('0b1mModFlw') == BusinessDate().adjust('ModFlw') + '1m'
   True

   >>> BusinessDate('1m0bModFlw')
   BusinessDate(20161109)

   >>> BusinessDate('1m0bModFlw') == (BusinessDate() + '1m').adjust('ModFlw')
   True

Clearly business days may be non zero, too.

.. doctest:: complex

   >>> BusinessDate('15b1mModFlw')
   BusinessDate(20161130)

   >>> BusinessDate('15b1mModFlw') == BusinessDate('ModFlw') + '15b' + '1m'
   True

   >>> BusinessDate('1m5bModFlw')
   BusinessDate(20161116)

   >>> BusinessDate('1m5bModFlw') == BusinessDate('1m').adjust('ModFlw') + '5b'
   True

Putting all together we get.

.. doctest:: complex

   >>> BusinessDate('15b1m5bModFlw20161213')
   BusinessDate(20170213)

   >>> bd = BusinessDate(20161213)
   >>> bd = bd.adjust('ModFlw')
   >>> bd = bd + '15b'
   >>> bd = bd + '1m'
   >>> bd = bd.adjust('ModFlw')
   >>> bd = bd + '5b'
   >>> bd
   BusinessDate(20170213)

   >>> BusinessDate('15b1m5bModFlw20161213') == (BusinessDate(20161213).adjust('ModFlw') + '15b' + '1m').adjust('ModFlw') + '5b'
   True


.. testcleanup:: complex

   BusinessDate.BASE_DATE = None


BusinessDate Inheritance
------------------------

Finally some lines on :ref:`base classes <base_class_warning>`
|BaseDateFloat| backed by **float** ...

.. paste this into python console to generate code block contents
   from datetime import date
   from businessdate.basedate import BaseDateFloat
   BaseDateFloat(40123.)
   BaseDateFloat.from_ymd(2009, 11, 6)
   BaseDateFloat.from_date(date(2009, 11, 6))
   BaseDateFloat.from_float(40123.)
   d = BaseDateFloat(40123.)
   d.year, d.month, d.day
   d.to_ymd()
   d.to_date()
   d.to_float()

.. doctest::

    >>> from datetime import date
    >>> from businessdate.basedate import BaseDateFloat

    >>> BaseDateFloat(40123.)
    40123.0

    >>> BaseDateFloat.from_ymd(2009, 11, 6)
    40123.0

    >>> BaseDateFloat.from_date(date(2009, 11, 6))
    40123.0

    >>> BaseDateFloat.from_float(40123.)
    40123.0

    >>> d = BaseDateFloat(40123.)
    >>> d.year, d.month, d.day
    (2009, 11, 6)

    >>> d.to_ymd()
    (2009, 11, 6)

    >>> d.to_date()
    datetime.date(2009, 11, 6)

    >>> d.to_float()
    40123.0



... and |BaseDateDatetimeDate|
backed by **datetime.date**.

.. paste this into python console to generate code block contents
   from datetime import date
   from businessdate.basedate import BaseDateDatetimeDate
   BaseDateDatetimeDate(2009, 11, 6)
   BaseDateDatetimeDate.from_ymd(2009, 11, 6)
   BaseDateDatetimeDate.from_date(date(2009, 11, 6))
   BaseDateDatetimeDate.from_float(40123.)
   BaseDateDatetimeDate(2009, 11, 6)
   d.year, d.month, d.day
   d.to_ymd()
   d.to_date()
   d.to_float()

.. doctest::

    >>> from datetime import date
    >>> from businessdate.basedate import BaseDateDatetimeDate

    >>> BaseDateDatetimeDate(2009, 11, 6)
    BaseDateDatetimeDate(2009, 11, 6)

    >>> BaseDateDatetimeDate.from_ymd(2009, 11, 6)
    BaseDateDatetimeDate(2009, 11, 6)

    >>> BaseDateDatetimeDate.from_date(date(2009, 11, 6))
    BaseDateDatetimeDate(2009, 11, 6)

    >>> BaseDateDatetimeDate.from_float(40123.)
    BaseDateDatetimeDate(2009, 11, 6)

    >>> BaseDateDatetimeDate(2009, 11, 6)
    BaseDateDatetimeDate(2009, 11, 6)

    >>> d.year, d.month, d.day
    (2009, 11, 6)

    >>> d.to_ymd()
    (2009, 11, 6)

    >>> d.to_date()
    datetime.date(2009, 11, 6)

    >>> d.to_float()
    40123.0


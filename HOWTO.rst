
.. currentmodule:: businessdate

To start with |businessdate| import it.
Note that, since we work with dates, |datetime.date| might be useful, too.
But not required. Nevertheless |datetime.date| is used inside |BusinessDate| from time to time.

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
    [BusinessDate(20140216), BusinessDate(23011230), BusinessDate(19991111), BusinessDate(20200202)]

Much easier to generate container with periodical items is using |BusinessRange|.

By default an empty |BusinessDate()|
is initiated with the system date as given by |datetime.date.today()|.
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
   |datetime.date.today()| is different to setting to **None**
   since |datetime.date.today()| changes at midnight!


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

Moreover, the difference of two instances of |datetime.date| or resp.
a |datetime.timedelta| instance can be used to init, too.

.. paste this into python console to generate code block contents
   from datetime import date, timedelta
   from businessdate import BusinessDate, BusinessPeriod
   a, b = date(2010,6,1), date(2010,12,31)
   b-a
   BusinessPeriod(b-a)
   timedelta(213)
   BusinessPeriod(timedelta(213))

.. doctest::

   >>> a, b = date(2010,6,1), date(2010,12,31)
   >>> b-a
   datetime.timedelta(days=213)

   >>> BusinessPeriod(b-a)
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


BusinessSchedule
----------------

`BusinesSchedule` provides more lists containing always start date as well as end date.
Since the first as well as the last period can be very short (short stubs),
both can be trimmed to give a first and/or last period as long stubs.

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
is useful as it converts nearly anything input into |datetime.date|.


Provide list of |datetime.date| or anything having attributes `year`, `month` and `days`,
e.g. iterable that yields of |BusinessDate|.

For example you can use projects like `python-holidays <https://pypi.org/project/holidays/>`_
or `workcalendar <https://peopledoc.github.io/workalendar/>`_
which offer holidays in many different countries, regions and calendars.

.. _target_holidays:

Build in are |TargetHolidays| which are bank holidays in
euro banking system `TARGET <https://en.wikipedia.org/wiki/TARGET2#Holidays>`_.


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

..  admonition:: ToDo

   Date + Period

   Period + Period


Subtracting
-----------

..  admonition:: ToDo

   Date - Date

   Date - Period

   Period - Period


Multiplying
-----------

..  admonition:: ToDo

   Period * Int


Comparing
---------

..  admonition:: ToDo

   Date <=> Date

   Period <=> Period (some Periods are difficult to compare, e.g. is **1M** greater or equal ***30D*** )
   nevertheless most of the time (years * 12 month) * 31 + days does give an useful order


Moving
------

Moving dates away from weekend or holidays requires holidays

If no holidays are give the |BusinessDate.DEFAULT_HOLIDAYS| are used.
They can be set on demand.

By default those are the :ref:`TARGET holidays <target_holidays>`.

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


..  admonition:: ToDo

   adjust BusinessDate / BusinessRange / BusinessSchedule to by conventions


Measuring
---------

..  admonition:: ToDo

   day count resp. year fraction as distance between dates


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
|BaseDateFloat| backed by |float| ...

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
backed by |datetime.date|.

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


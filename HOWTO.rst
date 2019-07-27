

First setup basic objects
=========================

Setup model imports

    >>> from datetime import date
    >>> from businessdate import BusinessDate, BusinessPeriod, BusinessRange, BusinessSchedule


Simplest example possible

.. code-block:: python

    >>> BusinessDate.from_date(date(2014, 1, 1)) == BusinessDate(20140101)
    True

    >>> BusinessDate(20140101) + '1y6m'
    20150701

    >>> BusinessDate(20140101).adjust_follow()
    20140102

    >>> BusinessPeriod('1Y')==BusinessPeriod(years=1)
    True

    >>> BusinessPeriod('1Y')
    1Y

    >>> BusinessPeriod('1Y').add_businessdays(3)
    1Y3B

    >>> BusinessPeriod('1Y') + '1y6m'
    1Y6M

    >>> sd = BusinessDate(20151231)
    >>> ed = BusinessDate(20201231)
    >>> BusinessRange(sd, ed, '1y', ed)
    [20151231, 20161231, 20171231, 20181231, 20191231]

    >>> BusinessSchedule(sd, ed, '1y', ed)
    [20151231, 20161231, 20171231, 20181231, 20191231, 20201231]

    >>> BusinessSchedule(sd, ed, '1y', ed).first_stub_long()
    [20151231, 20171231, 20181231, 20191231, 20201231]



:returns:
    an new :py:class:`businessdate.BusinessDate` object or raises according exeption on any error
:rtype: BusinessDate

creates new BusinessDate either from `int`, `float`, `string`, `datetime.date`
therefore the following will create the same

.. code-block:: python

    BusinessDate(datetime.date(2015, 12, 31))
    BusinessDate(20151231)
    BusinessDate('20151231')
    BusinessDate('2015-12-31')
    BusinessDate('31.12.2015')
    BusinessDate('12/31/2015')
    BusinessDate(42369)
    BusinessDate(42369.0)
    BusinessDate.fromordinal(735963)
    BusinessDate()


more complex creation styles work too and give the same

.. code-block:: python

    BusinessDate('1B3M0BMOD20161213')
    BusinessDate('20161213').adjust_follow().add_busindessday(1).add_month(3).adjust_follow()


and some lines on base classes backed by float

.. code-block:: python

    >>> from businessdate.basedate import BaseDateFloat
    >>> BaseDateFloat(40123.)
    40123.0
    >>>
    >>> BaseDateFloat(40123.).from_ymd(2009, 11, 6)
    40123.0
    >>> BaseDateFloat(40123.).from_date(datetime.date(2009, 11, 6))
    40123.0
    >>> BaseDateFloat(40123.).from_float(40123.)
    40123.0
    >>>
    >>> BaseDateFloat(40123.).year, BaseDateFloat(40123.).month, BaseDateFloat(40123.).day
    (2009, 11, 6)
    >>> BaseDateFloat(40123.).to_ymd()
    (2009, 11, 6)
    >>> BaseDateFloat(40123.).to_date()
    datetime.date(2009, 11, 6)
    >>> BaseDateFloat(40123.).to_float()
    40123.0


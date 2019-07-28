
businessdate
------------

.. image:: https://www.codefactor.io/repository/github/sonntagsgesicht/businessdate/badge
   :target: https://www.codefactor.io/repository/github/sonntagsgesicht/businessdate
   :alt: CodeFactor

.. image:: https://api.codeclimate.com/v1/badges/c96a263b34e6367a0b8c/maintainability
   :target: https://codeclimate.com/github/sonntagsgesicht/businessdate/maintainability
   :alt: Maintainability

.. image:: https://api.codeclimate.com/v1/badges/c96a263b34e6367a0b8c/test_coverage
   :target: https://codeclimate.com/github/sonntagsgesicht/businessdate/test_coverage
   :alt: Test Coverage

.. image:: https://img.shields.io/codeship/43157680-92f7-0137-34fd-0e3da511fc50/master.svg
   :target: https://codeship.com//projects/356697
   :alt: Codechip

.. image:: https://readthedocs.org/projects/businessdate/badge
   :target: http://businessdate.readthedocs.io
   :alt: ReadTheDocs

A fast, efficient Python library for generating business dates for fast date operations.
Typical banking business methods are provided like business holidays adjustment, day count fractions.
Beside dates generic business periods offer to create time periods like
'10Y', '3 Months' or '2b'. Periods can easily added to or subtracted from business dates.

Moreover `range` style schedule generator are provided to systematic build a list of dates.
Such are used to set up the payment schedule of loan and financial derivatives.


Example Usage
-------------

.. code-block:: python


    from datetime import date
    from businessdate import BusinessDate, BusinessPeriod

    >>> BusinessDate(years=2014, months=01, days=11)
    20140111
    >>> BusinessDate(date(2014,01,11))
    20140111
    >>> BusinessDate(20140111)
    20140111
    >>> BusinessDate('20140111')
    20140111
    >>> BusinessDate('2015-12-31')
    20151231
    >>> BusinessDate('31.12.2015')
    20151231
    >>> BusinessDate('12/31/2015')
    20151231
    >>>BusinessDate(42369)
    20151231
    >>> BusinessDate(20140101) + BusinessPeriod('1Y3M')
    20150401
    >>> BusinessDate(20140101) + '1Y3M'
    20150401
    >>> BusinessDate(20170101) - '1Y1D'
    20160229
    >>> BusinessDate('1Y3M20140101')
    20150301

Install
-------

The latest stable version can always be installed or updated via pip:

.. code-block:: bash

    $ pip install businessdate


Further Examples
----------------

.. code-block:: python

    # Simplest example possible

    >>> from datetime import date
    >>> from businessdate import BusinessDate, BusinessPeriod, BusinessRange, BusinessSchedule
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


Development Version
-------------------

The latest development version can be installed directly from GitHub:

.. code-block:: bash

    $ pip install --upgrade git+https://github.com/pbrisk/businessdate.git

or downloaded from `<https://github.com/pbrisk/businessdate>`_.


Contributions
-------------

.. _issues: https://github.com/pbrisk/businessdate/issues

Issues_ and `Pull Requests <https://github.com/pbrisk/businessdate/pulls>`_ are always welcome.


License
-------

.. __: https://github.com/pbrisk/businessdate/raw/master/LICENSE

Code and documentation are available according to the Apache Software License (see LICENSE__).

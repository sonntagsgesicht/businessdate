============
businessdate
============

.. image:: https://img.shields.io/codeship/5ba35f10-9caf-0134-8b2b-4e318545e956/master.svg
    :target: https://codeship.com//projects/188434

A fast, efficient Python library for generating business dates inherited
from float for fast date operations. Typical banking business methods
are provided like business holidays adjustment, day count fractions.
Beside dates generic business periods offer to create time periods like
'10Y', '3 Months' or '2b'. Periods can easily added to business dates.


Example Usage
-------------

.. code-block:: python

    from datetime import date

    from businessdate import BusinessDate, BusinessPeriod

    >>> BusinessDate(20140101).add_days(10)
    20140111

    >>> BusinessPeriod('1Y').add_months(3)
    1Y3M

    >>> BusinessDate(20140101) + BusinessPeriod('1Y3M')
    20150301

Install
-------

The latest stable version can always be installed or updated via pip:

.. code-block:: bash

    $ pip install businessdate

If the above fails, please try easy_install instead:

.. code-block:: bash

    $ easy_install businessdate


Examples
--------

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


Contributions
-------------

.. _issues: https://github.com/pbrisk/businessdate/issues
.. __: https://github.com/pbrisk/businessdate/pulls

Issues_ and `Pull Requests`__ are always welcome.


License
-------

.. __: https://github.com/pbrisk/businessdate/raw/master/LICENSE

Code and documentation are available according to the Apache Software License (see LICENSE__).



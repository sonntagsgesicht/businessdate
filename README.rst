
Python library *businessdate*
-----------------------------

.. image:: https://github.com/sonntagsgesicht/businessdate/actions/workflows/python-package.yml/badge.svg
    :target: https://github.com/sonntagsgesicht/businessdate/actions/workflows/python-package.yml
    :alt: GitHubWorkflow

.. image:: https://img.shields.io/readthedocs/businessdate
   :target: http://businessdate.readthedocs.io
   :alt: Read the Docs

.. image:: https://img.shields.io/github/license/sonntagsgesicht/businessdate
   :target: https://github.com/sonntagsgesicht/businessdate/raw/master/LICENSE
   :alt: GitHub

.. image:: https://img.shields.io/github/release/sonntagsgesicht/businessdate?label=github
   :target: https://github.com/sonntagsgesicht/businessdate/releases
   :alt: GitHub release

.. image:: https://img.shields.io/pypi/v/businessdate
   :target: https://pypi.org/project/businessdate/
   :alt: PyPI Version

.. image:: https://img.shields.io/pypi/pyversions/businessdate
   :target: https://pypi.org/project/businessdate/
   :alt: PyPI - Python Version

.. image:: https://img.shields.io/pypi/dm/businessdate
   :target: https://pypi.org/project/businessdate/
   :alt: PyPI Downloads

.. image:: https://pepy.tech/badge/businessdate
   :target: https://pypi.org/project/businessdate/
   :alt: PyPI Downloads

A fast, efficient Python library for generating `business dates` for simple and fast date operations.

.. code-block:: python

   >>> from businessdate import BusinessDate

   >>> BusinessDate(2017,12,31) + '2 weeks'
   BusinessDate(20180114)

   >>> BusinessDate(20171231) + '2w'  # same but shorter
   BusinessDate(20180114)

   >>> BusinessDate(20180114).to_date()
   datetime.date(2018, 1, 14)

Typical banking business features are provided like `holiday adjustments`
to move dates away from weekend days or `holidays`. As well as functionality to get
`year fractions` depending on `day count conventions` as the lengths of interest payment periods.

Beside dates `business periods` can be created for time intervals like **10Y**, **3 Months** or **2b**.
Those periods can easily be added to or subtracted from business dates.

Moreover `range` style `schedule generator`
are provided to systematic build a list of dates.
Such are used to set up a payment schedule of loan and financial derivatives.


Example Usage
-------------

.. paste this into python console to generate code block contents
   from datetime import date
   from businessdate import BusinessDate, BusinessPeriod
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

.. code-block:: python

    >>> from datetime import date
    >>> from businessdate import BusinessDate, BusinessPeriod


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

    >>> BusinessDate(42369)
    BusinessDate(20151231)

    >>> BusinessDate(20140101) + BusinessPeriod('1Y3M')
    BusinessDate(20150401)

    >>> BusinessDate(20140101) + '1Y3M'
    BusinessDate(20150401)

    >>> BusinessDate(20170101) - '1Y1D'
    BusinessDate(20151231)

    >>> BusinessDate() == BusinessDate(date.today())
    True

    >>> BusinessDate('1Y3M20140101')
    BusinessDate(20150401)

For more examples see the `documentation <http://businessdate.readthedocs.io>`_.

Install
-------

The latest stable version can always be installed or updated via pip:

.. code-block:: bash

    $ pip install businessdate



Development Version
-------------------

The latest development version can be installed directly from GitHub:

.. code-block:: bash

    $ pip install --upgrade git+https://github.com/sonntagsgesicht/businessdate.git

or downloaded from `<https://github.com/sonntagsgesicht/businessdate>`_.



ToDo
----

1. decide which base class or inheritance for `BusisnessDate` is better:

   a) `BaseDateFloat` (`float` inheritance)

   b) `BaseDateDatetimeDate` (`datetime.date` inheritance)

2. store businessdays adjustment convention and holidays as private property of `BusinessDate`.
The information should not get lost under `BusinessPeriod` operation.
Decide which date determines convention and holidays of a `BusinessRange`.


Contributions
-------------

.. _issues: https://github.com/pbrisk/businessdate/issues

Issues_ and `Pull Requests <https://github.com/sonntagsgesicht/businessdate/pulls>`_ are always welcome.


License
-------

.. __: https://github.com/sonntagsgesicht/businessdate/raw/master/LICENSE

Code and documentation are available according to the Apache Software License (see LICENSE__).

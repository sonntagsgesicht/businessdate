
.. module:: businessdate


---------------------
Project Documentation
---------------------

.. toctree::


.. autosummary::
    :nosignatures:

    BusinessDate
    BusinessPeriod
    BusinessDateList
    BusinessRange
    BusinessSchedule
    BusinessHolidays


Business Object Classes
=======================

BusinessDate
------------

.. module:: businessdate.businessdate

.. autoclass:: BusinessDate

.. _base_class_warning:

BusinessDate Base Classes
*************************

|BusinessDate| inherits from one of two possible base classes.
One itself inherited by a native **float** class.
The other inherited from **datetime.date** class.

Both classes are implemented to offer future releases the flexibility to switch
from one super class to another if such offers better performance.

Currently |BusinessDate| inherits from |BaseDateDatetimeDate| which offers more
elaborated functionality.

.. Warning:: Future releases of :mod:`businessdate` may be backed by different base classes.

.. module:: businessdate.basedate

.. autoclass:: BaseDateFloat
.. autoclass:: BaseDateDatetimeDate

BusinessPeriod
--------------

.. module:: businessdate.businessperiod

.. autoclass:: BusinessPeriod

BusinessSchedule
----------------

.. module:: businessdate.businessschedule

.. autoclass:: BusinessSchedule


.. module:: businessdate.businessrange

.. autoclass:: BusinessRange


BusinessHolidays
----------------

.. module:: businessdate.businessholidays

.. autoclass:: businessdate.businessholidays.TargetHolidays
.. autoclass:: BusinessHolidays


Convention Functions
====================


Day Count
---------

.. automodule:: businessdate.daycount
    :members:


Business Day Adjustment
-----------------------

.. automodule:: businessdate.conventions
    :members:

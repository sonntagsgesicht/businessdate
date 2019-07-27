
.. module:: businessdate

-----------------
API Documentation
-----------------

.. toctree::


.. autosummary::
    :nosignatures:

    BusinessDate
    BusinessPeriod
    BusinessRange
    BusinessSchedule
    BusinessHolidays


Business Object Classes
=======================

BusinessDate
------------
.. autoclass:: BusinessDate

BusinessDate Base Classes
*************************

`BusinessDate` inherits from one of two possible base classes.
One itself inherited by a native `float` class.
The other inherited from `datetime.date` class.

Both classes are implemented to offer future releases the flexibility to switch
from one super class to another if such offers better performance.

Currently `BusinessDate` inherits from `BaseDateDatetimeDate` which offers more
elaborated functionality.

.. Warning:: Future releases of `businessdate` may be backed by different base classes.


.. autoclass:: businessdate.basedate.BaseDateFloat
.. autoclass:: businessdate.basedate.BaseDateDatetimeDate

BusinessPeriod
--------------
.. autoclass:: BusinessPeriod

BusinessSchedule
----------------
.. autoclass:: BusinessSchedule
.. autoclass:: BusinessRange

BusinessHolidays
----------------
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


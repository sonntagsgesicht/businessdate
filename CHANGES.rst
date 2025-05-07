
These changes are listed in decreasing version number order.

Release 0.7.1
=============

Release date was |today|

# added more day count methods like |get_act_act_icma()|, |get_30_360_icma()|, ...

# string input to |BusinessPeriod()| e.g. `BusinessPeriod('annually)`

# negativ |BusinessPeriod()| e.g. `-BusinessPeriod(months=2)`


Release 0.7
===========

Release date was |today|


# `repr` on |BusinessDate()| shows convention, holidays and day_count if given

# added |BusinessDayCount()| and |BusinessDayAdjustment()| classes

# added auto `float` conversion to get `year_fraction` of |BusinessDate()|

# added auto `int` conversion to `YYYYMMDD` format

# added |BusinessDateList()|

# added |BusinessDate().yf()| as shortcut for |BusinessDate().get_year_fraction()|

# added |BusinessDate()| creation via construction dunder attributes like `__ts__`, `__timestamp__`, `__date__`, `__datetime__` or `.date()`  method


Release 0.6
===========

Release date was Saturday, 15 January 2022


# moved target_days into BusinessHolidays and removed businessdate.holidays

# added convention, holidays and day_count as BusinessDate arguments as well as properties

# moved to `auxilium <https://pypi.org/project/auxilium>`_, development workflow manager


Release 0.5
===========

Release date was August 1st, 2019


# first beta release (but still work in progress)

# migration to python 3.4, 3.5, 3.6 and 3.7

# automated code review

# 100% test coverage

# finished docs

# removed many calculation functions
  (BusinessDate.add_years, etc),
  better use `+` or `-` instead

# made some static methods to instance methods (BusinessDate.days_in_month, BusinessDate.end_of_month, BusinessDate.end_of_quarter)

# swapped the order of arguments in `BusinessDate.diff_in_ymd`

# new __cmp__ paradigm

# adding max_days and min_day method to `BusinessPeriod`


Release 0.4
===========

Release date was December 31th, 2017


Release 0.3
===========

Release date was July 7th, 2017


Release 0.2
===========

Release date was April 2nd, 2017


Release 0.1
===========

Release date was April 1st, 2017

Release 0.5
===========

Release date was July 31th, 2019


# migration to python 3.4, 3.5, 3.6 and 3.7

# automated code review

# 100% test coverage

# finished docs

# removed many calculation functions
  (BusinessDate.add_years, etc),
  better use `+` or `-` instead

# made some static methods to instance methods
  (BusinessDate.days_in_month, BusinessDate.end_of_month, BusinessDate.end_of_quarter)

# swapped the order of arguments in `BusinessDate.diff_in_ymd`

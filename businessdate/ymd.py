# -*- coding: utf-8 -*-

# businessdate
# ------------
# Python library for generating business dates for fast date operations
# and rich functionality.
#
# Author:   sonntagsgesicht, based on a fork of Deutsche Postbank [pbrisk]
# Version:  0.5, copyright Sunday 28 July 2019
# Website:  https://github.com/sonntagsgesicht/businessdate
# License:  Apache License 2.0 (see LICENSE file)

from datetime import date, timedelta
from math import floor

#: list(int): non-leap year number of days per month
_days_per_month = \
    [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

#: list(int): non-leap year cumulative number of days per month
_cum_month_days = \
    [0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334, 365]

#: dict: {year: (month, day)} of easter sunday dates from 1900 to 2200
_easter_dates = {
    1900: (4, 15), 1901: (4, 7), 1902: (3, 30), 1903: (4, 12), 1904: (4, 3),
    1905: (4, 23), 1906: (4, 15), 1907: (3, 31), 1908: (4, 19), 1909: (4, 11),
    1910: (3, 27), 1911: (4, 16), 1912: (4, 7), 1913: (3, 23), 1914: (4, 12),
    1915: (4, 4), 1916: (4, 23), 1917: (4, 8), 1918: (3, 31), 1919: (4, 20),
    1920: (4, 4), 1921: (3, 27), 1922: (4, 16), 1923: (4, 1), 1924: (4, 20),
    1925: (4, 12), 1926: (4, 4), 1927: (4, 17), 1928: (4, 8), 1929: (3, 31),
    1930: (4, 20), 1931: (4, 5), 1932: (3, 27), 1933: (4, 16), 1934: (4, 1),
    1935: (4, 21), 1936: (4, 12), 1937: (3, 28), 1938: (4, 17), 1939: (4, 9),
    1940: (3, 24), 1941: (4, 13), 1942: (4, 5), 1943: (4, 25), 1944: (4, 9),
    1945: (4, 1), 1946: (4, 21), 1947: (4, 6), 1948: (3, 28), 1949: (4, 17),
    1950: (4, 9), 1951: (3, 25), 1952: (4, 13), 1953: (4, 5), 1954: (4, 18),
    1955: (4, 10), 1956: (4, 1), 1957: (4, 21), 1958: (4, 6), 1959: (3, 29),
    1960: (4, 17), 1961: (4, 2), 1962: (4, 22), 1963: (4, 14), 1964: (3, 29),
    1965: (4, 18), 1966: (4, 10), 1967: (3, 26), 1968: (4, 14), 1969: (4, 6),
    1970: (3, 29), 1971: (4, 11), 1972: (4, 2), 1973: (4, 22), 1974: (4, 14), 1975: (3, 30), 1976: (4, 18),
    1977: (4, 10), 1978: (3, 26), 1979: (4, 15), 1980: (4, 6), 1981: (4, 19), 1982: (4, 11), 1983: (4, 3),
    1984: (4, 22), 1985: (4, 7), 1986: (3, 30), 1987: (4, 19), 1988: (4, 3), 1989: (3, 26), 1990: (4, 15),
    1991: (3, 31), 1992: (4, 19), 1993: (4, 11), 1994: (4, 3), 1995: (4, 16), 1996: (4, 7), 1997: (3, 30),
    1998: (4, 12), 1999: (4, 4), 2000: (4, 23), 2001: (4, 15), 2002: (3, 31), 2003: (4, 20), 2004: (4, 11),
    2005: (3, 27), 2006: (4, 16), 2007: (4, 8), 2008: (3, 23), 2009: (4, 12), 2010: (4, 4), 2011: (4, 24),
    2012: (4, 8), 2013: (3, 31), 2014: (4, 20), 2015: (4, 5), 2016: (3, 27), 2017: (4, 16), 2018: (4, 1),
    2019: (4, 21), 2020: (4, 12), 2021: (4, 4), 2022: (4, 17), 2023: (4, 9), 2024: (3, 31), 2025: (4, 20),
    2026: (4, 5), 2027: (3, 28), 2028: (4, 16), 2029: (4, 1), 2030: (4, 21), 2031: (4, 13), 2032: (3, 28),
    2033: (4, 17), 2034: (4, 9), 2035: (3, 25), 2036: (4, 13), 2037: (4, 5), 2038: (4, 25), 2039: (4, 10),
    2040: (4, 1), 2041: (4, 21), 2042: (4, 6), 2043: (3, 29), 2044: (4, 17), 2045: (4, 9), 2046: (3, 25),
    2047: (4, 14), 2048: (4, 5), 2049: (4, 18), 2050: (4, 10), 2051: (4, 2), 2052: (4, 21), 2053: (4, 6),
    2054: (3, 29), 2055: (4, 18), 2056: (4, 2), 2057: (4, 22), 2058: (4, 14), 2059: (3, 30), 2060: (4, 18),
    2061: (4, 10), 2062: (3, 26), 2063: (4, 15), 2064: (4, 6), 2065: (3, 29), 2066: (4, 11), 2067: (4, 3),
    2068: (4, 22), 2069: (4, 14), 2070: (3, 30), 2071: (4, 19), 2072: (4, 10), 2073: (3, 26),
    2074: (4, 15), 2075: (4, 7), 2076: (4, 19), 2077: (4, 11), 2078: (4, 3), 2079: (4, 23), 2080: (4, 7),
    2081: (3, 30), 2082: (4, 19), 2083: (4, 4), 2084: (3, 26), 2085: (4, 15), 2086: (3, 31), 2087: (4, 20),
    2088: (4, 11), 2089: (4, 3), 2090: (4, 16), 2091: (4, 8), 2092: (3, 30), 2093: (4, 12), 2094: (4, 4), 2095: (4, 24),
    2096: (4, 15), 2097: (3, 31), 2098: (4, 20), 2099: (4, 12), 2100: (3, 28), 2101: (4, 17), 2102: (4, 9),
    2103: (3, 25), 2104: (4, 13), 2105: (4, 5), 2106: (4, 18), 2107: (4, 10), 2108: (4, 1), 2109: (4, 21),
    2110: (4, 6), 2111: (3, 29), 2112: (4, 17), 2113: (4, 2), 2114: (4, 22), 2115: (4, 14), 2116: (3, 29),
    2117: (4, 18), 2118: (4, 10), 2119: (3, 26), 2120: (4, 14), 2121: (4, 6), 2122: (3, 29), 2123: (4, 11),
    2124: (4, 2), 2125: (4, 22), 2126: (4, 14), 2127: (3, 30), 2128: (4, 18), 2129: (4, 10), 2130: (3, 26),
    2131: (4, 15), 2132: (4, 6), 2133: (4, 19), 2134: (4, 11), 2135: (4, 3), 2136: (4, 22), 2137: (4, 7),
    2138: (3, 30), 2139: (4, 19), 2140: (4, 3), 2141: (3, 26), 2142: (4, 15), 2143: (3, 31), 2144: (4, 19),
    2145: (4, 11), 2146: (4, 3), 2147: (4, 16), 2148: (4, 7), 2149: (3, 30), 2150: (4, 12), 2151: (4, 4),
    2152: (4, 23), 2153: (4, 15), 2154: (3, 31), 2155: (4, 20), 2156: (4, 11), 2157: (3, 27),
    2158: (4, 16), 2159: (4, 8), 2160: (3, 23), 2161: (4, 12), 2162: (4, 4), 2163: (4, 24), 2164: (4, 8),
    2165: (3, 31), 2166: (4, 20), 2167: (4, 5), 2168: (3, 27), 2169: (4, 16), 2170: (4, 1), 2171: (4, 21),
    2172: (4, 12), 2173: (4, 4), 2174: (4, 17), 2175: (4, 9), 2176: (3, 31), 2177: (4, 20), 2178: (4, 5), 2179: (3, 28),
    2180: (4, 16), 2181: (4, 1), 2182: (4, 21), 2183: (4, 13), 2184: (3, 28), 2185: (4, 17), 2186: (4, 9),
    2187: (3, 25), 2188: (4, 13), 2189: (4, 5), 2190: (4, 25), 2191: (4, 10), 2192: (4, 1), 2193: (4, 21),
    2194: (4, 6), 2195: (3, 29), 2196: (4, 17), 2197: (4, 9), 2198: (3, 25), 2199: (4, 14), 2200: (4, 6)
}


def is_leap_year(year):
    """
    returns True for leap year and False otherwise

    :param int year: calendar year
    :return bool:
    """
    # return (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0)
    return year % 100 != 0 or year % 400 == 0 if year % 4 == 0 else False


def days_in_year(year):
    """
        returns number of days in the given calendar year

        :param int year: calendar year
        :return int:
        """

    return 366 if is_leap_year(year) else 365


def days_in_month(year, month):
    """
    returns number of days for the given year and month

    :param int year: calendar year
    :param int month: calendar month
    :return int:
    """

    eom = _days_per_month[month - 1]
    if is_leap_year(year) and month == 2:
        eom += 1

    return eom


def end_of_quarter_month(month):
    """
    method to return last month of quarter

    :param int month:
    :return: int
    """
    while month % 3:
        month += 1
    return month


def is_valid_ymd(year, month, day):
    """
    return True if (year,month, day) can be represented in Excel-notation
    (number of days since 30.12.1899) for calendar days, otherwise False

    :param int year: calendar year
    :param int month: calendar month
    :param int day: calendar day
    :return bool:
    """

    return 1 <= month <= 12 and 1 <= day <= days_in_month(year, month) and year >= 1899


def from_excel_to_ymd(excel_int):
    """
    converts date in Microsoft Excel representation style and returns `(year, month, day)` tuple

    :param int excel_int: date as int (days since 1899-12-31)
    :return tuple(int, int, int):
    """

    int_date = int(floor(excel_int))
    int_date -= 1 if excel_int > 60 else 0
    # jd: There are two errors in excels own date <> int conversion.
    # The first is that there exists the 00.01.1900 and the second that there never happened to be a 29.2.1900 since it
    # was no leap year. So there is the int 60 <> 29.2.1900 which has to be jumped over.

    year = (int_date - 1) // 365
    rest_days = int_date - 365 * year - (year + 3) // 4 + (year + 99) // 100 - (year + 299) // 400
    year += 1900

    while rest_days <= 0:
        year -= 1
        rest_days += days_in_year(year)

    month = 1
    if is_leap_year(year) and rest_days == 60:
        month = 2
        day = 29
    else:
        if is_leap_year(year) and rest_days > 60:
            rest_days -= 1

        while rest_days > _cum_month_days[month]:
            month += 1

        day = rest_days - _cum_month_days[month - 1]
    return year, month, day


def from_ymd_to_excel(year, month, day):
    """
    converts date as `year, month, day` tuple into Microsoft Excel representation style

    :param int year:
    :param int month:
    :param int day:
    :return int:
    """
    if not is_valid_ymd(year, month, day):
        raise ValueError("Invalid date {0}.{1}.{2}".format(year, month, day))

    days = _cum_month_days[month - 1] + day
    days += 1 if (is_leap_year(year) and month > 2) else 0

    years_distance = year - 1900
    days += \
        years_distance * 365 + (years_distance + 3) // 4 - (years_distance + 99) // 100 + (years_distance + 299) // 400

    # count days since 30.12.1899 (excluding 30.12.1899) (workaround for excel bug)
    days += 1 if (year, month, day) > (1900, 2, 28) else 0
    return days


def target_days(year):
    ret = dict()
    ret[date(year, 1, 1)] = "New Year's Day"
    month, day = _easter_dates[year]
    e = date(year, month, day)
    ret[e - timedelta(2)] = "Black Friday"
    ret[e + timedelta(1)] = "Easter Monday"
    ret[date(year, 5, 1)] = "Labour Day"
    ret[date(year, 12, 25)] = "First Christmas Day"
    ret[date(year, 12, 26)] = "Second Christmas Day"
    return ret

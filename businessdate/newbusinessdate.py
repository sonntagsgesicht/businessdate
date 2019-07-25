"""

behavior of a NewBusinessDate object which consists of a (datetime, period, holidays) tuple

"""

'''
BusinessDate(20091231) -> date, period('0D')
BusinessDate('1m') -> None, period('1M')
BusinessDate('0b3Y2M1D2BMODFOLLOW20091231TAR') ->
    bd = date(20091231)         # default on BASE_DATE
    bd += period('0b')          # ignored on default
    bd.adjust_mod_follow(TAR)   # no adjust on default, ignored if previous period is ignored
    bd += period('3Y2M1D')      # ignored on default, equivalent to '0D'
    bd += period('2b')          # ignored on default
    bd.adjust_mod_follow(TAR)   # no adjust on default, ignored if previous period is ignored

dp + dp = fail
dp + np = dp
dp - np = dp
dp - dp = np


d+d=fail
p+d=fail
d+p=d
p+p=p

d-d=p
p-d=fail
d-p=d
p-p=p


'''


from .basedate import BaseDate, BaseDateFloat, BaseDateDatetimeDate
from businessdate import BusinessDate, BusinessPeriod, BusinessHolidays


class AdjustedBusinessDate(BusinessDate):

    @property
    def business_date(self):
        # init date
        start, mid, end = self._periods
        adjust = lambda bd: bd.adjust(self._adjust_convention, self._holidays)

        res = self if start is None else adjust(self+start)
        res += mid
        res = res if end is None else adjust(self+end)
        return res

    def __init__(self, date_value=None, *args):
        if args:
            month, day = args
            self._origin = BusinessDate(date_value, month, day)
    #def __init__(self, base_date=None, start_offset=None, period=None, end_offset=None, adjust='', holidays=(), origin=None):
        #origin = BusinessDate.BASE_DATE if origin is None else origin
        #super(AdjustedBusinessDate, self).__init__(origin.year, origin.month, origin.day)
        super(AdjustedBusinessDate, self).__init__(self._origin.year, self._origin.month, self._origin.day)
        #self._periods = start_offset, period, end_offset
        #self._adjust_convention = adjust
        # self._holidays = holidays
        self._periods = '','',''
        self._adjust_convention = ''
        self._holidays = ()

    def to_string(self, date_format=None):
        start, mid, end = self._periods
        s = ''
        s += '' if start is None else str(start)
        s += '' if mid is None else str(mid)
        s += '' if end is None else str(end)
        s += '' if self._adjust_convention is None else self._adjust_convention
        s += '' if self._origin is None else self._origin.to_string()
        s += '' if not self._holidays else str(self._holidays)
        return s

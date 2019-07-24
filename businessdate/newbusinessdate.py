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


from datetime import date

_BASE_DATE = date.today()


class NewBusinessDate(object):

    _base_date = _BASE_DATE

    @property
    def dp(self):
        return self._date, self._period

    def __init__(self, *args):
        self._date = None
        self._period = ''
        self._holidays = list()
        self._base_date = self.__class__._base_date

        self._origin = None
        self._period = BusinessPeriod()

        try:
            self._period = BusinessPeriod(*args, **kwargs)
        except TypeError:
            pass
        except ValueError:
            pass

        try:
            self._origin = BusinessDate(*args, **kwargs)
        except TypeError:
            pass
        except ValueError:
            pass

    def __str__(self):
        return str(self._origin if self._origin else '') + str(self._period)

    def __getattr__(self, item):
        #print self, item
        o, p = hasattr(self._origin, item), hasattr(self._period, item)
        print(o+p)
        if o and p:
            o, p = getattr(self._origin, item, None), getattr(self._period, item, None)
            print (type(o), type(p))

            def attr(*args, **kwargs):
                try:
                    return o(*args, **kwargs)
                except:
                    pass
                try:
                    return p(*args, **kwargs)
                except:
                    pass
            return attr

        elif o:
            return getattr(self._origin, item)

        elif p:
            return getattr(self._period, item)

        else:
            return None

    def __add__(self, other):
        d, p = other.dp
        if d is None:  # or d is self._date:
            return NewBusinessDate((self._date, self._period + p))
        else:
            raise ValueError()

    def __sub__(self, other):
        d, p = other.dp
        if d is None:
            return NewBusinessDate((self._date, self._period-p))
        else:
            return NewBusinessDate((None, self.as_date() - other.as_date()))

    def __mul__(self, other):
        if isinstance(other, int):
            return NewBusinessDate(self._date, self._period * other)
        else:
            raise ValueError()

    def __div__(self, other):
        if isinstance(other, int):
            return NewBusinessDate(self._date, self._period / other)
        else:
            raise ValueError()


dp = NewBusinessDate()

assert dp.date is None
assert dp.period == ''
assert dp.holidays == list()
assert dp.basedate == date.today()
assert dp.as_date == dp.basedate

assert dp + date()

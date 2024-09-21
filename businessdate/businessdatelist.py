# -*- coding: utf-8 -*-

# businessdate
# ------------
# Python library for generating business dates for fast date operations
# and rich functionality.
#
# Author:   sonntagsgesicht, based on a fork of Deutsche Postbank [pbrisk]
# Version:  0.5, copyright Wednesday, 18 September 2019
# Website:  https://github.com/sonntagsgesicht/businessdate
# License:  Apache License 2.0 (see LICENSE file)

from .businessdate import BusinessDate


class BusinessDateList(list):

    def __getitem__(self, key):
        if isinstance(key, int):
            # use default behavior
            return super().__getitem__(key)

        if isinstance(key, float):
            # get all entries of given year fraction
            return [v for v in self if float(v) == key]

        if not isinstance(key, slice):
            key = BusinessDate(key)
            return [v for v in self if BusinessDate(v) == key]

        if (isinstance(key.start, int) or
                isinstance(key.stop, int) or
                isinstance(key.step, int)):
            # use default slice behavior
            return self.__class__(super().__getitem__(key))

        if key.step:
            cls = key.step.__class__.__name__
            raise ValueError(f"slice steps of type {cls} do not work")

        if isinstance(key.start, float) or isinstance(key.stop, float):
            func = float
        else:
            func = BusinessDate

        if key.start and not isinstance(key.start, float):
            key = slice(BusinessDate(key.start), key.stop)

        if key.stop and not isinstance(key.stop, float):
            key = slice(key.start, BusinessDate(key.stop))

        if key.start and key.stop:
            r = (v for v in self if key.start <= func(v) < key.stop)
        elif key.start:
            r = (v for v in self if key.start <= func(v))
        elif key.stop:
            r = (v for v in self if func(v) < key.stop)
        else:
            r = self
        return self.__class__(r)

    def __str__(self):
        return f"[{', '.join(str(v) for v in list(self))}]"

    def dict(self):
        r = {}
        for v in self:
            k = BusinessDate(v)
            r[k] = r.get(k, [])
            r[k].append(v)
        return r

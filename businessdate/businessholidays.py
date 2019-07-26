from datetime import date

from holidays import target_days
# from businessdate import BusinessDate


class BusinessHolidays(list):
    """
    holiday calendar class
    """
    # def __init__(self, iterable=()):
    #     if iterable:
    #         iterable = [bd.to_date() for bd in map(BusinessDate, iterable)]
    #     super(BusinessHolidays, self).__init__(iterable)

    def __contains__(self, item):
        if super(BusinessHolidays, self).__contains__(item):
            return True
        return super(BusinessHolidays, self).__contains__(date(item.year, item.month, item.day))


class TargetHolidays(BusinessHolidays):
    """
    holiday calendar class for ecb target2 holidays
    """

    def __contains__(self, item):
        if not super(TargetHolidays, self).__contains__(date(item.year, 1, 1)):
            # add tar days if not done jet
            self.extend(target_days(item.year).keys())
        return super(TargetHolidays, self).__contains__(item)
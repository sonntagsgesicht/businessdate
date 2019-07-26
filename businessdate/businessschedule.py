from businessdate import BusinessDate, BusinessPeriod
from businessrange import BusinessRange


class BusinessSchedule(BusinessRange):
    def __init__(self, start, end, step, roll=None):
        """
        class to build date schedules incl. start and end date

        :param BusinessDate start: start date of schedule
        :param BusinessDate end: end date of schedule
        :param BusinessPeriod step: period distance of two dates
        :param BusinessDate roll: origin of schedule

        convenient class to build date schedules
        a schedule includes always start and end date
        and rolls on roll, i.e. builds a sequence by
        adding and/or substracting step to/from roll.
        start and end slice the relevant dates.
        """
        roll = roll if roll else end
        start, end = map(BusinessDate, (start, end))
        super(BusinessSchedule, self).__init__(start, end, step, roll)
        if start not in self:
            self.insert(0, start)
        if end not in self:
            self.append(end)

    def first_stub_long(self):
        if len(self) > 2:
            self.pop(1)
        return self

    def last_stub_long(self):
        if len(self) > 2:
            self.pop(-2)
        return self

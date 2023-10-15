from gym_manager_api import models
import datetime
import pandas as pd

class Calendar:

    def __init__(self) -> None:
        self.dates = {}
        pass

    def load_dates_in_range(self, first: datetime.datetime, last: datetime.datetime,
                            group:int=None, generate_events=False) -> dict:
        """
        to view calendar by day, week, month etc
        will return a set of dates that happen between input dates. for all group or specific
        one if provided
        e.g. {'pole exotic': DatetimeIndex(['2023-10-02', '2023-10-09'], dtype='datetime64[ns]', freq='W-MON')}
        """
        max_last = (datetime.datetime.now() + datetime.timedelta(weeks=48)).date()
        if last > max_last:
            last = max_last

        if group:
            schedulers = models.Scheduler.objects.filter(group=group).filter(first__lt=last)
        else:
            schedulers = models.Scheduler.objects.filter(first__lt=last)

        if len(schedulers) == 0:
            # TODO  this cant stay like this
            raise Exception('no schedulers')

        dates = {}
        for scheduler in schedulers:
            dates.update(scheduler.get_dates_in_range(first, last, generate_events))
            self.dates = dates
        return dates

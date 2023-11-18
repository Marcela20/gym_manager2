from gym_manager_api import models
import datetime


class Scheduler:

    def __init__(self) -> None:
        self.dates = {}
        pass

    def load_dates_in_range(self, first: datetime.datetime, last: datetime.datetime,
                            group:int=None, generate_events=False) -> dict:

        max_last = (first + datetime.timedelta(weeks=48))
        if last > max_last:
            last = max_last

        if group:
            schedulers = models.Scheduler.objects.filter(group=group).filter(first__lt=last)
        else:
            schedulers = models.Scheduler.objects.filter(first__lt=last)

        if len(schedulers) == 0:
            # TODO  this cant stay like this
            return []

        dates = []
        for scheduler in schedulers:
            dates += scheduler.get_dates_in_range(first, last, generate_events)
            self.dates = dates
        return dates

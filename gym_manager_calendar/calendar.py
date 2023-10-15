from gym_manager_api import models
import pandas as pd
import datetime
class Calendar:

    def __init__(self) -> None:
        pass
    
    def load_events_in_range_by_group(cls, first, last):
        print(first, last)
        max_last = (datetime.datetime.now() + datetime.timedelta(weeks=48)).date()
        if last > max_last:
            last = max_last

        schedulers = models.Scheduler.objects.filter(first__lt=last).filter(last__gt=first)
        if len(schedulers) == 0:
            # TODO  this cant stay like this
            raise Exception('no schedulers')

        events = {}
        for scheduler in schedulers:
            if not scheduler.get_dates_in_range(first, last):
                continue

            events.update(scheduler.get_dates_in_range(first, last))
        
        return events
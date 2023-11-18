from .scheduler import Scheduler
import datetime
from django.http import JsonResponse
import pytz


def scheduler(request):
    """
    1. from currentDate extract start date of a view
    """

    start_date_str = int(request.GET.get('startDate'))/1000
    start_date = datetime.datetime.fromtimestamp(start_date_str)

    end_date_str = int(request.GET.get('endDate'))/1000
    end_date = datetime.datetime.fromtimestamp(end_date_str)

    utc = pytz.UTC
    scheduler = Scheduler()
    dates = scheduler.load_dates_in_range(
        utc.localize(start_date),
        utc.localize(end_date), generate_events=False
    )
    response = JsonResponse(dates, safe=False)

    return response
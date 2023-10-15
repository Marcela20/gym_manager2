from .calendar import Calendar
import datetime
from django.http import HttpResponse


def calendar(request):
    calendar = Calendar()
    a = calendar.load_events_in_range_by_group(datetime.date(2022, 10, 10), datetime.datetime.now().date())
    return HttpResponse("<html><body> %s </body></html>" %a)
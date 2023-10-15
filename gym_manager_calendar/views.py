from .calendar import Calendar
import datetime
from django.http import HttpResponse


def calendar(request):
    calendar = Calendar()
    a = calendar.load_dates_in_range(datetime.date(2023, 10, 1),
                                     datetime.datetime.now().date(), 3, True)
    return HttpResponse("<html><body> %s </body></html>" %a)
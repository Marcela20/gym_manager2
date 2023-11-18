
from django.http import JsonResponse, HttpResponse
from gym_manager_api import models


def attendance(request):
    group_id = request.GET.get('group_id')
    group = models.Group.objects.get(id=int(group_id))
    dates = group.get_all_dates()
    dates.reset_index(inplace=True)
    dates = dates.to_dict('records')
    response = JsonResponse(dates, safe=False)

    return response
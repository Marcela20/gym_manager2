from gym_manager_api import models
from rest_framework.views import APIView
from rest_framework.response import Response

class StudentsGroup(APIView):

    def post(self, request):
        data = request.data
        group_id = request.GET.get('group_id')
        group = models.Group.objects.get(pk=group_id)
        for scheduler_id, students in data.items():
            if scheduler_id == "all days":
                for student in students:
                    for scheduler in group.whereabouts.all():
                        scheduler.students.add(student["id"])
            else:
                scheduler = models.Scheduler.objects.get(pk=scheduler_id)
                for student in students:
                    scheduler.students.add(student["id"])
        return Response(status=200)


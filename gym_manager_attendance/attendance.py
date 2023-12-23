from django.http import JsonResponse
from rest_framework.views import APIView
from gym_manager_api.models import (Attendance, Group, Student, Scheduler)
from rest_framework.response import Response
from datetime import datetime
import pandas as pd


def get_dates_as_columns(request):
    group_id = request.GET.get('group_id')
    group = Group.objects.get(id=int(group_id))
    dates = group.all_dates
    dates.index.name = 'field'
    dates = dates.reset_index()
    dates = dates.T
    dates = dates.to_dict().values()
    resp = [{"field": "index"}]
    [resp.append(date) for date in dates]
    response = JsonResponse(resp, safe=False)
    return response


def get_group_attendance(group_id):
    group = Group.objects.get(id=int(group_id))
    attendance = group.attendance.all()
    for a in attendance:
        print(a.is_paid)
    students = group.students_list
    sub = students[0].subscription.all()[0]
    data = [{'index': a.student.full_name, 'id': a.student.id, a.date.strftime('%a %d/%m/%Y'): a.state, 'paid':a.is_paid} for a in attendance]
    [data.append({'index': student.full_name, 'id': student.id}) for student in students]
    if data:
        df = pd.DataFrame(data).set_index('index').groupby(level=0).agg('first')
        df =  df.reset_index().to_dict('records')
        return df
    return []


class AttendanceCheker(APIView):
    queryset = Attendance.objects.all()

    def get(self, request, format=None):
        group_id = request.GET.get('group_id')
        response = get_group_attendance(group_id)
        return JsonResponse(response, safe=False)

    def post(self, request, format=None):
        added_attendance = request.data
        group_id = request.GET.get('group_id')
        group = Group.objects.get(id=int(group_id))
        for student_id, dates in added_attendance.items():
            for date, state in dates.items():
                scheduler_id = dates["scheduler_id"]
                if date in ("id", "index", "scheduler_id"):
                    continue

                scheduler = Scheduler.objects.get(id=int(scheduler_id))
                attendance = Attendance.objects.get_or_create(
                    group=group,
                    scheduler=scheduler,
                    student=Student(pk=student_id),
                    date=datetime.strptime(date, '%a %d/%m/%Y'))[0]

                attendance.state = state
                attendance.save()
                group.attendance.add(attendance)

        # TODO will return 200 even if there was some error
        return Response(status=200)
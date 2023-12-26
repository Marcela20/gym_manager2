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
    dates = group.all_dates
    students = group.students_list
    rows = []
    for student in students:
        values = {
            row[0] :{
                "text": student.check_attendance(
                    datetime.strptime(row[0],'%a %d/%m/%Y').date(), row[1]
                    ),
                "paid": student.can_attend(
                    datetime.strptime(row[0], '%a %d/%m/%Y').date(), row[1]
                    )} for row in dates.itertuples(index=True)}
        data = {'index': student.full_name, 'id': student.id}
        data.update(values)
        rows.append(data)

    df = pd.DataFrame(rows).set_index('index').groupby(level=0).agg('first')
    df =  df.reset_index().to_dict('records')
    return df


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
            for date, values in dates.items():
                scheduler_id = values["scheduler_id"]
                scheduler = Scheduler.objects.get(id=int(scheduler_id))
                attendance = Attendance.objects.get_or_create(
                    group=group,
                    scheduler=scheduler,
                    student=Student(pk=student_id),
                    date=datetime.strptime(date, '%a %d/%m/%Y').date())[0]
                if values['text'] in ["PRE", "ABS"]:
                    attendance.state = values['text']
                else:
                        raise Exception(f"cant set {values['text']} as state")
                attendance.remove_entrance_from_subscription(values['text'])
                attendance.save()
                group.attendance.add(attendance)

        # TODO will return 200 even if there was some error
        return Response(status=200)
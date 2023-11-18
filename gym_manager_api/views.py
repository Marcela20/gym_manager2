from .models import (Group, Student, Instructor, Classroom, Scheduler, Event, EventException)
from rest_framework import viewsets
from rest_framework import permissions
from .serializers import (SchedulerCreateSerializer, GroupViewSerializer,GroupCreateSerializer, ClassroomViewSerializer, StudentViewSerializer, InstructorViewSerializer, SchedulerViewSerializer, EventViewSerializer)
from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from datetime import datetime
from dateutil import parser

class GroupWithSchedulers(APIView):

    queryset = Group.objects.all()

    def post(self, request, format=None):
        #TODO this function needs to be fixed to create all object or none
        data = request.data
        group_serializer = GroupCreateSerializer(data=data)
        if group_serializer.is_valid():
            group = group_serializer.save()
        else:
            return Response(status=404, data=group_serializer.error_messages)
        for item in data.get("items"):
            item_data = {}
            end = parser.parse(item["end_time"])
            start = parser.parse(item["start_time"])
            duration = end - start
            item_data.update({"duration": duration,
                              "first": data["first"],
                              "last": data["last"],
                              "repeat_on": item["repeat_on"],
                              "classroom": item["location"]["id"],
                              "instructor": item["instructor"]["id"],
                              "group": group.id
                              })
            print(item_data)
            scheduler_serializer = SchedulerCreateSerializer(data=item_data)

            if scheduler_serializer.is_valid():
                scheduler_serializer.save()
            else:
                print(scheduler_serializer.errors)
                return Response(status=404, data=scheduler_serializer.error_messages)



        return Response(status=200)


class GroupViewSet(APIView):

    queryset = Group.objects.all()
    def get(self, request, format=None):
        queryset = Group.objects.all()
        serializer = GroupViewSerializer(queryset, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        data = request.data
        serializer = GroupCreateSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(status=200)
        return Response(status=400, data=serializer.error_messages)

class StudentViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentViewSerializer
    # permission_classes = [permissions.IsAuthenticated]


class InstructorViewSet(viewsets.ModelViewSet):
    queryset = Instructor.objects.all()
    serializer_class = InstructorViewSerializer
    # permission_classes = [permissions.IsAuthenticated]


class ClassroomViewSet(viewsets.ModelViewSet):
    queryset = Classroom.objects.all()
    serializer_class = ClassroomViewSerializer
    # permission_classes = [permissions.IsAuthenticated]


class SchedulerViewSet(viewsets.ModelViewSet):
    queryset = Scheduler.objects.all()
    serializer_class = SchedulerViewSerializer
    permission_classes = [permissions.IsAuthenticated]


class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventViewSerializer
    permission_classes = [permissions.IsAuthenticated]


class EventExceptionViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventException
    permission_classes = [permissions.IsAuthenticated]
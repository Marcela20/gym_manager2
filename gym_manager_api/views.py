from .models import (Group, Student, Instructor, Classroom, Scheduler, Event, EventException)
from rest_framework import viewsets
from rest_framework import permissions
from .serializers import (GroupViewSerializer, ClassroomViewSerializer, StudentViewSerializer, InstructorViewSerializer, SchedulerViewSerializer, EventViewSerializer)


class GroupViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupViewSerializer
    permission_classes = [permissions.IsAuthenticated]


class StudentViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentViewSerializer
    permission_classes = [permissions.IsAuthenticated]


class InstructorViewSet(viewsets.ModelViewSet):
    queryset = Instructor.objects.all()
    serializer_class = InstructorViewSerializer
    permission_classes = [permissions.IsAuthenticated]


class ClassroomViewSet(viewsets.ModelViewSet):
    queryset = Classroom.objects.all()
    serializer_class = ClassroomViewSerializer
    permission_classes = [permissions.IsAuthenticated]


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
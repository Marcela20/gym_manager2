from .models import (Group, Student, Instructor, Classroom, Scheduler, Event, EventException)
from rest_framework import serializers


class GroupViewSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ['name', 'whereabouts', 'students']


class InstructorViewSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Instructor
        fields = ['name', 'second_name', 'phone_number']


class StudentViewSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Student
        fields = ['name', 'second_name', 'phone_number']


class ClassroomViewSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Classroom
        fields = ['name']


class SchedulerViewSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Scheduler
        fields = ['first', 'last', 'repeat_on', 'hour', 'classroom', 'instructor']



class EventViewSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Event
        fields = ['date', 'hour', 'group', 'instructor', 'attendees']


class EventExceptionViewSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = EventException
        fields = ['move_from', 'move_to',  'group', 'instructor', 'attendees']
from .models import (Group, Student, Instructor, Classroom,
                     Scheduler, Event, EventException, Attendance)
from rest_framework import serializers



class GroupViewSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ['id', 'name', 'time_and_place', 'instructors', 'classrooms', 'repeats_on']

class GroupCreateSerializer(serializers.Serializer):
    name = serializers.CharField()
    def create(self, validated_data):
        group = Group(**validated_data)
        group.save()
        return group

class SchedulerCreateSerializer(serializers.Serializer):
    first = serializers.DateTimeField()
    last = serializers.DateTimeField()
    start_hour = serializers.TimeField()
    duration = serializers.DurationField()
    repeat_on = serializers.CharField()
    classroom = serializers.PrimaryKeyRelatedField(queryset=Classroom.objects.all())
    instructor = serializers.PrimaryKeyRelatedField(queryset=Instructor.objects.all())
    group = serializers.PrimaryKeyRelatedField(queryset=Group.objects.all())


    def create(self, validated_data):
        scheduler = Scheduler(**validated_data)
        scheduler.save()

        return scheduler


class InstructorViewSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Instructor
        fields = ['id', 'name', 'second_name', 'phone_number', 'full_name']


class StudentViewSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Student
        fields = ['id', 'name', 'second_name', 'phone_number']


class ClassroomViewSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Classroom
        fields = ['id', 'name']


class SchedulerViewSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Scheduler
        fields = ['first', 'duration', 'last', 'repeat_on', 'classroom', 'instructor', 'students']



class EventViewSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Event
        fields = ['date', 'end_date', 'group', 'instructor', 'attendees', 'classroom']


class EventExceptionViewSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = EventException
        fields = ['move_from', 'move_to',  'group', 'instructor', 'attendees']


class AttendanceViewSerializer(serializers.Serializer):
    state = serializers.CharField()
    group = serializers.PrimaryKeyRelatedField(queryset=Group.objects.all())
    student = serializers.PrimaryKeyRelatedField(queryset=Student.objects.all())
    date = serializers.DateField()


    def create(self, validated_data):
        attendance = Attendance(**validated_data)
        attendance.save()
        return attendance
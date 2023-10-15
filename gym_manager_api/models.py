from django.db import models
from .validators import phone_number_validator
import datetime
from django.utils import timezone
import pandas as pd


class User(models.Model):
    class Role(models.IntegerChoices):
        student = 0
        instructor = 1

    name = models.CharField(max_length=25)
    second_name = models.CharField(max_length=25)
    phone_number = models.CharField(max_length=15, validators=[phone_number_validator])    


class Student(User):
    role = models.CharField(default='student', max_length=25)


class Instructor(User):
    role = models.CharField(default='instructor', max_length=25)


class Classroom(models.Model):
    name = models.CharField(max_length=25)


class Scheduler(models.Model):
    
    DAYS = [
        ("MON", "Monday"),
        ("TUE", "Tuesday"),
        ("WED", "Wednesday"),
        ("THR", "Thursday"),
        ("FRI", "Friday"),
        ("SAT", "Saturday"),
        ("SUN", "Sunday"),
    ]
    hour = models.TimeField(blank=False, null=False, default=datetime.time(10, 30))
    first = models.DateField(null=False, blank=False, default=timezone.now)
    last = models.DateField(null=True, blank=True)
    repeat_on = models.CharField(
        max_length=3,
        choices=DAYS,
        null=True
    )
    classroom = models.ManyToManyField(Classroom)
    instructor = models.ManyToManyField(Instructor)

    def get_all_dates(self):

        last = self.last or (datetime.datetime.now() + datetime.timedelta(weeks=48)).date()

        return {f'{self.group.all()[0]}':pd.date_range(start=self.first, end=last,
                freq=f'W-{self.repeat_on}')}
    
    def get_dates_in_range(self, first, last):
        if first > self.last or self.last< first:
            return
        
        if self.first > first and last < self.last: 
            first = self.first
            last = self.last

        elif self.first > first and self.last < last:
            first = self.first
        
        return {f'{self.group.all()[0]}':pd.date_range(start=first, end=last,
                freq=f'W-{self.repeat_on}')}


class Group(models.Model):
    name = models.CharField(max_length=25)
    whereabouts = models.ManyToManyField(Scheduler, related_name='group')
    students = models.ManyToManyField(Student)

    def __str__(self) -> str:
        return self.name


class Event(models.Model):
    date = models.DateTimeField(null=True, blank=True)
    group = models.ManyToManyField(Group)
    instructor = models.ManyToManyField(Instructor)
    attendees = models.ManyToManyField(Student)


class EventException(models.Model):
    move_from  = models.DateTimeField(null=False, blank=False, default=timezone.now)
    move_to = models.DateTimeField(null=False, blank=False, default=timezone.now)
    group = models.ManyToManyField(Group)
    instructor = models.ManyToManyField(Instructor)
    attendees = models.ManyToManyField(Student)

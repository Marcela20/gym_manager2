from django.db import (models, IntegrityError)
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


class Group(models.Model):
    name = models.CharField(max_length=25)
    students = models.ManyToManyField(Student)

    def __str__(self) -> str:
        return self.name


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
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='whereabouts', null=True, blank=True)

    def get_all_dates(self, generate_events=False):

        last = self.last or (datetime.datetime.now() + datetime.timedelta(weeks=48)).date()

        dates = pd.date_range(start=self.first, end=last, freq=f'W-{self.repeat_on}')
        if generate_events:
            for date in dates:
                    print(date)

        return {f'{self.group.all()[0]}':dates}

    def create_event(self, date):
        print(Event.objects.get(date=date, hour=self.hour, group=self.group))
        try:
            e = Event.objects.create(date=date, hour=self.hour, group=self.group)
            e.instructor.set(self.instructor.all())
            e.attendees.set(self.group.students.all())
            e.save()
        except IntegrityError:
            pass

    def get_dates_in_range(self, first: datetime.datetime, last: datetime.datetime,
                           generate_events=False):
        """
        will return dates in between first and last for this scheduler as a dict
        """
        if not self.last:
            self.last = last

        if first > self.last or self.last< first:
            return {}

        if self.first > first and last < self.last:
            first = self.first
            last = self.last

        elif self.first > first and self.last < last:
            first = self.first

        if self.group:
            dates = pd.date_range(start=first, end=last,freq=f'W-{self.repeat_on}')
            if generate_events:
                for date in dates:
                    self.create_event(date)

            return {f'{self.group}': dates}

        return {}


class Event(models.Model):
    date = models.DateTimeField(null=True, blank=True)
    hour = models.TimeField(blank=False, null=False, default=datetime.time(10, 30))
    group = models.ForeignKey(Group, on_delete=models.CASCADE, null=True, blank=True)
    instructor = models.ManyToManyField(Instructor)
    attendees = models.ManyToManyField(Student)
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['date', 'hour', 'group'], name='unique_event'
            )
        ]


class EventException(models.Model):
    move_from  = models.DateTimeField(null=False, blank=False, default=timezone.now)
    move_to = models.DateTimeField(null=False, blank=False, default=timezone.now)
    group = models.ManyToManyField(Group)
    instructor = models.ManyToManyField(Instructor)
    attendees = models.ManyToManyField(Student)

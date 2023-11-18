from django.db import (models, IntegrityError)
from .validators import phone_number_validator
import datetime
from django.utils import timezone
import pandas as pd
import pytz

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
    def __str__(self) -> str:
        return self.name
    @property
    def full_name(self):
        return f"{self.name} {self.second_name}"


class Classroom(models.Model):
    name = models.CharField(max_length=25)
    def __str__(self) -> str:
        return self.name

class Group(models.Model):
    name = models.CharField(max_length=25)
    students = models.ManyToManyField(Student)

    def _get_time_from_datetime(self, date_time:datetime.datetime):
        return date_time.strftime("%H:%M")

    @property
    def students_list(self):
        students = []
        for student in self.students.all():
            students.append(f"{student.name} {student.second_name}")
        return students



    def get_all_dates(self):
        schedulers = self.whereabouts.all()
        dates = schedulers[0].get_all_dates()
        students = self.students_list

        df1 = pd.DataFrame(index=dates, columns=students)


        if len(schedulers)>1:
            for entry in schedulers[1:]:
                entry_dates = entry.get_all_dates()
                df2 = pd.DataFrame(index=entry_dates, columns=students)
                df1 = pd.concat([df1,df2], join='inner', axis=0)
        df1 = df1.sort_index()
        df1 = df1.fillna("hi")
        df1.index = df1.index.strftime('%a %d/%m/%Y')
        return df1.T


    @property
    def _get_group_data(self):
        schedulers = self.whereabouts.all()
        instructors = set()
        classrooms = set()
        time_and_place = set()

        for entry in schedulers:
            try:
                instructors.add(f"{entry.instructor.name} {entry.instructor.second_name}")
            except AttributeError:
                pass
            try:
                classrooms.add(entry.classroom.name)
            except AttributeError:
                pass
            try:
                time_and_place.add(f"{entry.repeat_on}: {self._get_time_from_datetime(entry.first)}- {entry.classroom.name}")
            except AttributeError:
                pass
        return {
            "instructors": instructors,
            "classrooms": classrooms,
            "time_and_place": time_and_place,
        }

    @property
    def instructors(self):
        return(self._get_group_data.get("instructors"))

    @property
    def classrooms(self):
        return(self._get_group_data.get("classrooms"))

    @property
    def time_and_place(self):
        return(self._get_group_data.get("time_and_place"))


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
    first = models.DateTimeField(null=False, blank=False, default=timezone.now)
    last =  models.DateTimeField(null=True, blank=True)
    repeat_on = models.CharField(
        max_length=3,
        choices=DAYS,
        null=True
    )
    duration = models.DurationField(default=datetime.timedelta(hours=1))
    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE, null=True, blank=True)
    instructor = models.ForeignKey(Instructor, on_delete=models.CASCADE, null=True, blank=True)
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='whereabouts', null=True, blank=True)

    def get_all_dates(self):
        utc = pytz.UTC
        last = self.last or utc.localize((datetime.datetime.now() + datetime.timedelta(weeks=48)))
        dates = pd.date_range(start=self.first, end=last, freq=f'W-{self.repeat_on}')

        return dates

    def create_event(self, date):
        # TODO do get in try and create in except
        try:
            e = Event.objects.create(date=date, end_date=date+self.duration, group=self.group)
            e.instructor.set(self.instructor.all())
            e.attendees.set(self.group.students.all())
            e.classroom.set(self.classroom.all())
            e.save()
        except IntegrityError:
            e = Event.objects.get(date=date, group=self.group)

        return {"text": self.group.name, "startDate": date, "endDate": e.end_date, 'id': e.id, 'location':e.classroom.all()[0].name}

    def get_dates_in_range(self, first: datetime.datetime, last: datetime.datetime,
                           generate_events=False):
        """
        will return dates in between first and last for this scheduler as a dict
        """
        hour = self.first.hour
        minute = self.first.minute
        first = first.replace(hour=hour, minute=minute)
        last = last.replace(hour=hour, minute=minute)
        if not self.last:
            self.last = last

        if first > self.last or self.last< first:
            return []

        if self.first > first and last < self.last:
            first = self.first
            last = self.last

        elif self.first > first and self.last < last:
            first = self.first

        if self.group:
            dates = pd.date_range(start=first, end=last, freq=f'W-{self.repeat_on}')

            if generate_events:
                events = []
                for date in dates:
                    events.append(self.create_event(date))
                return events

            events_not_created = []
            for date in dates:
                e =  {"text": self.group.name, "startDate": date, "endDate": date+self.duration, 'location':self.classroom.name}
                events_not_created.append(e)
            return events_not_created

        return {}


class Event(models.Model):
    date = models.DateTimeField(null=True, blank=True)
    group = models.ForeignKey(Group, on_delete=models.CASCADE, null=True, blank=True)
    end_date =  models.DateTimeField(null=True, blank=True)
    instructor = models.ManyToManyField(Instructor)
    attendees = models.ManyToManyField(Student)
    classroom = models.ManyToManyField(Classroom)
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['date', 'group'], name='unique_event'
            )
        ]

class EventException(models.Model):
    move_from  = models.DateTimeField(null=False, blank=False, default=timezone.now)
    move_to = models.DateTimeField(null=False, blank=False, default=timezone.now)
    group = models.ManyToManyField(Group)
    instructor = models.ManyToManyField(Instructor)
    attendees = models.ManyToManyField(Student)

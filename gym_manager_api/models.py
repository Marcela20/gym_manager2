from django.db import (models, IntegrityError)
from .validators import phone_number_validator
from .exceptions import AttendanceException
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

    @property
    def full_name(self):
        return f"{self.name} {self.second_name}"


class Student(User):
    role = models.CharField(default='student', max_length=25)

    def can_attend(self, date, scheduler_id):
        scheduler=Scheduler(pk=scheduler_id)
        for sub in self.subscription.all():
            if sub.check_valid(date, scheduler):
                return True
        return False

    def check_attendance(self, date, scheduler_id):
        try:
            a = self.attendance.get(date=date, scheduler=Scheduler(pk=scheduler_id))
        except Attendance.DoesNotExist:
            a = None
        if a:
            return a.state
        return "-"

class Instructor(User):
    role = models.CharField(default='instructor', max_length=25)
    def __str__(self) -> str:
        return self.name


class Classroom(models.Model):
    name = models.CharField(max_length=25)
    def __str__(self) -> str:
        return self.name


class Group(models.Model):
    name = models.CharField(max_length=25)

    @property
    def students_list(self):
        students = set()
        for scheduler in self.whereabouts.all():
            [students.add(student) for student in scheduler.students.all()]


        return list(students)

    @property
    def all_dates(self):
        schedulers = self.whereabouts.all()
        if not schedulers:
            return []
        dates =  schedulers[0].get_all_dates()
        df = pd.DataFrame(index=dates[1], columns=["scheduler_id"])
        df.fillna(dates[0], inplace=True)

        if len(schedulers)>1:
            for s in schedulers[1:]:
                s_dates = s.get_all_dates()
                s_df = pd.DataFrame(index=s_dates[1], columns=["scheduler_id"])
                s_df.fillna(s_dates[0], inplace=True)
                df = pd.concat([df, s_df])
        df = df.sort_index()
        df.index = pd.to_datetime(df.index).strftime('%a %d/%m/%Y')
        return df

    @property
    def _get_group_data(self):
        schedulers = self.whereabouts.all()
        instructors = set()
        classrooms = set()
        time_and_place = set()
        repeats_on = []
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
                time_and_place.add(f"{entry.day_hour}- {entry.classroom.name}")
            except AttributeError:
                pass
            try:
                repeats_on.append({"day_hour": entry.day_hour, "scheduler_id": entry.id})
            except AttributeError:
                pass

        return {
            "instructors": instructors,
            "classrooms": classrooms,
            "time_and_place": time_and_place,
            "repeats_on": repeats_on,
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

    @property
    def repeats_on(self):
        return(self._get_group_data.get("repeats_on"))


class Scheduler(models.Model):
    DAYS = [
        ("MON", "Monday"),
        ("TUE", "Tuesday"),
        ("WED", "Wednesday"),
        ("THU", "Thursday"),
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
    students = models.ManyToManyField(Student)
    start_hour = models.TimeField(null=True, blank=True)

    def _get_time_from_datetime(self, date_time:datetime.datetime):
        return date_time.strftime("%H:%M")

    def get_all_dates(self):
        utc = pytz.UTC
        last = self.last or utc.localize((datetime.datetime.now() + datetime.timedelta(weeks=48)))
        dates = pd.date_range(start=self.first, end=last, freq=f'W-{self.repeat_on}')
        return (self.id, dates)

    def create_event(self, date):
        e = Event.objects.get_or_create(date=date, end_date=date+self.duration, group=self.group)
        e.instructor.set(self.instructor.all())
        e.attendees.set(self.group.students.all())
        e.classroom.set(self.classroom.all())
        e.save()
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

    @property
    def day_hour(self):
        return f"{self.repeat_on}: {self.start_hour}"


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


class Attendance(models.Model):
    STATES = [
        ("PRE", "present"),
        ("ABS", "absent"),
        ]
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['date', 'scheduler', 'student'], name='unique_attendance'
            )
        ]
    group = models.ForeignKey(Group, on_delete=models.SET_NULL, related_name='attendance', null=True, blank=True)
    scheduler = models.ForeignKey(Scheduler, on_delete=models.SET_NULL, related_name='attendance', null=True, blank=True)
    student = models.ForeignKey(Student, on_delete=models.SET_NULL, related_name='attendance', null=True, blank=True)
    state = models.CharField(
        max_length=3,
        choices=STATES,
        null=True,
        blank=True
    )
    date = models.DateField(null=False, blank=False, default=timezone.now)

    def _get_valid_subscription(self):
        subscriptions = self.student.subscription.filter(schedulers__in=[self.scheduler])
        if subscriptions:
            for subscription in subscriptions:
                if subscription.check_valid(self.date):
                    return subscription
        return None

    @property
    def is_paid(self):
        if self._get_valid_subscription():
            return True
        return False

    def remove_entrance_from_subscription(self, state):
        sub = self._get_valid_subscription()
        if sub:
            if state in ['PRE']:
                # TODO should we also  do that when absent?
                sub.remove_entrance()

class Subscription(models.Model):
    '''
    it will be possible to either have number of entrances, date range
    or both: x entrances, valid till may
    We can also assign the subscription to schedulers
    '''
    student = models.ForeignKey(Student, on_delete=models.SET_NULL, related_name='subscription', null=True, blank=True)
    schedulers = models.ManyToManyField(Scheduler)
    entrances = models.IntegerField(null=False, blank=False)
    valid_start = models.DateField(null=False, blank=False, default=timezone.now)
    valid_stop = models.DateField(null=False, blank=False, default=timezone.now)
    entrances_left = models.IntegerField(null=False, blank=False)

    def check_valid_entrances(self) -> None:
        if self.entrances_left and self.entrances_left == 0:
            return False
        return True

    def check_valid_dates(self, date) -> None:
        if self.valid_start and self.valid_stop:
            if date >= self.valid_start and date <= self.valid_stop:
                return True
            return False

    def check_valid(self, date, scheduler=None) -> None:
        if self.check_valid_dates(date) and self.check_valid_entrances():
            if scheduler:
                if scheduler in self.schedulers.all():
                    return True
                return False
            return True
        return False

    def remove_entrance(self):
        if self.entrances_left and self.entrances_left > 0 :
            self.entrances_left = self.entrances_left - 1
            self.save()
        else:
            raise AttendanceException("no entrances left")



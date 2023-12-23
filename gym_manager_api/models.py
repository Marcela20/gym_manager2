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

    @property
    def full_name(self):
        return f"{self.name} {self.second_name}"


class Student(User):
    role = models.CharField(default='student', max_length=25)


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
    # students = models.ManyToManyField(Student)

    @property
    def students_list(self):
        students = set()
        for scheduler in self.whereabouts.all():
            # [students.add(student.full_name) for student in scheduler.students.all()]
            [students.add(student) for student in scheduler.students.all()]


        return list(students)

    # def get_attendance(self):
    #     schedulers = self.whereabouts.all()
    #     if not schedulers:
    #         return []
    #     dates = schedulers[0].get_all_dates()
    #     students_list = self.students_list
    #     students = [{student.full_name for student in students_list}]

    #     df1 = pd.DataFrame(index=dates, columns=students)

    #     if len(schedulers)>1:
    #         for entry in schedulers[1:]:
    #             entry_dates = entry.get_all_dates()
    #             df2 = pd.DataFrame(index=entry_dates, columns=students)
    #             df1 = pd.concat([df1,df2], join='inner', axis=0)
    #     df1 = df1.sort_index()
    #     df1 = df1.fillna("hi")
    #     df1.index = df1.index.strftime('%a %d/%m/%Y')
    #     return df1.T

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
        ("PAI", "paid"),
        ("UNP", "unpaid"),
        ("PPR", "paid present"),
        ("UPR", "unpaid present"),
        ("UNP", "unpaid not present"),
        ("PNP", "paid not present"),
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
        default="UNP",
        null=True,
        blank=True
    )
    date = models.DateField(null=False, blank=False, default=timezone.now)

    @property
    def is_paid(self):
        subscriptions = self.student.subscription.filter(schedulers__in=[self.scheduler])
        for s in subscriptions:
            if s.valid:
                return True
            break
        return False


class Subscription(models.Model):
    '''
    it will be possible to either have number of entrances, date range
    or both: x entrances, valid till may
    We can also assign the pass to schedulers
    '''
    student = models.ForeignKey(Student, on_delete=models.SET_NULL, related_name='subscription', null=True, blank=True)
    schedulers = models.ManyToManyField(Scheduler)
    entrances = models.IntegerField(null=False, blank=False)
    valid_until = models.DateField(null=False, blank=False, default=timezone.now)
    valid_since = models.DateField(null=False, blank=False, default=timezone.now)
    entrances_left = models.IntegerField(null=False, blank=False)

    @property
    def valid(self):
        if  self.valid_until and datetime.datetime.now().date() <= self.valid_until:
            if self.entrances_left:
                if  self.entrances_left > 0:
                    return True
                return False
        else:
            if self.entrances_left > 0:
                return True
        return False

    def count_attendance(self):
        if self.entrances_left and self.entrances_left > 0 :
            self.entrances_left = self.entrances_left - 1
            self.save()
        else:
            raise Exception("no entrances left")



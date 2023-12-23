from django.contrib import admin
from .models import (User, Instructor, Student, Classroom, Group,
                     Event, Scheduler, EventException, Attendance, Subscription)

for model in [User, Instructor, Student, Classroom, Group,
              Event, Scheduler, EventException, Attendance, Subscription]:
    admin.site.register(model)

# Register your models here.

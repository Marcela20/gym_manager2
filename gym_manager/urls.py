"""
URL configuration for gym_manager project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from gym_manager_api.views import (GroupDetail, GroupViewSet, GroupWithSchedulers,
                                   StudentViewSet, InstructorViewSet, ClassroomViewSet,
                                   SchedulerViewSet, EventViewSet, EventExceptionViewSet,
                                   AttendanceViewSet, AttendanceDetail)
from django.urls import include, path
from rest_framework import routers
from gym_manager_calendar.views import scheduler
from gym_manager_attendance.attendance import AttendanceCheker, get_dates_as_columns
from gym_manager_attendance.StudentsGroup import StudentsGroup

router = routers.DefaultRouter()
router.register(r'students', StudentViewSet)
router.register(r'instructors', InstructorViewSet)
router.register(r'classrooms', ClassroomViewSet)
router.register(r'schedulers', SchedulerViewSet)
router.register(r'events', EventViewSet)
# router.register(r'events', EventExceptionViewSet)



urlpatterns = [
    path("admin/", admin.site.urls),
    path("scheduler/", scheduler),
    path("attendance/", AttendanceCheker.as_view()),
    path("attendance/columns/", get_dates_as_columns),
    path("group/students/", StudentsGroup.as_view()),
    path('api/', include(router.urls)),
    path('api/groups/', GroupViewSet.as_view()),
    path('api/groups/<pk>', GroupDetail.as_view()),
    path('api/attendance/<pk>', AttendanceDetail.as_view()),
    path('api/create_group/', GroupWithSchedulers.as_view()),
    path('api/attendance/', AttendanceViewSet.as_view()),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
]
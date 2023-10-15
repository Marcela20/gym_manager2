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
from gym_manager_api.views import (GroupViewSet, StudentViewSet, InstructorViewSet, ClassroomViewSet, SchedulerViewSet, EventViewSet, EventExceptionViewSet)
from django.urls import include, path
from rest_framework import routers
from gym_manager_calendar import views

router = routers.DefaultRouter()
router.register(r'groups', GroupViewSet)
router.register(r'students', StudentViewSet)
router.register(r'instructors', InstructorViewSet)
router.register(r'classrooms', ClassroomViewSet)
router.register(r'schedulers', SchedulerViewSet)
router.register(r'events', EventViewSet)
router.register(r'events', EventExceptionViewSet)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("calendar/", views.calendar),
    path('api/', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]
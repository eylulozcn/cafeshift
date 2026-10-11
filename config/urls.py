from django.contrib import admin
from django.urls import path

from scheduling.views import weekly_schedule


urlpatterns = [
    path("admin/", admin.site.urls),
    path("", weekly_schedule, name="weekly_schedule"),
]
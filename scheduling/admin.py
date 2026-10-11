from django.contrib import admin

from .models import Availability, Employee, Shift


class AvailabilityInline(admin.TabularInline):
    model = Availability
    extra = 7
    max_num = 7
    fields = ("weekday", "day_available", "evening_available")


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ("name", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name",)
    inlines = [AvailabilityInline]


@admin.register(Shift)
class ShiftAdmin(admin.ModelAdmin):
    list_display = ("date", "period", "employee")
    list_filter = ("period", "employee")
    search_fields = ("employee__name",)
    date_hierarchy = "date"
    ordering = ("date", "period")
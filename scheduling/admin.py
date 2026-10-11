from django.contrib import admin

from .models import Employee, Shift


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ("name", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name",)


@admin.register(Shift)
class ShiftAdmin(admin.ModelAdmin):
    list_display = ("date", "period", "employee")
    list_filter = ("period", "employee")
    search_fields = ("employee__name",)
    date_hierarchy = "date"
    ordering = ("date", "period")
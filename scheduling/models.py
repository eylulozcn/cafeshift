from django.db import models


class Employee(models.Model):
    name = models.CharField("Adı", max_length=100)
    is_active = models.BooleanField("Aktif çalışan", default=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "Çalışan"
        verbose_name_plural = "Çalışanlar"

    def __str__(self):
        return self.name

class Shift(models.Model):
    class Period(models.TextChoices):
        DAY = "day", "12:00–18:00"
        EVENING = "evening", "18:00–00:00"

    date = models.DateField("Tarih")

    period = models.CharField(
        "Vardiya",
        max_length=10,
        choices=Period.choices,
    )

    employee = models.ForeignKey(
        Employee,
        on_delete=models.PROTECT,
        related_name="shifts",
        verbose_name="Çalışan",
    )

    class Meta:
        ordering = ["date", "period"]
        verbose_name = "Vardiya"
        verbose_name_plural = "Vardiyalar"
        constraints = [
            models.UniqueConstraint(
                fields=["date", "period"],
                name="unique_shift_per_date_period",
            ),
        ]

    def __str__(self):
        return (
            f"{self.date:%d.%m.%Y} | "
            f"{self.get_period_display()} | {self.employee}"
        )

class Availability(models.Model):
    WEEKDAYS = [
        (0, "Pazartesi"),
        (1, "Salı"),
        (2, "Çarşamba"),
        (3, "Perşembe"),
        (4, "Cuma"),
        (5, "Cumartesi"),
        (6, "Pazar"),
    ]

    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name="availability",
        verbose_name="Çalışan",
    )

    weekday = models.IntegerField(
        "Gün",
        choices=WEEKDAYS,
    )

    day_available = models.BooleanField(
        "12:00–18:00 uygun",
        default=False,
    )

    evening_available = models.BooleanField(
        "18:00–00:00 uygun",
        default=False,
    )

    class Meta:
        ordering = ["weekday"]
        verbose_name = "Müsaitlik"
        verbose_name_plural = "Müsaitlikler"
        constraints = [
            models.UniqueConstraint(
                fields=["employee", "weekday"],
                name="unique_employee_weekday_availability",
            ),
        ]

    def __str__(self):
        return f"{self.employee} — {self.get_weekday_display()}"
from datetime import date, timedelta

from django import forms
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.db import transaction
from django.db.models import Q
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.http import require_http_methods

from .models import Availability, Employee, Shift

class AvailabilityChoiceField(forms.ModelChoiceField):
    def __init__(self, *args, available_ids, **kwargs):
        self.available_ids = available_ids
        super().__init__(*args, **kwargs)

    def label_from_instance(self, employee):
        if not employee.is_active:
            status = "Pasif çalışan"
        elif employee.pk in self.available_ids:
            status = "Uygun"
        else:
            status = "Uygun değil"

        return f"{employee.name} — {status}"

    def clean(self, value):
        employee = super().clean(value)

        if employee is not None:
            if (
                not employee.is_active
                or employee.pk not in self.available_ids
            ):
                raise forms.ValidationError(
                    "Bu çalışan bu vardiyaya uygun değil. "
                    "Uygun bir çalışan seç veya atamayı kaldır."
                )

        return employee
    
@staff_member_required
@require_http_methods(["GET", "POST"])
def weekly_schedule(request):
    selected_date = request.GET.get("week", "")

    try:
        selected = date.fromisoformat(selected_date)
        if not 1900 <= selected.year <= 2100:
            raise ValueError
    except ValueError:
        if request.method == "POST":
            messages.error(request, "Hafta bilgisi geçersiz. Tekrar seç.")
            return redirect("weekly_schedule")
        selected = date.today()

    week_start = selected - timedelta(days=selected.weekday())
    week_end = week_start + timedelta(days=6)

    shifts = list(
        Shift.objects.filter(
            date__range=(week_start, week_end)
        ).select_related("employee")
    )

    shift_map = {
        (shift.date, shift.period): shift
        for shift in shifts
    }

    day_names = [
        "Pazartesi", "Salı", "Çarşamba", "Perşembe",
        "Cuma", "Cumartesi", "Pazar",
    ]

    form = forms.Form(
        request.POST if request.method == "POST" else None
    )

    available_by_slot = {}

    for availability in Availability.objects.filter(
        employee__is_active=True
    ):
        if availability.day_available:
            key = (availability.weekday, Shift.Period.DAY)
            available_by_slot.setdefault(key, set()).add(
                availability.employee_id
            )

        if availability.evening_available:
            key = (availability.weekday, Shift.Period.EVENING)
            available_by_slot.setdefault(key, set()).add(
                availability.employee_id
            )
    days = []
    slots = []

    for index, name in enumerate(day_names):
        current_date = week_start + timedelta(days=index)
        row = {"date": current_date, "name": name}

        for period in Shift.Period.values:
            field_name = f"shift_{index}_{period}"
            existing = shift_map.get((current_date, period))
            existing_id = existing.employee_id if existing else None

            # Aktif çalışanlar ve bu vardiyadaki mevcut kişi.
            employees = Employee.objects.filter(
                Q(is_active=True) | Q(pk=existing_id)
            ).order_by("name")

            available_ids = available_by_slot.get(
                (current_date.weekday(), period),
                set(),
            )

            form.fields[field_name] = AvailabilityChoiceField(
                queryset=employees,
                available_ids=available_ids,
                required=False,
                empty_label="— Atanmadı —",
                initial=existing_id,
                label=f"{name} {Shift.Period(period).label}",
            )

            row[f"{period}_field"] = form[field_name]
            slots.append((current_date, period, field_name))

        days.append(row)

    if request.method == "POST":
        valid = form.is_valid()

        # Eksik gönderilen form yüzünden kayıtları silme.
        if any(name not in request.POST for name in form.fields):
            form.add_error(
                None,
                "Form eksik gönderildi. Sayfayı yenileyip tekrar dene.",
            )
            valid = False

        if valid:
            # Tüm değişiklikleri birlikte uygula.
            with transaction.atomic():
                for shift_date, period, field_name in slots:
                    employee = form.cleaned_data[field_name]

                    if employee is None:
                        Shift.objects.filter(
                            date=shift_date,
                            period=period,
                        ).delete()
                    else:
                        Shift.objects.update_or_create(
                            date=shift_date,
                            period=period,
                            defaults={"employee": employee},
                        )

            messages.success(request, "Haftalık plan kaydedildi.")
            url = reverse("weekly_schedule")
            return redirect(f"{url}?week={week_start.isoformat()}")
    # Aktif çalışanlar ve bu haftada kaydı bulunan eski çalışanlar.
    assigned_ids = [shift.employee_id for shift in shifts]

    summary_employees = Employee.objects.filter(
        Q(is_active=True) | Q(pk__in=assigned_ids)
    ).order_by("name")

    employee_totals = []

    for employee in summary_employees:
        employee_shifts = [
            shift for shift in shifts
            if shift.employee_id == employee.id
        ]

        day_count = sum(
            shift.period == Shift.Period.DAY
            for shift in employee_shifts
        )

        evening_count = sum(
            shift.period == Shift.Period.EVENING
            for shift in employee_shifts
        )

        employee_totals.append({
            "name": employee.name,
            "day_count": day_count,
            "evening_count": evening_count,
            "shift_count": len(employee_shifts),
            "hours": len(employee_shifts) * 6,
        })

    # Paylaşılacak metni kayıtlı vardiyalardan oluştur.
    lines = [
        f"{week_start:%d.%m.%Y} – {week_end:%d.%m.%Y}",
        "HAFTALIK VARDİYA PLANI",
        "",
    ]

    for day in days:
        current_date = day["date"]
        lines.append(f"{current_date:%d.%m.%Y} {day['name']}")

        for period, label in Shift.Period.choices:
            shift = shift_map.get((current_date, period))
            employee_name = shift.employee.name if shift else "Atanmadı"
            lines.append(f"{label}: {employee_name}")

        lines.append("")

    share_text = "\n".join(lines).strip()
    context = {
        "form": form,
        "days": days,
        "week_start": week_start,
        "week_end": week_end,
        "previous_week": week_start - timedelta(days=7),
        "next_week": week_start + timedelta(days=7),
        "filled_count": len(shifts),
        "empty_count": 14 - len(shifts),
        "employee_totals": employee_totals,
        "share_text": share_text,
    }

    return render(request, "scheduling/weekly_schedule.html", context)

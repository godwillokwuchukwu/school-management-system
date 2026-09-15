from django.contrib import admin

from .models import Fee, FeeSchedule, Payment


@admin.register(Fee)
class FeeAdmin(admin.ModelAdmin):
    list_display = ("title", "student", "amount", "status", "due_date", "paid_at")
    list_filter = ("status", "due_date")
    search_fields = (
        "title",
        "student__profile__user__first_name",
        "student__profile__user__last_name",
    )


@admin.register(FeeSchedule)
class FeeScheduleAdmin(admin.ModelAdmin):
    list_display = ["title", "academic_year", "amount", "due_date"]
    list_filter = ["academic_year"]


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ["fee", "amount", "transaction_ref", "status", "created_at"]
    list_filter = ["status"]
    search_fields = ["transaction_ref"]

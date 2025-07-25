from django.contrib import admin
from .models import  *

@admin.register(LeaveType)
class LeaveTypeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'max_days_per_year', 'deleted')
    search_fields = ('name',)
    list_filter = ('deleted',)

@admin.register(LeaveStatus)
class LeaveStatusAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'deleted')
    search_fields = ('name',)
    list_filter = ('deleted',)

@admin.register(LeaveRequest)
class LeaveRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'employee', 'leave_type', 'status', 'from_date', 'to_date', 'approved_by','is_half_day', 'deleted')
    search_fields = ('employee__first_name', 'employee__last_name')
    list_filter = ('status', 'leave_type', 'deleted')


@admin.register(LeaveBalance)
class LeaveBalanceAdmin(admin.ModelAdmin):
    list_display = ('employee', 'leave_type', 'total_allocated', 'used', 'days_left_display', 'deleted')

    def days_left_display(self, obj):
        return obj.days_left
    days_left_display.short_description = 'Days Left'

@admin.register(LeaveLog)
class LeaveLogAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "employee",
        "leave_type",
        "date",
        "is_half_day",
        "leave_request",
        "created_at"
    )
    list_filter = ("leave_type", "is_half_day", "date", "employee")
    search_fields = ("employee__user__first_name", "employee__user__last_name", "leave_type__name")
    ordering = ("-date",)

# @admin.register(LeaveSummaryLog)
# class LeaveSummaryLogAdmin(admin.ModelAdmin):
#     list_display = (
#         'id',
#         'employee',
#         'leave_type',
#         'from_date',
#         'to_date',
#         'is_half_day',
#         'leave_request',
#         'created_at',
#     )
#     list_filter = ('leave_type', 'is_half_day', 'created_at')
#     search_fields = ('employee__user__first_name', 'employee__user__last_name', 'leave_type__name')
#     readonly_fields = ('created_at',)
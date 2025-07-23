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
    list_display = ('id', 'employee', 'leave_type', 'status', 'from_date', 'to_date', 'is_half_day', 'deleted')
    search_fields = ('employee__first_name', 'employee__last_name')
    list_filter = ('status', 'leave_type', 'deleted')


@admin.register(LeaveBalance)
class LeaveBalanceAdmin(admin.ModelAdmin):
    list_display = ('employee', 'leave_type', 'total_allocated', 'used', 'deleted')
    search_fields = ('employee__first_name', 'employee__last_name', 'leave_type__name')
    list_filter = ('leave_type', 'deleted')

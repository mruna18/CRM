from django.contrib import admin
from .models import *

@admin.register(AttendenceStatus)
class AttendenceStatusAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'acronym', 'deleted')
    search_fields = ('name', 'acronym')
    list_filter = ('deleted',)
    ordering = ('id',)

@admin.register(Attendence)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'employee',
        'check_in_date',
        'check_in',
        'check_out_date',
        'check_out',
        'status',
        'total_working_hour',
        'deleted',
    )
    search_fields = ('employee__first_name', 'employee__last_name', 'employee__email')
    list_filter = ('status', 'check_in_date', 'deleted')
    readonly_fields = ('total_working_hour',)
    ordering = ('-check_in_date',)
    autocomplete_fields = ['employee', 'status']

@admin.register(AttendenceSession)
class AttendenceSessionAdmin(admin.ModelAdmin):
    list_display = (
        'employee', 'get_date', 'login_time', 'logout_time', 'session_duration'
    )
    search_fields = ('employee__user__username',)
    list_filter = ('login_time',)

    def get_date(self, obj):
        return obj.login_time.date() if obj.login_time else "-"
    get_date.short_description = "Date"

    def session_duration(self, obj):
        if obj.login_time and obj.logout_time:
            return obj.logout_time - obj.login_time
        return "-"
    session_duration.short_description = "Duration"

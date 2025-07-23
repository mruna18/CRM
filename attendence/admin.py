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

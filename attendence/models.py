from django.db import models
from api.models import *

class AttendenceStatus(models.Model):
    name=models.CharField(max_length=200,null=True,blank=True)#Present,Absent,Sick Leave,Casual Leave ,Week off,Half Day,Late,Early Leave,Compensatory Off 
    acronym=models.CharField(max_length=10,null=True,blank=True)
    deleted=models.BooleanField(default=False)
    class Meta:
        db_table="emp_status"

    def __str__(self):
        return self.name or self.acronym or f"Status {self.id}"

class Attendence(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.DO_NOTHING, null=True, blank=True)
    
    check_in_date = models.DateField(null=True, blank=True)
    check_in = models.TimeField(null=True, blank=True)
    
    check_out_date = models.DateField(null=True, blank=True)
    check_out = models.TimeField(null=True, blank=True)

    check_in_location = models.JSONField(null=True, blank=True)  # Example: {"lat": ..., "lng": ...}
    check_out_location = models.JSONField(null=True, blank=True)

    check_in_image = models.TextField(null=True, blank=True)  # Base64 or URL to image
    check_out_image = models.TextField(null=True, blank=True)

    status = models.ForeignKey(AttendenceStatus, on_delete=models.DO_NOTHING, null=True, blank=True)  # e.g., Present, WFH, Leave, etc.

    remarks = models.TextField(null=True, blank=True)
    total_working_hour = models.CharField(max_length=20, null=True, blank=True)  # Storing as HH:MM format
    
    deleted = models.BooleanField(default=False)

    class Meta:
        db_table = 'Attendance'
        unique_together = ('employee', 'check_in_date')
        indexes = [
        models.Index(fields=['check_in_date']),
        ]
        ordering = ['check_in_date']

    def __str__(self):
        return f"{self.employee} - {self.check_in_date}"


class AttendenceSession(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    login_time = models.DateTimeField()
    logout_time = models.DateTimeField(null=True, blank=True)
    deleted = models.BooleanField(default=False)

    class Meta:
        db_table = "AttendenceSession"

    def __str__(self):
        return f"{self.employee} - {self.login_time.date()}"
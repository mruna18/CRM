from django.db import models
from api.models import Employee  # Adjust if needed

class LeaveType(models.Model):
    name = models.CharField(max_length=50, unique=True)  # e.g., Sick, Casual, Maternity
    description = models.TextField(null=True, blank=True)
    max_days_per_year = models.IntegerField(null=True, blank=True)
    deleted = models.BooleanField(default=False)

    class Meta:
        db_table = "leave_type"

    def __str__(self):
        return self.name


class LeaveStatus(models.Model):
    name = models.CharField(max_length=30, unique=True)  # Pending, Approved, Rejected
    deleted = models.BooleanField(default=False)

    class Meta:
        db_table = "leave_status"

    def __str__(self):
        return self.name


class LeaveRequest(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    leave_type = models.ForeignKey(LeaveType, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.ForeignKey(LeaveStatus, on_delete=models.SET_NULL, null=True, blank=True)

    from_date = models.DateField()
    to_date = models.DateField()
    is_half_day = models.BooleanField(default=False)
    total_days = models.DecimalField(max_digits=4, decimal_places=1, default=0)  # Allow half days

    reason = models.TextField(null=True, blank=True)
    remarks_by_superior = models.TextField(null=True, blank=True)
    approved_by = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True, related_name="approved_leaves")
    applied_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    deleted = models.BooleanField(default=False)

    class Meta:
        db_table = "leave_request"
        ordering = ["-applied_at"]
        unique_together = ("employee", "from_date", "to_date")  # optional

    def __str__(self):
        return f"{self.employee} | {self.leave_type} | {self.status}"


#! leave balance

class LeaveBalance(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    leave_type = models.ForeignKey(LeaveType, on_delete=models.CASCADE)

    total_allocated = models.IntegerField(default=0)  # max allowed
    used = models.IntegerField(default=0)             # leave taken

    deleted = models.BooleanField(default=False)

    class Meta:
        unique_together = ('employee', 'leave_type')
        db_table = 'leave_balance'

    @property
    def days_left(self):
        """Calculate remaining leave days"""
        return self.total_allocated - self.used

    def __str__(self):
        return f"{self.employee} - {self.leave_type} | {self.used}/{self.total_allocated}"

from rest_framework import serializers
from .models import *

class LeaveSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeaveRequest
        fields = '__all__'


# leave_type serializer
class LeaveTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeaveType
        fields = '__all__'

# leave_status serializer
class LeaveStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeaveStatus
        fields = '__all__'

# leave balance
class LeaveBalanceSerializer(serializers.ModelSerializer):
    employee_name = serializers.SerializerMethodField()
    leave_type_name = serializers.CharField(source='leave_type.name', read_only=True)

    class Meta:
        model = LeaveBalance
        fields = '__all__'

    def get_employee_name(self, obj):
        return f"{obj.employee.first_name} {obj.employee.last_name}" if obj.employee else ""

# leave request
# class LeaveRequestSerializer(serializers.ModelSerializer):
#     employee_name = serializers.CharField(source='employee.name', read_only=True)
#     leave_type_name = serializers.CharField(source='leave_type.name', read_only=True)
#     status_name = serializers.CharField(source='status.name', read_only=True)

#     class Meta:
#         model = LeaveRequest
#         fields = [
#             'id',
#             'employee', 'employee_name',
#             'leave_type', 'leave_type_name',
#             'status', 'status_name',
#             'from_date', 'to_date', 'total_days',
#             'is_half_day', 'reason', 'remarks_by_superior',
#             'applied_at', 'updated_at',
#             'deleted'
#         ]



class LeaveRequestSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source='employee.user.get_full_name', read_only=True)
    leave_type_name = serializers.CharField(source='leave_type.name', read_only=True)
    status_name = serializers.CharField(source='status.name', read_only=True)
    approved_by_name = serializers.CharField(source='approved_by.user.get_full_name', read_only=True)

    class Meta:
        model = LeaveRequest
        fields = '__all__'


#! leave daily log
class LeaveLogSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source="employee.user.get_full_name", read_only=True)
    leave_type_name = serializers.CharField(source="leave_type.name", read_only=True)
    status_name = serializers.CharField(source="status.name", read_only=True)
    approved_by_name = serializers.CharField(source="approved_by.user.get_full_name", read_only=True)

    class Meta:
        model = LeaveLog
        fields = [
            "id", "leave_request", "employee", "employee_name", 
            "leave_type", "leave_type_name", "date", "is_half_day",
            "status", "status_name", "remarks", "approved_by", "approved_by_name",
            "created_at", "updated_at"
        ]

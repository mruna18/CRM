from rest_framework.views import APIView
from rest_framework.response import Response
from .models import *
from .serializers import *
from api.models import *  
from datetime import datetime

#! leave type
class CreateLeaveType(APIView):
    def post(self, request):
        data = request.data
        if LeaveType.objects.filter(name__iexact=data.get("name"), deleted=False).exists():
            return Response({"error": "Leave type already exists", "status": 409})
        serializer = LeaveTypeSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({"data": serializer.data, "status": 201})
        return Response({"error": serializer.errors, "status": 400})


class GetAllLeaveTypes(APIView):
    def get(self, request):
        queryset = LeaveType.objects.filter(deleted=False)
        serializer = LeaveTypeSerializer(queryset, many=True)
        return Response({"data": serializer.data, "status": 200})


class GetLeaveTypeById(APIView):
    def get(self, request, id):
        try:
            leave_type = LeaveType.objects.get(id=id, deleted=False)
            serializer = LeaveTypeSerializer(leave_type)
            return Response({"data": serializer.data, "status": 200})
        except LeaveType.DoesNotExist:
            return Response({"error": "Leave type not found", "status": 404})


class UpdateLeaveType(APIView):
    def post(self, request):
        data = request.data
        leave_type_id = data.get("id")
        try:
            leave_type = LeaveType.objects.get(id=leave_type_id, deleted=False)
        except LeaveType.DoesNotExist:
            return Response({"error": "Leave type not found", "status": 404})
        
        if LeaveType.objects.filter(name__iexact=data.get("name"), deleted=False).exclude(id=leave_type_id).exists():
            return Response({"error": "Leave type with this name already exists", "status": 409})

        serializer = LeaveTypeSerializer(leave_type, data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({"data": serializer.data, "status": 200})
        return Response({"error": serializer.errors, "status": 400})


class DeleteLeaveType(APIView):
    def get(self, request, id):
        try:
            leave_type = LeaveType.objects.get(id=id, deleted=False)
            leave_type.deleted = True
            leave_type.save()
            return Response({"message": "Leave type deleted successfully", "status": 200})
        except LeaveType.DoesNotExist:
            return Response({"error": "Leave type not found", "status": 404})


#! leave status.
class CreateLeaveStatus(APIView):
    def post(self, request):
        data = request.data
        if LeaveStatus.objects.filter(name__iexact=data.get("name"), deleted=False).exists():
            return Response({"error": "Leave status already exists", "status": 409})
        serializer = LeaveStatusSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({"data": serializer.data, "status": 201})
        return Response({"error": serializer.errors, "status": 400})


class GetAllLeaveStatuses(APIView):
    def get(self, request):
        statuses = LeaveStatus.objects.filter(deleted=False)
        serializer = LeaveStatusSerializer(statuses, many=True)
        return Response({"data": serializer.data, "status": 200})


class GetLeaveStatusById(APIView):
    def get(self, request, id):
        try:
            status = LeaveStatus.objects.get(id=id, deleted=False)
            serializer = LeaveStatusSerializer(status)
            return Response({"data": serializer.data, "status": 200})
        except LeaveStatus.DoesNotExist:
            return Response({"error": "Leave status not found", "status": 404})


class UpdateLeaveStatus(APIView):
    def post(self, request):
        data = request.data
        status_id = data.get("id")
        try:
            status = LeaveStatus.objects.get(id=status_id, deleted=False)
        except LeaveStatus.DoesNotExist:
            return Response({"error": "Leave status not found", "status": 404})

        if LeaveStatus.objects.filter(name__iexact=data.get("name"), deleted=False).exclude(id=status_id).exists():
            return Response({"error": "Leave status with this name already exists", "status": 409})

        serializer = LeaveStatusSerializer(status, data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({"data": serializer.data, "status": 200})
        return Response({"error": serializer.errors, "status": 400})


class DeleteLeaveStatus(APIView):
    def get(self, request, id):
        try:
            status = LeaveStatus.objects.get(id=id, deleted=False)
            status.deleted = True
            status.save()
            return Response({"message": "Leave status deleted successfully", "status": 200})
        except LeaveStatus.DoesNotExist:
            return Response({"error": "Leave status not found", "status": 404})
        

#! leave balance
class LeaveBalanceView(APIView):
    def get(self, request):
        balances = LeaveBalance.objects.filter(deleted=False)
        serializer = LeaveBalanceSerializer(balances, many=True)
        return Response({"data": serializer.data, "status": 200})

class LeaveBalanceForEmployee(APIView):
    def get(self, request, employee_id):
        balances = LeaveBalance.objects.filter(employee_id=employee_id, deleted=False)
        serializer = LeaveBalanceSerializer(balances, many=True)
        return Response({"data": serializer.data, "status": 200})
    

#! leave
class CreateLeave(APIView):
    def post(self, request):
        data = request.data.copy()

        employee_id = data.get("employee")
        from_date = data.get("from_date")
        to_date = data.get("to_date")

        if not employee_id or not from_date or not to_date:
            return Response({"error": "employee, from_date, and to_date are required", "status": 400})

        # Check if employee exists
        try:
            employee = Employee.objects.get(id=employee_id, deleted=False)
        except Employee.DoesNotExist:
            return Response({"error": "Employee not found", "status": 404})

        # Calculate total leave days
        try:
            start = datetime.strptime(from_date, "%Y-%m-%d").date()
            end = datetime.strptime(to_date, "%Y-%m-%d").date()
            if end < start:
                return Response({"error": "to_date cannot be before from_date", "status": 400})
            data["total_days"] = (end - start).days + 1
        except Exception as e:
            return Response({"error": f"Date error: {str(e)}", "status": 400})

        # Save leave
        serializer = LeaveSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({"data": serializer.data, "status": 201})
        return Response({"error": serializer.errors, "status": 400})

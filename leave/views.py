from rest_framework.views import APIView
from rest_framework.response import Response
from .models import *
from .serializers import *
from api.models import *  
from datetime import datetime, timedelta
from django.db.models import Q

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

#creating the leave request
# class CreateLeave(APIView):
#     def post(self, request):
#         data = request.data.copy()

#         employee_id = data.get("employee")
#         from_date = data.get("from_date")
#         to_date = data.get("to_date")

#         if not employee_id or not from_date or not to_date:
#             return Response({"error": "employee, from_date, and to_date are required", "status": 400})

#         # Check if employee exists
#         try:
#             employee = Employee.objects.get(id=employee_id, deleted=False)
#         except Employee.DoesNotExist:
#             return Response({"error": "Employee not found", "status": 404})

#         # Calculate total leave days
#         try:
#             start = datetime.strptime(from_date, "%Y-%m-%d").date()
#             end = datetime.strptime(to_date, "%Y-%m-%d").date()
#             if end < start:
#                 return Response({"error": "to_date cannot be before from_date", "status": 400})
#             data["total_days"] = (end - start).days + 1
#         except Exception as e:
#             return Response({"error": f"Date error: {str(e)}", "status": 400})

#         # Save leave
#         serializer = LeaveSerializer(data=data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response({"data": serializer.data, "status": 201})
#         return Response({"error": serializer.errors, "status": 400})

# Optional: Assume Saturday and Sunday as weekends
WEEKENDS = [5, 6]  # Saturday=5, Sunday=6

class CreateLeave(APIView):
    def post(self, request):
        data = request.data.copy()

        employee_id = data.get("employee")
        leave_type_id = data.get("leave_type")
        from_date = data.get("from_date")
        to_date = data.get("to_date")
        is_half_day = data.get("is_half_day", False)

        if not employee_id or not from_date or not to_date or not leave_type_id:
            return Response({"error": "employee, leave_type, from_date, and to_date are required", "status": 400})

        # 1. Employee check
        try:
            employee = Employee.objects.get(id=employee_id, deleted=False)
        except Employee.DoesNotExist:
            return Response({"error": "Employee not found", "status": 404})

        # 1.5. Leave type check
        try:
            leave_type = LeaveType.objects.get(id=leave_type_id, deleted=False)
        except LeaveType.DoesNotExist:
            return Response({"error": "Leave type not found", "status": 404})

        # 2. Date validation and total days calculation
        try:
            start = datetime.strptime(from_date, "%Y-%m-%d").date()
            end = datetime.strptime(to_date, "%Y-%m-%d").date()
            if end < start:
                return Response({"error": "to_date cannot be before from_date", "status": 400})

            # Handle weekends
            total_days = sum(1 for i in range((end - start).days + 1)
                             if (start + timedelta(days=i)).weekday() not in WEEKENDS)

            if total_days == 0:
                return Response({"error": "Selected range only includes weekends", "status": 400})

            # Handle half-day logic
            if is_half_day:
                if total_days > 1:
                    return Response({"error": "Half-day leave can only be for single day", "status": 400})
                total_days = 0.5

            data["total_days"] = total_days
        except Exception as e:
            return Response({"error": f"Date error: {str(e)}", "status": 400})

        # 3. Overlapping leave check
        overlap_exists = LeaveRequest.objects.filter(
            employee_id=employee_id,
            deleted=False,
            from_date__lte=end,
            to_date__gte=start
        ).exists()

        if overlap_exists:
            return Response({"error": "Leave request overlaps with existing request", "status": 400})

        # 4. Check leave balance
        try:
            balance = LeaveBalance.objects.get(employee_id=employee_id, leave_type_id=leave_type_id)
        except LeaveBalance.DoesNotExist:
            return Response({"error": "Leave balance not set for this leave type", "status": 400})

        if total_days > balance.days_left:
            return Response({
                "error": f"Not enough leave balance. Available: {balance.days_left}, Required: {total_days}",
                "status": 400
            })

        # 5. Check against max_days_per_year from LeaveType
        leave_type = LeaveType.objects.get(id=leave_type_id, deleted=False)
        yearly_leaves = LeaveRequest.objects.filter(
            employee_id=employee_id,
            leave_type_id=leave_type_id,
            from_date__year=start.year,
            deleted=False
        )

        used_days = sum(l.total_days for l in yearly_leaves)
        if used_days + total_days > leave_type.max_days_per_year:
            return Response({
                "error": f"Exceeded yearly limit for {leave_type.name}. Max allowed: {leave_type.max_days_per_year}",
                "status": 400
            })

        # Save
        serializer = LeaveSerializer(data=data)
        if serializer.is_valid():
            leave_request = serializer.save()
            
            # Set default status to "Pending" if not provided
            if not leave_request.status:
                try:
                    pending_status = LeaveStatus.objects.get(name__iexact="pending", deleted=False)
                    leave_request.status = pending_status
                    leave_request.save()
                except LeaveStatus.DoesNotExist:
                    # If "Pending" status doesn't exist, create it
                    pending_status = LeaveStatus.objects.create(name="Pending")
                    leave_request.status = pending_status
                    leave_request.save()
            
            return Response({"data": serializer.data, "status": 201})
        return Response({"error": serializer.errors, "status": 400})


class ApproveLeaveRequest(APIView):
    def post(self, request):
        data = request.data
        leave_id = data.get("leave_id")
        approver_id = data.get("approver_id")
        action = data.get("action")  # "approve" or "reject"
        remarks = data.get("remarks", "")

        if not all([leave_id, approver_id, action]):
            return Response({"error": "leave_id, approver_id, and action are required", "status": 400})

        if action not in ["approve", "reject"]:
            return Response({"error": "action must be 'approve' or 'reject'", "status": 400})

        # Check if approver exists and has permission
        try:
            approver = Employee.objects.get(id=approver_id, deleted=False)
        except Employee.DoesNotExist:
            return Response({"error": "Approver not found", "status": 404})

        # Check if approver has permission (HR, Admin, Manager)
        if approver.role.name.lower() not in ["hr", "admin", "manager"]:
            return Response({"error": "Unauthorized to approve leaves", "status": 403})

        # Get leave request
        try:
            leave_request = LeaveRequest.objects.get(id=leave_id, deleted=False)
        except LeaveRequest.DoesNotExist:
            return Response({"error": "Leave request not found", "status": 404})

        # Get appropriate status
        try:
            if action == "approve":
                status = LeaveStatus.objects.get(name__iexact="approved", deleted=False)
            else:
                status = LeaveStatus.objects.get(name__iexact="rejected", deleted=False)
        except LeaveStatus.DoesNotExist:
            # Create status if it doesn't exist
            status = LeaveStatus.objects.create(name=action.title())

        # Update leave request
        leave_request.status = status
        leave_request.approved_by = approver
        leave_request.remarks_by_superior = remarks
        leave_request.save()

        # If approved, update leave balance
        if action == "approve":
            try:
                balance = LeaveBalance.objects.get(
                    employee=leave_request.employee,
                    leave_type=leave_request.leave_type,
                    deleted=False
                )
                balance.used += float(leave_request.total_days)
                balance.save()
            except LeaveBalance.DoesNotExist:
                return Response({"error": "Leave balance not found", "status": 404})

        serializer = LeaveRequestSerializer(leave_request)
        return Response({
            "data": serializer.data,
            "message": f"Leave request {action}d successfully",
            "status": 200
        })


# get leave request
class GetLeaveRequests(APIView):
    def get(self, request):
        employee_id = request.GET.get("employee_id")
        if not employee_id:
            return Response({"error": "employee_id is required", "status": 400})

        try:
            employee = Employee.objects.get(id=employee_id, deleted=False)
        except Employee.DoesNotExist:
            return Response({"error": "Employee not found", "status": 404})

        # Regular employee sees only their own requests
        if employee.role.name.lower() == "employee":
            leaves = LeaveRequest.objects.filter(employee=employee, deleted=False)
        else:
            # Manager/Admin sees all
            leaves = LeaveRequest.objects.filter(deleted=False)

        serializer = LeaveRequestSerializer(leaves, many=True)
        return Response({"data": serializer.data, "status": 200})



class GetAllLeaveRequests(APIView):
    def post(self, request):
        employee_id = request.data.get("employee_id")
        if not employee_id:
            return Response({"error": "employee_id is required", "status": 400})

        try:
            employee = Employee.objects.get(id=employee_id, deleted=False)
        except Employee.DoesNotExist:
            return Response({"error": "Employee not found", "status": 404})

        # Return only leave requests belonging to the requesting employee
        leaves = LeaveRequest.objects.filter(employee=employee, deleted=False)

        serializer = LeaveRequestSerializer(leaves, many=True)
        return Response({"data": serializer.data, "status": 200})

#! for hr and admin
class GetAllLeaveRequestsAdmin(APIView):
    def post(self, request):
        employee_id = request.data.get("employee_id")
        if not employee_id:
            return Response({"error": "employee_id is required", "status": 400})

        try:
            employee = Employee.objects.get(id=employee_id, deleted=False)
        except Employee.DoesNotExist:
            return Response({"error": "Employee not found", "status": 404})

        # Only allow roles like "HR", "Admin", "Manager" to see all
        if employee.role.name.lower() not in ["hr", "admin", "manager"]:
            return Response({"error": "Unauthorized", "status": 403})

        leaves = LeaveRequest.objects.filter(deleted=False)
        serializer = LeaveRequestSerializer(leaves, many=True)
        return Response({"data": serializer.data, "status": 200})




class GetLeaveRequestDetail(APIView):
    def get(self, request, id):
        employee_id = request.GET.get("employee_id")
        if not employee_id:
            return Response({"error": "employee_id is required", "status": 400})

        try:
            employee = Employee.objects.get(id=employee_id, deleted=False)
        except Employee.DoesNotExist:
            return Response({"error": "Employee not found", "status": 404})

        try:
            leave = LeaveRequest.objects.get(id=id, deleted=False)
        except LeaveRequest.DoesNotExist:
            return Response({"error": "Leave request not found", "status": 404})

        if employee.role.name.lower() == "employee" and leave.employee_id != employee.id:
            return Response({"error": "You are not authorized to view this leave request", "status": 403})

        serializer = LeaveRequestSerializer(leave)
        return Response({"data": serializer.data, "status": 200})



class DeleteLeaveRequest(APIView):
    def post(self, request):
        leave_id = request.data.get("id")
        employee_id = request.data.get("employee_id")

        if not leave_id or not employee_id:
            return Response({"error": "Both leave_id and employee_id are required", "status": 400})

        try:
            employee = Employee.objects.get(id=employee_id, deleted=False)
        except Employee.DoesNotExist:
            return Response({"error": "Employee not found", "status": 404})

        try:
            leave = LeaveRequest.objects.get(id=leave_id, deleted=False)
        except LeaveRequest.DoesNotExist:
            return Response({"error": "Leave request not found", "status": 404})

        if employee.role.name.lower() == "employee" and leave.employee_id != employee.id:
            return Response({"error": "You are not authorized to delete this leave request", "status": 403})

        leave.deleted = True
        leave.save()
        return Response({"msg": "Leave request deleted successfully", "status": 200})


class UpdateLeaveRequest(APIView):
    def post(self, request):
        data = request.data
        leave_id = data.get("id")

        if not leave_id:
            return Response({"error": "Leave ID is required", "status": 400})

        try:
            leave = LeaveRequest.objects.get(id=leave_id, deleted=False)
        except LeaveRequest.DoesNotExist:
            return Response({"error": "Leave request not found", "status": 404})

        serializer = LeaveRequestSerializer(leave, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"data": serializer.data, "status": 200})
        return Response({"error": serializer.errors, "status": 400})


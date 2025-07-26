from rest_framework.views import APIView
from rest_framework.response import Response
from .models import *
from .serializers import *
from api.models import *  
from datetime import datetime, timedelta
from django.db.models import Q
from attendence.models import * 

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
    
class CreateLeaveBalanceForEmployee(APIView):
    def post(self, request):
        employee_id = request.data.get("employee_id")

        if not employee_id:
            return Response({"error": "employee_id is required", "status": 400}, status=400)

        try:
            employee = Employee.objects.get(id=employee_id, deleted=False)
        except Employee.DoesNotExist:
            return Response({"error": "Employee not found", "status": 404}, status=404)

        leave_types = LeaveType.objects.filter(deleted=False)
        created_entries = []

        for leave_type in leave_types:
            balance, created = LeaveBalance.objects.get_or_create(
                employee=employee,
                leave_type=leave_type,
                defaults={
                    "total_allocated": leave_type.max_days_per_year or 0,
                    "used": 0,
                    "deleted": False
                }
            )
            if created:
                created_entries.append(f"{leave_type.name}")

        if created_entries:
            return Response({
                "message": "Leave balances created",
                "created_for_types": created_entries,
                "status": 201
            })
        else:
            return Response({
                "message": "Leave balances already exist",
                "status": 200
            })
    

#! request leave
#? Optional: Assume Saturday and Sunday as weekends
WEEKENDS = [5, 6]  # Saturday=5, Sunday=6

class CreateLeave(APIView):
    def post(self, request):
        data = request.data.copy()

        leave_type_id = data.get("leave_type")
        from_date = data.get("from_date")
        to_date = data.get("to_date")
        is_half_day = data.get("is_half_day", False)

        if not from_date or not to_date or not leave_type_id:
            return Response({"error": "leave_type, from_date, and to_date are required", "status": 400})

        # Get logged-in user’s employee object
        try:
            current_employee = Employee.objects.get(user=request.user, deleted=False)
        except Employee.DoesNotExist:
            return Response({"error": "You are not a valid employee"}, status=403)

        # Default to logged-in employee
        requested_employee_id = data.get("employee")
        is_self = not requested_employee_id or str(current_employee.id) == str(requested_employee_id)

        allowed_roles = ["hr", "admin", "manager"]
        is_authority = any(role in current_employee.role.name.lower() for role in allowed_roles)

        if not is_self and not is_authority:
            return Response({"error": "Unauthorized to create leave for others"}, status=403)

        employee_id = requested_employee_id or current_employee.id
        data["employee"] = employee_id  # Force correct employee ID

        # Employee existence check
        try:
            employee = Employee.objects.get(id=employee_id, deleted=False)
        except Employee.DoesNotExist:
            return Response({"error": "Employee not found", "status": 404})

        # Leave type check
        try:
            leave_type = LeaveType.objects.get(id=leave_type_id, deleted=False)
        except LeaveType.DoesNotExist:
            return Response({"error": "Leave type not found", "status": 404})

        # Date validation and working day count
        try:
            start = datetime.strptime(from_date, "%Y-%m-%d").date()
            end = datetime.strptime(to_date, "%Y-%m-%d").date()
            if end < start:
                return Response({"error": "to_date cannot be before from_date", "status": 400})

            total_days = sum(1 for i in range((end - start).days + 1)
                             if (start + timedelta(days=i)).weekday() not in WEEKENDS)

            if total_days == 0:
                return Response({"error": "Selected range only includes weekends", "status": 400})

            if is_half_day:
                if total_days > 1:
                    return Response({"error": "Half-day leave can only be for single day", "status": 400})
                total_days = 0.5

            data["total_days"] = total_days

        except Exception as e:
            return Response({"error": f"Date error: {str(e)}", "status": 400})

        # Overlapping leave check
        overlap_exists = LeaveRequest.objects.filter(
            employee_id=employee_id,
            deleted=False,
            from_date__lte=end,
            to_date__gte=start
        ).exists()

        if overlap_exists:
            return Response({"error": "Leave request overlaps with existing request", "status": 400})

        # Leave balance check
        try:
            balance = LeaveBalance.objects.get(employee_id=employee_id, leave_type_id=leave_type_id)
        except LeaveBalance.DoesNotExist:
            return Response({"error": "Leave balance not set for this leave type", "status": 400})

        if total_days > balance.days_left:
            return Response({
                "error": f"Not enough leave balance. Available: {balance.days_left}, Required: {total_days}",
                "status": 400
            })

        # Annual leave limit check
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

        # Force status to "Pending"
        try:
            pending_status = LeaveStatus.objects.get(name__iexact="pending", deleted=False)
        except LeaveStatus.DoesNotExist:
            pending_status = LeaveStatus.objects.create(name="Pending")

        data["status"] = pending_status.id  # override any incoming status

        # Save leave request
        serializer = LeaveSerializer(data=data)
        if serializer.is_valid():
            leave_request = serializer.save()
            return Response({"data": serializer.data, "status": 201})
        return Response({"error": serializer.errors, "status": 400})

#! cancel leave request
class CancelLeaveRequest(APIView):
    def post(self, request):
        leave_id = request.data.get("leave_id")

        if not leave_id:
            return Response({"error": "leave_id is required", "status": 400})

        # Get logged-in employee
        try:
            current_employee = Employee.objects.get(user=request.user, deleted=False)
        except Employee.DoesNotExist:
            return Response({"error": "You are not a valid employee"}, status=403)

        # Fetch the leave
        try:
            leave = LeaveRequest.objects.get(id=leave_id, deleted=False)
        except LeaveRequest.DoesNotExist:
            return Response({"error": "Leave request not found"}, status=404)

        # Check permission to cancel
        allowed_roles = ["admin", "hr", "manager"]
        is_creator = leave.employee == current_employee
        is_authority = any(role in current_employee.role.name.lower() for role in allowed_roles)

        if not is_creator and not is_authority:
            return Response({"error": "You are not authorized to cancel this leave"}, status=403)

        # Only cancel if it's pending or approved
        if leave.status.name.lower() not in ["pending", "approved"]:
            return Response({"error": f"Cannot cancel a leave with status '{leave.status.name}'"}, status=400)

        # Revert leave balance if it was approved
        if leave.status.name.lower() == "approved":
            try:
                balance = LeaveBalance.objects.get(employee=leave.employee, leave_type=leave.leave_type, deleted=False)
                balance.used -= float(leave.total_days or 0)
                balance.used = max(balance.used, 0)
                balance.save()
            except LeaveBalance.DoesNotExist:
                return Response({"error": "Leave balance not found"}, status=404)

            # Delete logs and attendance
            LeaveLog.objects.filter(leave_request=leave).delete()
            Attendence.objects.filter(
                employee=leave.employee,
                check_in_date__range=[leave.from_date, leave.to_date],
                status__name__iexact="on leave"
            ).delete()

        # Mark leave as "Cancelled"
        try:
            cancelled_status = LeaveStatus.objects.get(name__iexact="cancelled", deleted=False)
        except LeaveStatus.DoesNotExist:
            cancelled_status = LeaveStatus.objects.create(name="Cancelled")

        leave.status = cancelled_status
        leave.save()

        return Response({"message": "Leave cancelled successfully", "status": 200})


#! leave request approval
class ApproveLeaveRequest(APIView):
    def post(self, request):
        data = request.data
        leave_id = data.get("leave_id")
        status_id = data.get("status_id")  
        remarks = data.get("remarks", "")

        if not leave_id or not status_id:
            return Response({"error": "leave_id and status_id are required", "status": 400})

        # Get approver
        try:
            approver = Employee.objects.get(user=request.user, deleted=False)
        except Employee.DoesNotExist:
            return Response({"error": "Approver not found", "status": 404})

        allowed_roles = ["hr", "admin", "manager"]
        if not any(role in approver.role.name.lower() for role in allowed_roles):
            return Response({"error": "Unauthorized to approve leaves", "status": 403})

        # Get LeaveRequest
        try:
            leave_request = LeaveRequest.objects.get(id=leave_id, deleted=False)
        except LeaveRequest.DoesNotExist:
            return Response({"error": "Leave request not found", "status": 404})
        

        # Track previous status
        previous_status = leave_request.status.name.lower() if leave_request.status else ""

        # Get new status
        try:
            status = LeaveStatus.objects.get(id=status_id, deleted=False)
        except LeaveStatus.DoesNotExist:
            return Response({"error": "Invalid leave status", "status": 400})

        # Prevent re-approval or redundant status change
        if leave_request.status and leave_request.status.id == status.id:
            return Response({
                "message": f"Leave request is already marked as '{status.name}'",
                "status": 400
            })

        # Apply new status
        leave_request.status = status
        leave_request.approved_by = approver
        leave_request.remarks_by_superior = remarks
        leave_request.save()

        # ========== APPROVED ==========
        if status.name.lower() == "approved":
            try:
                balance = LeaveBalance.objects.get(
                    employee=leave_request.employee,
                    leave_type=leave_request.leave_type,
                    deleted=False
                )
                balance.used += float(leave_request.total_days or 0)
                balance.save()

                # Create leave logs
                current_date = leave_request.from_date
                while current_date <= leave_request.to_date:
                    if current_date.weekday() not in WEEKENDS:
                        LeaveLog.objects.get_or_create(
                            employee=leave_request.employee,
                            leave_type=leave_request.leave_type,
                            date=current_date,
                            leave_request=leave_request,
                            defaults={"is_half_day": leave_request.is_half_day}
                        )
                    current_date += timedelta(days=1)

            except LeaveBalance.DoesNotExist:
                return Response({"error": "Leave balance not found", "status": 404})

            # Create attendance entries for approved leave
            try:
                on_leave_status = AttendenceStatus.objects.get(name__iexact="on leave", deleted=False)
            except AttendenceStatus.DoesNotExist:
                on_leave_status = AttendenceStatus.objects.create(name="On Leave", acronym="OL")

            current_date = leave_request.from_date
            while current_date <= leave_request.to_date:
                if current_date.weekday() not in WEEKENDS:
                    Attendence.objects.get_or_create(
                        employee=leave_request.employee,
                        check_in_date=current_date,
                        defaults={
                            "status": on_leave_status,
                            "remarks": "Auto-marked as on leave",
                            "total_working_hour": "00:00"
                        }
                    )
                current_date += timedelta(days=1)

        # ========== REJECTED or CANCELLED ==========
        elif status.name.lower() in ["rejected", "cancelled"] and previous_status == "approved":
            try:
                balance = LeaveBalance.objects.get(
                    employee=leave_request.employee,
                    leave_type=leave_request.leave_type,
                    deleted=False
                )
                balance.used -= float(leave_request.total_days or 0)
                balance.used = max(balance.used, 0)
                balance.save()
            except LeaveBalance.DoesNotExist:
                return Response({"error": "Leave balance not found", "status": 404})

            # Clean up logs and attendance
            LeaveLog.objects.filter(leave_request=leave_request).delete()
            Attendence.objects.filter(
                employee=leave_request.employee,
                check_in_date__range=[leave_request.from_date, leave_request.to_date],
                status__name__iexact="on leave"
            ).delete()

        # Skip attendance/log creation for rejected/cancelled
        if status.name.lower() not in ["rejected", "cancelled"]:
            try:
                on_leave_status = AttendenceStatus.objects.get(name__iexact="on leave", deleted=False)
            except AttendenceStatus.DoesNotExist:
                on_leave_status = AttendenceStatus.objects.create(name="On Leave", acronym="OL")

            current_date = leave_request.from_date
            while current_date <= leave_request.to_date:
                if current_date.weekday() not in WEEKENDS:
                    LeaveLog.objects.get_or_create(
                        employee=leave_request.employee,
                        leave_type=leave_request.leave_type,
                        date=current_date,
                        leave_request=leave_request,
                        defaults={
                            "is_half_day": leave_request.is_half_day,
                            "status": status,
                            "approved_by": approver,
                            "remarks": remarks
                        }
                    )

                    Attendence.objects.get_or_create(
                        employee=leave_request.employee,
                        check_in_date=current_date,
                        defaults={
                            "status": on_leave_status,
                            "remarks": "Auto-marked as on leave",
                            "total_working_hour": "00:00"
                        }
                    )
                current_date += timedelta(days=1)

        # Final response
        serializer = LeaveRequestSerializer(leave_request)
        return Response({
            "data": serializer.data,
            "message": f"Leave request updated to '{status.name}' successfully",
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
        try:
            employee = Employee.objects.get(user=request.user, deleted=False)
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


#! log
def create_leave_log(leave_request):
    start = leave_request.from_date
    end = leave_request.to_date
    is_half_day = leave_request.is_half_day

    for i in range((end - start).days + 1):
        leave_date = start + timedelta(days=i)

        # Skip weekends
        if leave_date.weekday() in WEEKENDS:
            continue

        LeaveLog.objects.get_or_create(
            leave_request=leave_request,
            employee=leave_request.employee,
            leave_type=leave_request.leave_type,
            date=leave_date,
            defaults={'is_half_day': is_half_day}
        )


# log for daily attendance/audit
class LeaveLogListView(APIView):
    def get(self, request):
        logs = LeaveLog.objects.filter(leave_request__deleted=False).order_by("-date")
        serializer = LeaveLogSerializer(logs, many=True)
        return Response({"data": serializer.data, "status": 200})

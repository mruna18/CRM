from django.shortcuts import render
from api.models import *
from .models import *
from .serializers import *
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Q
from datetime import datetime, timedelta

# Create your views here.
class CreateStatus(APIView):
    def post(self, request):
        data=request.data
        if AttendenceStatus.objects.filter(
            Q(name__iexact=data.get('name'))|
            Q(acronym__iexact=data.get('acronym'))).exists():

            return Response({"msg":"Name or acronym already exists","status":500})
        serializer=AttendenceStatusSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"data": serializer.data.copy(),"status":200})
        return Response({"msg":serializer.errors,"status":500})
    
class GetAllStatus(APIView):
    def get(self, request):
        data = AttendenceStatus.objects.filter(deleted=False)
        serializer = AttendenceStatusSerializer(data, many = True)
        return Response({"data": serializer.data.copy(),"status":200})

class GetStatus(APIView):
    def get(self, request, id):
        try:
            status = AttendenceStatus.objects.get(id=id, deleted=False)
        except AttendenceStatus.DoesNotExist:
            return Response({"msg": "Status not found", "status": 404})

        serializer = AttendenceStatusSerializer(status)
        return Response({"data": serializer.data.copy(), "status": 200})
    
class EditStatus(APIView):
    def post(self, request):
        data = request.data
        if AttendenceStatus.objects.filter(
            Q(name__iexact=data.get('name'))|
            Q(acronym__iexact=data.get('acronym'))).exists():
            return Response({"msg":"Name or acronym already exists","status":500})
        status = AttendenceStatus.objects.get(id=data.get("id"),deleted = False)
        serializer = AttendenceStatusSerializer(status, data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({"data": serializer.data.copy(),"status":200})
        return Response({"msg": serializer.errors,"status":500})

class DeleteStatus(APIView):
    def get(self, request, id):
        if Attendence.objects.filter(status=id).exists():
            return Response({"msg":"Status cannot be deleted as it is in use","status":500})
        AttendenceStatus.objects.filter(id=id).update(deleted = True)
        return Response({"msg":"Status deleted successfully","status":200})

#! attendence

class CreateAttendence(APIView):
    def post(self, request):
        data = request.data.copy()

        employee_id = data.get('employee')
        check_in_date = data.get('check_in_date')
        status_id = data.get('status')

        if not employee_id or not check_in_date or not status_id:
            return Response({"error": "employee, status and check_in_date are required", "status": 400})

        # Validate employee
        try:
            Employee.objects.get(id=employee_id, deleted=False)
        except Employee.DoesNotExist:
            return Response({"error": "Employee not found", "status": 404})

        # Prevent duplicates
        if Attendence.objects.filter(employee_id=employee_id, check_in_date=check_in_date, deleted=False).exists():
            return Response({"error": "Attendance already exists for this employee on this date", "status": 409})

        # Validate status
        try:
            status = AttendenceStatus.objects.get(id=status_id, deleted=False)
        except AttendenceStatus.DoesNotExist:
            return Response({"error": "Status not found", "status": 404})

        status_name = status.name.lower()

        # Handle status-based conditions
        if status_name in ["absent", "week off", "sick leave", "casual leave", "compensatory off"]:
            data["check_in"] = None
            data["check_out"] = None
            data["total_working_hour"] = "00:00"
        elif status_name == "half day":
            data["total_working_hour"] = "04:00"
        else:
            # Calculate working hours if check_in and check_out are provided
            check_in = data.get("check_in")
            check_out = data.get("check_out")
            if check_in and check_out:
                try:
                    in_time = datetime.strptime(check_in, "%H:%M:%S")
                    out_time = datetime.strptime(check_out, "%H:%M:%S")
                    if out_time > in_time:
                        delta = out_time - in_time
                        hours, remainder = divmod(delta.seconds, 3600)
                        minutes = remainder // 60
                        data["total_working_hour"] = f"{hours:02d}:{minutes:02d}"
                except Exception as e:
                    return Response({"error": f"Error calculating hours: {str(e)}", "status": 400})

        serializer = AttendenceSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({"data": serializer.data, "status": 201})

        return Response({"error": serializer.errors, "status": 400})
    
#update
class UpdateAttendence(APIView):
    def post(self, request):
        data = request.data.copy()
        attendence_id = data.get("id")

        if not attendence_id:
            return Response({"error": "Attendance ID is required", "status": 400})

        try:
            attendence = Attendence.objects.get(id=attendence_id, deleted=False)
        except Attendence.DoesNotExist:
            return Response({"error": "Attendance not found", "status": 404})

        # Validate employee
        employee_id = data.get("employee")
        if employee_id:
            try:
                Employee.objects.get(id=employee_id, deleted=False)
            except Employee.DoesNotExist:
                return Response({"error": "Employee not found", "status": 404})

        # Validate unique constraint (only if employee or date changed)
        check_in_date = data.get("check_in_date")
        if employee_id and check_in_date:
            if Attendence.objects.filter(
                employee_id=employee_id,
                check_in_date=check_in_date,
                deleted=False
            ).exclude(id=attendence_id).exists():
                return Response({
                    "error": "Attendance already exists for this employee on this date.",
                    "status": 409
                })

        # Validate status
        status_id = data.get("status")
        if status_id:
            try:
                status = AttendenceStatus.objects.get(id=status_id, deleted=False)
                status_name = status.name.lower()
            except AttendenceStatus.DoesNotExist:
                return Response({"error": "Status not found", "status": 404})
        else:
            status_name = attendence.status.name.lower() if attendence.status else ""

        # Apply logic based on status
        if status_name in ["absent", "week off", "sick leave", "casual leave", "compensatory off"]:
            data["check_in"] = None
            data["check_out"] = None
            data["total_working_hour"] = "00:00"
        elif status_name == "half day":
            data["total_working_hour"] = "04:00"
        else:
            check_in = data.get("check_in")
            check_out = data.get("check_out")
            if check_in and check_out:
                try:
                    in_time = datetime.strptime(check_in, "%H:%M:%S")
                    out_time = datetime.strptime(check_out, "%H:%M:%S")
                    if out_time > in_time:
                        delta = out_time - in_time
                        hours, remainder = divmod(delta.seconds, 3600)
                        minutes = remainder // 60
                        data["total_working_hour"] = f"{hours:02d}:{minutes:02d}"
                except Exception as e:
                    return Response({"error": f"Error calculating hours: {str(e)}", "status": 400})

        serializer = AttendenceSerializer(attendence, data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({"data": serializer.data, "status": 200})

        return Response({"error": serializer.errors, "status": 400})


# get all

class GetAllAttendence(APIView):
    def get(self, request):
        filters = Q(deleted=False)

        employee_id = request.GET.get("employee")
        check_in_date = request.GET.get("date")

        if employee_id:
            filters &= Q(employee_id=employee_id)
        if check_in_date:
            try:
                date_obj = datetime.strptime(check_in_date, "%Y-%m-%d").date()
                filters &= Q(check_in_date=date_obj)
            except ValueError:
                return Response({"error": "Invalid date format. Use YYYY-MM-DD", "status": 400})

        attendences = Attendence.objects.filter(filters).order_by("-check_in_date")
        serializer = AttendenceSerializer(attendences, many=True)

        return Response({"data": serializer.data, "status": 200})
    
#id
class GetAttendenceById(APIView):
    def get(self, request, id):
        try:
            attendence = Attendence.objects.get(id=id, deleted=False)
        except Attendence.DoesNotExist:
            return Response({"error": "Attendance not found", "status": 404})

        serializer = AttendenceSerializer(attendence)
        return Response({"data": serializer.data, "status": 200})
    
#delete
class DeleteAttendence(APIView):
    def delete(self, request, id):
        try:
            attendence = Attendence.objects.get(id=id, deleted=False)
        except Attendence.DoesNotExist:
            return Response({"error": "Attendance not found", "status": 404})

        attendence.deleted = True
        attendence.save()

        return Response({"msg": "Attendance deleted successfully", "status": 200})


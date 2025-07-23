from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import *
from .serializers import *
from rest_framework.permissions import IsAuthenticated
from .shortcut import get_pagination
from django.db.models import Q, F, Value
from django.db.models.functions import Concat
from django.core.paginator import Paginator, EmptyPage
from django.contrib.auth.models import User
from .models import Employee
from .serializers import EmployeeSerializer


# Create your views here.
#Employee creation 
class EmployeeCreate(APIView):
    # permission_classes = [IsAuthenticated]
    def post(self, request, *args, **kwargs):
        data = request.data
        required_fields = ["first_name","last_name","branch", "department", "role", "designation", "email", "mobile_no"]
        for field in required_fields:
            if not data.get(field):
                return Response({"error": f"{field} cannot be null", "status": "500"})
        # if not request.user.employee.role.can_create_employees:
        #     return Response({"error": "You don't have permission to create employees."}, status=403)
        if Employee.objects.filter(email=data["email"], deleted=False).exists():
            return Response({"error": "An employee with this email already exists.", "status": "500"})
        if Employee.objects.filter(mobile_no=data["mobile_no"], deleted=False).exists():
            return Response({"error": "An employee with this phone number already exists.", "status": "500"})
        user, created = User.objects.get_or_create(
            username=data["mobile_no"],
            defaults={
                "first_name": data.get("first_name", ""),
                "last_name": data.get("last_name", ""),
                "email": data["email"],
                "is_active": True,
                "is_superuser": False,
            }
        )
        if created:
            user.set_password(data["mobile_no"])
            user.save()
        if not created:
            return Response({"error": "A user with this mobile number already exists.", "status": "500"})
        current_user = request.user
        try:
            current_employee = Employee.objects.get(user=current_user, deleted=False)
        except Employee.DoesNotExist:
            current_employee = None
        data["user"] = user.id
        if current_employee:
            data["superior"] = current_employee.id  # Assign the logged-in user's employee ID as the superior
        serializer = EmployeeSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({"data": "Employee created successfully", "status": "200"})
        
        return Response({"error": "Employee creation failed", "status": "500"})

#list employee 
class EmployeeListGet(APIView):
    def get(self, request,keyw):
        """ Fetches employees based on search and department filters, with pagination. """
        data = request.data
        """ Fetches employees based on search and department filters, with pagination. """
        filters = Q(deleted=False)

        # Search filter
        if keyw.startswith("s=") and len(keyw) > 2:
            search_term = keyw[2:]
            filters &= (
                Q(first_name__icontains=search_term) |
                Q(last_name__icontains=search_term) |
                Q(email__icontains=search_term) |
                Q(mobile_no__icontains=search_term)
            )

        # Extract filters safely from request.GET
        department_id = request.GET.get("department_id")
        department_name = request.GET.get("department_name")
        designation_id = request.GET.get("designation_id")
        designation_name = request.GET.get("designation_name")
        role_id = request.GET.get("role_id")
        role_name = request.GET.get("role_name")
        branch_id = request.GET.get("branch_id")
        branch_name = request.GET.get("branch_name")

        # Apply filters if values exist
        if department_id:
            filters &= Q(department=department_id)
        if department_name:
            filters &= Q(department__name__icontains=department_name)
        if designation_id:
            filters &= Q(designation=designation_id)
        if designation_name:
            filters &= Q(designation__designation_name__icontains=designation_name)
        if role_id:
            filters &= Q(role=role_id)
        if role_name:
            filters &= Q(role__name__icontains=role_name)
        if branch_id:
            filters &= Q(branch=branch_id)
        if branch_name:
            filters &= Q(branch__branchName__icontains=branch_name)

        # Fetch employees with annotations
        employees = Employee.objects.filter(filters).annotate(
            full_name=Concat(F('first_name'), Value(' '), F('last_name')),
            role_name=F('role__name'),
            department_name=F('department__name'),
            branch_name=F('branch__branchName'),
            superior_name=Concat(F('superior__first_name'), Value(' '), F('superior__last_name')),
            designation_name=F('designation__designation_name')
        ).order_by('id')

        if data.get('pagination', False):
            page_number = data.get('page_number', 1)
            limit = data.get('limit', 10)
            paginator = Paginator(employees, limit)
            try:
                page = paginator.page(page_number)
            except EmptyPage:
                page = paginator.page(paginator.num_pages)
            serializer = EmployeeSerializer(page, many=True)
            return Response({
                "data": serializer.data,
                "pagination_data": {'total_data': paginator.count,'limit': limit,'total_pages': paginator.num_pages,'page_number': page.number,'next_page': page.has_next(),'previous_page': page.has_previous()},
                "status": 200
            })
        return Response({"data": list(employees.values()), "status": 200})
    

class EmployeeDetailGet(APIView):
    def get(self, request, pk):
        try:
            employee = Employee.objects.select_related(
                'department', 'role', 'branch', 'designation', 'superior', 'user'
            ).get(id=pk, deleted=False)
        except Employee.DoesNotExist:
            return Response({"error": "Employee not found", "status": "500"})

        serializer = EmployeeSerializer(employee)
        data = serializer.data.copy()

        # Add nested objects manually
        data['department'] = {
            "id": employee.department.id,
            "name": employee.department.name,
            "description": employee.department.description,
            "branch_id": employee.department.branch.id if employee.department.branch else None,
        } if employee.department else None

        data['role'] = {
            "id": employee.role.id,
            "name": employee.role.name,
            "description": employee.role.description,
            "level_id": employee.role.level.id if employee.role.level else None,
        } if employee.role else None

        data['branch'] = {
            "id": employee.branch.id,
            "branchName": employee.branch.branchName,
            "address": employee.branch.address,
            "city": employee.branch.city,
            "state_id": employee.branch.state.id if employee.branch.state else None,
            "pincode": employee.branch.pincode,
        } if employee.branch else None

        data['designation'] = {
            "id": employee.designation.id,
            "designation_name": employee.designation.designation_name,
            "description": employee.designation.description,
            "department_id": employee.designation.department.id if employee.designation.department else None,
        } if employee.designation else None

        data['superior'] = {
            "id": employee.superior.id,
            "name": f"{employee.superior.first_name} {employee.superior.last_name}"
        } if employee.superior else None

        data['user'] = {
            "id": employee.user.id,
            "first_name": employee.user.first_name,
            "last_name": employee.user.last_name,
            "email": employee.user.email,
            "username": employee.user.username
        } if employee.user else None

        return Response({'data': data, 'status': 200})


class EmployeeUpdate(APIView):
    def post(self, request, pk, *args, **kwargs):
        data = request.data
        required_fields = ["branch", "department", "role", "designation", "email", "mobile_no"]
        for field in required_fields:
            if not data.get(field):
                return Response({"error": f"{field} cannot be null", "status": "500"})
        try:
            employee = Employee.objects.get(id=pk, deleted=False)
        except Employee.DoesNotExist:
            return Response({"error": "Employee not found", "status": "500"})
        if Employee.objects.filter(email=data["email"], deleted=False).exclude(id=employee.id).exists():
            return Response({"error": "An employee with this email already exists.", "status": "500"})
        if Employee.objects.filter(mobile_no=data["mobile_no"], deleted=False).exclude(id=employee.id).exists():
            return Response({"error": "An employee with this phone number already exists.", "status": "500"})
        print(request.user.id)
        try:
            current_employee = Employee.objects.get(user=request.user.id, deleted=False)
        except Employee.DoesNotExist:
            return Response({"error": "Unauthorized access", "status": "500"})
        if current_employee != (employee.superior if employee.superior else None):
            return Response({"error": "You are not authorized to update this employee", "status": "500"})
        user = employee.user
        if not user:
            return Response({"error": "User not linked to employee", "status": "500"})
        user.first_name = data.get("first_name", user.first_name)
        user.last_name = data.get("last_name", user.last_name)
        user.email = data["email"]  # Email must always be updated
        if user.username != data["mobile_no"]:
            if User.objects.filter(username=data["mobile_no"]).exclude(id=user.id).exists():
                return Response({"error": "Another user with this mobile number already exists.", "status": "500"})
            user.username = data["mobile_no"]  # Set mobile_no as username
        user.save()
        serializer = EmployeeSerializer(employee, data=data, partial=True)  # partial=True allows updating only provided fields
        if serializer.is_valid():
            serializer.save()
            return Response({"data": "Employee updated successfully", "status": "200"})
        return Response({"error": "Employee update failed", "status": "500"})

class EmployeeDelete(APIView):
    def post(self, request, pk, *args, **kwargs):
        try:
            employee = Employee.objects.get(id=pk, deleted=False)
        except Employee.DoesNotExist:
            return Response({"error": "Employee not found", "status": "500"})
        try:
            current_employee = Employee.objects.get(user=request.user, deleted=False)
        except Employee.DoesNotExist:
            return Response({"error": "Unauthorized access", "status": "500"})
        if current_employee.id != (employee.superior.id if employee.superior else None):
            return Response({"error": "You are not authorized to delete this employee", "status": "500"})
        employee.deleted = True
        employee.save()
        if employee.user:
            user = User.objects.get(id=employee.user.id)  # Ensure fetching user separately
            user.is_active = False
            user.save()   
        return Response({"data": "Employee deleted successfully", "status": "200"})
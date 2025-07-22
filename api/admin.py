from django.contrib import admin
from .models import (
    State, LevelTypes, BusinessInfo,
    Role, Branch, Department, Designation, Employee
)

@admin.register(State)
class StateAdmin(admin.ModelAdmin):
    list_display = ('id', 'state', 'state_code')
    search_fields = ('state',)
    ordering = ('state',)

@admin.register(LevelTypes)
class LevelTypesAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)

@admin.register(BusinessInfo)
class BusinessInfoAdmin(admin.ModelAdmin):
    list_display = ('id', 'company_name')
    search_fields = ('company_name',)

@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'level', 'deleted')
    search_fields = ('name',)
    list_filter = ('level', 'deleted')

@admin.register(Branch)
class BranchAdmin(admin.ModelAdmin):
    list_display = ('id', 'branchName', 'address', 'city', 'state', 'pincode', 'deleted')
    search_fields = ('branchName', 'city', 'pincode')
    list_filter = ('state', 'deleted')

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'branch', 'deleted')
    search_fields = ('name',)
    list_filter = ('branch', 'deleted')

@admin.register(Designation)
class DesignationAdmin(admin.ModelAdmin):
    list_display = ('id', 'designation_name', 'level', 'department', 'deleted')
    search_fields = ('designation_name',)
    list_filter = ('level', 'department', 'deleted')

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'first_name',
        'last_name',
        'email',
        'mobile_no',
        'designation',
        'branch',
        'department',
        'role',
        'superior',
        'user',
        'deleted',
    )
    search_fields = ('first_name', 'last_name', 'email', 'mobile_no')
    list_filter = ('branch', 'department', 'role', 'deleted')
    ordering = ('-id',)
    autocomplete_fields = ['user', 'superior']

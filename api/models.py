from django.db import models
from django.contrib.auth.models import User


class State(models.Model):
    state = models.CharField(max_length=75, null=True, blank=True)
    state_code = models.IntegerField(null=True, blank=True)

    class Meta:
        db_table = 'State'

class LevelTypes(models.Model):
    name=models.CharField(max_length=20,null=False,blank=False)

    class Meta:
        db_table = 'leveltypes'

class BusinessInfo(models.Model):
    company_name = models.CharField(max_length=100,unique= True)

    class Meta:
        db_table = 'BusinessInfo'

class Role(models.Model):
    name = models.CharField(max_length=100, unique=True, null= False, blank=False)
    description = models.TextField(blank=True)
    level = models.ForeignKey(LevelTypes, on_delete=models.SET_NULL,null=True,blank=True)
    Permission = models.JSONField(blank=True, null=True)
    deleted = models.BooleanField(default=False)

    class Meta:
        db_table = 'Role'
        ordering = ['level']  

    def __str__(self):
        return self.name
    
class Branch(models.Model):
    branchName = models.CharField(max_length=50, unique=True, null=False,blank=False)
    address = models.CharField(max_length=200)
    city = models.CharField(max_length=50)
    state = models.ForeignKey(State, on_delete=models.SET_NULL, null=True, blank=True) 
    pincode = models.CharField(max_length=6)
    deleted = models.BooleanField(default=False)

    class Meta:
        db_table = 'Branch'
        
class Department(models.Model):
    name = models.CharField(max_length=100, null=False, blank=False)
    description = models.TextField(blank=True)
    branch = models.ForeignKey(Branch, on_delete=models.SET_NULL, null=True, blank=True)
    deleted = models.BooleanField(default=False)

    class Meta:
        db_table = 'Department'
        unique_together = ['name', 'branch']  # Ensures the combination of name and branch is unique.

    def __str__(self):
        return self.name
        

class Designation(models.Model):
    designation_name = models.CharField(max_length=50, null=False,blank=False)
    description = models.CharField(max_length=200)
    level = models.ForeignKey(LevelTypes, on_delete=models.SET_NULL,null=True,blank=True)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, related_name='department',null=True,blank=True)
    deleted = models.BooleanField(default=False)
    class Meta:
        db_table = 'Designation'
        
    def __str__(self):
        return self.designation_name

class Employee(models.Model):
    email = models.EmailField(max_length=150, null=False, blank=False)
    mobile_no = models.CharField(max_length=20, null=False, blank=False)
    first_name = models.CharField(max_length=30, blank=False)
    last_name = models.CharField(max_length=30, blank=False)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True)
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True, blank=True) 
    branch = models.ForeignKey(Branch, on_delete=models.SET_NULL, null=True, blank=True) 
    designation = models.ForeignKey(Designation, on_delete=models.SET_NULL, null=True, blank=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='employee', null=True, blank=True) 
    superior = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True)
    deleted = models.BooleanField(default=False)

    class Meta:
        db_table = 'Employee'

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
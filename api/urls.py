from django.urls import path
from django.conf.urls.static import static
from crm import settings
from .views import *

urlpatterns = [
    path('get_employee/<str:keyw>', EmployeeListGet.as_view(), name='Employee-list'),  #!!!!!!!!
    path('create_employee/', EmployeeCreate.as_view(), name='Employee-create'),
    path('particular_employee/<int:pk>/', EmployeeDetailGet.as_view(), name='Employee-detail'),
    path('edit_employee/<int:pk>/', EmployeeUpdate.as_view(), name='Employee-update'),
    path('delete_employee/<int:pk>/', EmployeeDelete.as_view(), name='Employee-delete'),
]
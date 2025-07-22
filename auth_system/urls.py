from django.urls import path
from rest_framework_simplejwt.views import *
from .views import *

urlpatterns = [
    # JWT Token endpoints
    path('token/', TokenObtainPairView.as_view(), name='pairtoken'),
    path('refresh_token/', CustomTokenRefreshView.as_view(), name='refresh_token'),
    
    # Authentication endpoints
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    
    # Additional endpoints
    # path('employee_permissions/', GetEmployeePermision.as_view(), name='employee_permissions'),
    # path('send-otp/', OtpValidateion.as_view(), name='send_otp'),
]
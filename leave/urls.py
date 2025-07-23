from django.urls import path
from .views import *

urlpatterns = [

    #leave type
    path("leave-type/create/", CreateLeaveType.as_view()),
    path("leave-type/all/", GetAllLeaveTypes.as_view()),
    path("leave-type/<int:id>/", GetLeaveTypeById.as_view()),
    path("leave-type/update/", UpdateLeaveType.as_view()),
    path("leave-type/delete/<int:id>/", DeleteLeaveType.as_view()),

    # leave status
    path("leave-status/create/", CreateLeaveStatus.as_view()),
    path("leave-status/all/", GetAllLeaveStatuses.as_view()),
    path("leave-status/<int:id>/", GetLeaveStatusById.as_view()),
    path("leave-status/update/", UpdateLeaveStatus.as_view()),
    path("leave-status/delete/<int:id>/", DeleteLeaveStatus.as_view()),

    # leave balance
    path('leave/balance/', LeaveBalanceView.as_view(), name='leave-balance-list'),
    path('leave/balance/<int:employee_id>/', LeaveBalanceForEmployee.as_view(), name='leave-balance-employee'),

    #leave
    path('create/', CreateLeave.as_view(), name='create-leave'),
    # path('leave/', GetAllLeaves.as_view(), name='get-all-leaves'),
    # path('leave/<int:id>/', GetLeave.as_view(), name='get-leave'),
    # path('leave/update/', UpdateLeave.as_view(), name='update-leave'),
    # path('leave/delete/<int:id>/', DeleteLeave.as_view(), name='delete-leave'),
]

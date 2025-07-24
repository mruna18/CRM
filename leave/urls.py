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
    path('balance/', LeaveBalanceView.as_view(), name='leave-balance-list'),
    path('balance/<int:employee_id>/', LeaveBalanceForEmployee.as_view(), name='leave-balance-employee'),

    #leave
    path('create-leave/', CreateLeave.as_view(), name='create-leave'),
    path('approve-leave/', ApproveLeaveRequest.as_view(), name='approve-leave'),
    path('get-leave/', GetAllLeaveRequests.as_view(), name='get-all-leaves'),
    path('get-leave/all/', GetAllLeaveRequestsAdmin.as_view(), name='get-all-leaves'), #! check when add authentication
    path('leave/<int:id>/', GetLeaveRequestDetail.as_view(), name='get-leave'),
    path('update-leave/', UpdateLeaveRequest.as_view(), name='update-leave'),
    path('delete-leave/<int:id>/', DeleteLeaveRequest.as_view(), name='delete-leave'),

    #log
    path("logs/", LeaveLogListView.as_view(), name="leave-logs"),
    path("summary-log/", LeaveSummaryLogListView.as_view(), name="leave-summary-log-list"),
]


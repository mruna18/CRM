from django.urls import path
from .views import *

urlpatterns = [
    # status 
    path('status/create/', CreateStatus.as_view(), name='create-status'),
    path('status/all/', GetAllStatus.as_view(), name='get-all-status'),
    path('status/<int:id>/', GetStatus.as_view(), name='get-status'),
    path('status/edit/', EditStatus.as_view(), name='edit-status'),
    path('status/delete/<int:id>/', DeleteStatus.as_view(), name='delete-status'),

    # Attendence
    path('create/', CreateAttendence.as_view(), name='create-Attendence'),
    path('update-attendence/', UpdateAttendence.as_view(), name='update-Attendence'),
    path('all-attendence/all/', GetAllAttendence.as_view()),
    path('get-attendence/<int:id>/', GetAttendenceById.as_view()),
    path('delete-attendence/<int:id>/', DeleteAttendence.as_view()),

]

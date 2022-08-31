from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token
from Driver_api import views

urlpatterns = [
    path('generate-api-token/', obtain_auth_token),
    path('api/login/', views.driver_login),
    path('api/drivers/round_list/', views.round_list),
    path('api/drivers/set_round_status/', views.set_round_status),
    path('api/drivers/students_bus_checks/', views.students_bus_checks),
    path('api/recent-notifications/', views.recent_notifications),
    path('api/drivers/round-students-list/<int:round_id>', views.student_list),
    path('api/drivers/reordered-students', views.reordered_students),
    path('/api/notify', views.notify),
]

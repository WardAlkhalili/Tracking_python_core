from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token
from Driver_api import views


urlpatterns = [
    path('generate-api-token/', obtain_auth_token),
    path('login/', views.driver_login),
    path('rest/driver/round_list/', views.round_list),
    path('rest/driver/round-students-list/<int:round_id>', views.student_list),
]
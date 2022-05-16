from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token
from Parent_api import views

urlpatterns = [
    # path('generate-api-token/', obtain_auth_token),
    # path('login/', views.driver_login),
    path('parents/feed-back/', views.feed_back),
    path('parents/settings/', views.settings),
    path('parents/is-student-served/', views.student_served),
    # path('round-students-list/<int:round_id>', views.student_list),
]

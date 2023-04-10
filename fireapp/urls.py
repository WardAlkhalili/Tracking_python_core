from django.contrib import admin
from django.urls import path
from fireapp import views

urlpatterns = [
    path('api/bus_location/<int:bus_id>/<str:school_name>', views.Get_last_bus_location),
    path('api/schools/route', views.Get_round_locations),
    path('api/send_confirmation_message_to_parent', views.send_confirmation_message_to_parent),
    path('api/send_dri', views.send_dri),
    path('api/send_survey_message_to_parent', views.send_survey_message_to_parent),
    path('api/send-school-message', views.send_school_message),
    path('rt/api/schools/push-notification', views.push_notification),
    

    # path('api/send_confirmation_message_to_parent', views.send_confirmation_message_to_parent),
    # path('index/', views.index, name='index'),
]

from django.contrib import admin
from django.urls import path
from fireapp import views

urlpatterns = [
    path('api/bus_location/<int:bus_id>/<str:school_name>', views.Get_last_bus_location),
    path('api/schools/route', views.Get_round_locations),
    # path('index/', views.index, name='index'),
]

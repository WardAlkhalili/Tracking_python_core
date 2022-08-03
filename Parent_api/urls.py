from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token
from Parent_api import views

urlpatterns = [
    path('parents/login/', views.parent_login),
    path('parents/feed-back/', views.feed_back),
    path('parents/settings/', views.settings),
    path('parents/is-student-served/', views.student_served),
    path('parents/student-pick-up-status/', views.student_pick_up),
    path('parents/kids_list', views.kids_list),
    path('parents/kids-history', views.kids_hstory),
    path('parents/pre-arrive', views.pre_arrive),
    path('parents/notify', views.notify),
]

# https://iks.staging.trackware.com/web/session/authenticate

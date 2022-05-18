from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token
from Parent_api import views

urlpatterns = [
    path('parents/login/', views.parent_login),
    path('parents/feed-back/', views.feed_back),
    path('parents/settings/', views.settings),
]

# https://iks.staging.trackware.com/web/session/authenticate
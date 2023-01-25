from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token
from Parent_api import views

urlpatterns = [
    path('parents/login/', views.parent_login),
    path('parents/feed-back/', views.feed_back),
    path('parents/settings', views.settings),
    path('parents/is-student-served/', views.student_served),
    path('parents/student-pick-up-status/', views.student_pick_up),
    path('parents/kids_list', views.kids_list),
    path('parents/kids-history', views.kids_hstory),
    path('parents/pre-arrive', views.pre_arrive),
    path('parents/post-attendance', views.post_attendance),
    path('parents/post-worksheet', views.post_workSheet),
    path('parents/post-Event', views.post_workSheet),
    path('notify', views.notify),
    path('api/get_calendar/<int:student_id>', views.get_calendar),
    path('api/get_badge/<int:student_id>', views.get_badge),
    path('api/get_clinic/<int:student_id>', views.get_clinic),
    path('api/get_attendance/<int:student_id>', views.get_attendance),
    path('api/get_assignment/<int:student_id>', views.get_student_assignment),
    path('api/get_exam/<int:student_id>', views.get_exam),
    path('api/get_badges/<int:student_id>', views.get_badge),
    path('api/get_worksheets/<int:student_id>', views.get_data_worksheets),
    path('api/get_events/<int:student_id>', views.get_event_data),
    path('api/get_worksheet_view_data/<int:wsheet>', views.get_worksheet_form_view_data),
    path('api/get_event_form_view_data/<int:event>', views.get_event_form_view_data),
    # get_form_view_data
    path('api/get_all_weekly_plans/<int:student_id>', views.get_all_weekly_plans),
    path('api/get_weekly_plan_lines/<int:student_id>/<int:plan_id>/<str:week_name>', views.get_weekly_plan_lines),
#     get_weekly_plan_lines plan_id, student_id,week_name


]

# https://iks.staging.trackware.com/web/session/authenticate

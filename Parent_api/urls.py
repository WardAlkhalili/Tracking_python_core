from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token
from Parent_api import views

urlpatterns = [
    path('parents/login/', views.parent_login),
    path('parents/logout/', views.logout),
    path('parents/feed-back/', views.feed_back),
    path('parents/settings', views.settings),
    path('parents/is-student-served/', views.student_served),
    path('parents/student-pick-up-status/', views.student_pick_up),
    path('parents/kids_list', views.kids_list),
    path('parents/kids-history', views.kids_hstory),
    # hide_message
    path('parents/hide-message', views.hide_message),
    path('parents/read-message', views.read_message),
    path('parents/hide-survey', views.hide_survey),
    path('parents/read-survey', views.read_survey),
    path('parents/kids-history-new', views.kids_hstory_new),
    path('parents/pre-arrive', views.pre_arrive),
    path('parents/post-attendance', views.post_attendance),
    path('parents/post-worksheet', views.post_workSheet),
    path('parents/post-Event', views.post_Event),
    path('parents/cancel-event', views.cancel_event),
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
    path('api/get_worksheet_view_data/<int:wsheet>/<int:std>', views.get_worksheet_form_view_data),
    path('api/get_event_form_view_data/<int:event>/<int:std>', views.get_event_form_view_data),
    path('api/get_all_weekly_plans/<int:student_id>', views.get_all_weekly_plans),
    path('api/get_weekly_plan_lines/<int:student_id>/<int:plan_id>/<str:week_name>', views.get_weekly_plan_lines),
    path('api/get_library/<int:student_id>', views.get_library),
    path('parents/post_library', views.post_library),
    path('api/get_marks/<int:student_id>', views.get_marks),
    path('api/get_time_table/<int:student_id>', views.get_time_table),
#     get_time_table
#     get_marks


]

# https://iks.staging.trackware.com/web/session/authenticate

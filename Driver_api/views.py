from builtins import map

from django.conf import settings
from django.db.models import Q
from django.utils.datetime_safe import datetime

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import *
from django.db import connections
from django.http.response import Http404, JsonResponse
from django.http import HttpResponse
from django.core.serializers import serialize
from collections import ChainMap
from rest_framework import status
from itertools import chain
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
import datetime
from datetime import date
import calendar
from pyfcm import FCMNotification
from Parent_api.models import ManagerParent
import json

# Create your views here.


@api_view(['POST'])
def driver_login(request):
    if request.method == 'POST':
        pincode = request.data.get('bus_pin')
        mobile_token = request.data.get('mobile_token')
        school_name = Manager.pincode(pincode)
        with connections[school_name].cursor() as cursor:
            cursor.execute("select  driver_id,bus_no,id  from fleet_vehicle WHERE bus_pin = %s", [pincode])
            data_id_bus = cursor.fetchall()

            cursor.execute("select name from res_partner WHERE id = %s", [data_id_bus[0][0]])
            driver_name = cursor.fetchall()

            cursor.execute("select id,name from transport_round WHERE driver_id = %s", [data_id_bus[0][0]])
            rounds_name = cursor.fetchall()

            # Authentication
            user = User.objects.all().first()
            token_auth, created = Token.objects.get_or_create(user=user)
            from django.utils.crypto import get_random_string
            unique_id = get_random_string(length=32)
            manager = Manager(token=unique_id, db_name=school_name, driver_id=data_id_bus[0][0],
                              mobile_token=mobile_token)
            manager.save()
            cursor.execute(
                "UPDATE public.res_partner SET signup_token=%s WHERE id=%s;",
                [mobile_token, data_id_bus[0][0]])
            # *------------------------------------------------------------------------------------------------*
            # Details for login setting

            cursor.execute("""
            
            select nearby_distance,lat,lng,battery_low,location_refresh_rate,timezone,utc_offset,speed_limit_watch,standstill_watch,notify_if_driver_check_in_out_geo_fence,notify_on_battery_low_of_drivers_app,notify_it_driver_turns_off_gps,user_speed_exceeded,user_no_move_time_exceeded,use_round_order from transport_setting ORDER BY ID DESC LIMIT 1
            
            """)
            login_details = cursor.fetchall()

            login_details1 = []
            columnNames = [column[0] for column in cursor.description]
            for record in login_details:
                login_details1.append(dict(zip(columnNames, record)))
            cursor.execute('select name,phone,id  from  res_company')
            company_login_info = cursor.fetchall()

            # *------------------------------------------------------------------------------------------------*
            cursor.execute("select id,round_id,day_id from round_schedule WHERE round_id = %s", [rounds_name[0][0]])
            rounds_details = cursor.fetchall()

            cursor.execute("select count(student_id) from transport_participant WHERE round_schedule_id = %s",
                           [rounds_name[0][0]])
            rounds_count_student = cursor.fetchall()

            day_list = []
            for x, y, z in rounds_details:
                cursor.execute("select  name  from school_day where id = %s", [z])
                day_name = cursor.fetchall()
                day_list.append(list(day_name))

            # *------------------------------------------------------------------------------------------------*
            # 1-List of active round

            cursor.execute("select  id,name  from transport_round WHERE is_active = %s", [True])
            active_round_list = cursor.fetchall()
            active_round_list = str(active_round_list)[1:-1]

            # 2-A student transferred to another round
            cursor.execute(
                "select  student_id,source_round_id  from transport_participant WHERE source_round_id IS NOT %s",
                [None])
            student_transferred = cursor.fetchall()
            student_transferred_list = str(student_transferred)[1:-1]

            student_name_transferred = []
            for x, y in student_transferred:
                cursor.execute("select id,display_name_search from student_student WHERE id = %s", [x])
                student_transferred = cursor.fetchall()
                student_name_transferred.append(list(student_transferred))

            student_name_transferred_list = str(student_name_transferred)[1:-1]
            result = {
                "status": "ok",
                "school_phone": company_login_info[0][1],
                "location_refresh_rate": login_details1[0]['location_refresh_rate'],
                "school_name": company_login_info[0][0],
                "school_db": school_name,
                "school_lng": login_details1[0]['lng'],
                "school_lat": login_details1[0]['lat'],
                "school_id": company_login_info[0][2],
                "utc_offset": login_details1[0]['utc_offset'],
                "timezone": login_details1[0]['timezone'],
                "tracklink": True,
                "bus_id": data_id_bus[0][2],
                "bus_number": data_id_bus[0][1],
                "driver_id": data_id_bus[0][0],
                "nearby_distance": login_details1[0]['nearby_distance'],
                "use_round_order":login_details1[0]['use_round_order'] if login_details1[0]['use_round_order'] else False,
                "notifications_text": [
                    {
                        "type": "drop-off",
                        "actions": {
                            "near_by_ar": " @student_name على وصول الى المنزل",
                            "no-show_ar": "الطالب @student_name لم يصعد للحافلة في الجولة @round_name ",
                            "check_in_ar": " @student_name صعد الى الحافلة",
                            "check_out_ar": " @student_name وصل الى المنزل",
                            "near_by_en": " @student_name  is about to arrive home.",
                            "no-show_en": " @student_name  did not show today in  @round_name ",
                            "check_in_en": " @student_name  just entered the bus.",
                            "check_out_en": " @student_name   just reached home."
                        }
                    },
                    {
                        "type": "pick-up",
                        "actions": {
                            "near_by_ar": "انت التالي، الحافلة اقتربت منك، الرجاء أن يكون @student_name مستعداَ",
                            "absent_ar": "الطالب @student_name غائب اليوم",
                            "check_in_ar": "  @student_name صعد الى الحافلة",
                            "check_out_ar": "  @student_name وصل الى المدرسة",
                            "near_by_en": "You are next in route. Please have  @student_name ready",
                            "absent_en": " @student_name  is absent today",
                            "check_in_en": " @student_name  has entered the bus",
                            "check_out_en": " @student_name  just reached the school"
                        }
                    }
                ],
                "round_cancellation_messages": [
                    {
                        "type": "cancel",
                        "actions": [
                            "Round cancellation- Round time changed.",
                            "Round cancelled by the school administrator.",
                            "Malfunction in the bus."
                        ]
                    },
                    {
                        "type": "absent",
                        "actions": [
                            "Absent- We have been informed verbally by the parent.",
                            "We waited for long time with no show."
                        ]
                    },
                    {
                        "type": "no_show",
                        "actions": [
                            "No show:- Picked up by parent.",
                            "Left in other round",
                            "Absent the whole day",
                            "We waited for long time with no show."
                        ]
                    }
                ],
                "notifications_thresholds": [
                    {
                        "battery_low": login_details1[0]['battery_low'],
                        "user_speed_exceeded": login_details1[0]['user_speed_exceeded'],
                        "user_no_move_time_exceeded": login_details1[0]['user_no_move_time_exceeded']
                    }
                ],
                "notifications_settings": [
                    {
                        "speed_limit_watch": login_details1[0]['speed_limit_watch'],
                        "standstill_watch": login_details1[0]['standstill_watch'],
                        "notify_if_driver_check_in_out_geo_fence": login_details1[0][
                            'notify_if_driver_check_in_out_geo_fence'],
                        "notify_on_battery_low_of_drivers_app": login_details1[0][
                            'notify_on_battery_low_of_drivers_app'],
                        "notify_it_driver_turns_off_gps": login_details1[0]['notify_it_driver_turns_off_gps']
                    }
                ],
                "geofenses": [],
                "Authorization": "Bearer " + unique_id, }
        return Response(result)


# cursor.execute("select id,name from transport_round WHERE id = %s",[y])


# def login_settings(self,pincode):

#     if request.method == 'GET':

#         school_name = Manager.pincode(pincode)
#         with connections[school_name].cursor() as cursor:
#             cursor.execute("select nearby_distance,lat,lng,battery_low,location_refresh_rate,timezone,utc_offset from transport_setting ORDER BY ID DESC LIMIT 1")    
#             columns2 = (x.name for x in cursor.description)        
#             login_details = cursor.fetchall()
#             login_details=str(login_details)[1:-1]

#             result = {
#                     'nearby_distance ' : str(nearby_distance)[1:-1],
#                     'lat' : str(lat)[1:-1],
#                     'lng': str(lng)[1:-1],
#                     'battery_low':str(battery_low)[1:-1],
#                     'location_refresh_rate':str(location_refresh_rate)[1:-1],
#                     'timezone':str(timezone)[1:-1],
#                     'utc_offset':str(utc_offset)[1:-1]
#                 }

#         return Response(login_details)

{
    "pincode": "iksW6O4MR"
}


@api_view(['POST'])
def round_list(request):
    if request.method == 'POST':
        if request.headers:
            if request.headers.get('Authorization'):
                if 'Bearer' in request.headers.get('Authorization'):
                    au = request.headers.get('Authorization').replace('Bearer', '').strip()
                    db_name = Manager.objects.filter(token=au).values_list('db_name')
                    driver_id = Manager.objects.filter(token=au).values_list('driver_id')

                    for e in driver_id:
                        driver_id = e[0]
                    if db_name:
                        for e in db_name:
                            school_name = e[0]

                        with connections[school_name].cursor() as cursor:
                            curr_date = date.today()
                            cursor.execute(
                                "select  id  from school_day where name = %s",
                                [calendar.day_name[curr_date.weekday()]])
                            day_id = cursor.fetchall()

                            result = {}
                            cursor.execute(
                                "select name,start_time,pick_up_address,drop_off_address,pick_up_lat,pick_up_lng,drop_off_lat,drop_off_lng,route_id,id,is_active from transport_round WHERE vehicle_id = %s and  type = %s and  active_status='active'",
                                [request.data.get('bus_id'),
                                 'drop_off' if 'drop' in request.data.get('round_type') else 'pick_up'])
                            columns = (x.name for x in cursor.description)
                            list_round = cursor.fetchall()

                            list_round1 = []

                            columnNames = [column[0] for column in cursor.description]
                            for record in list_round:
                                list_round1.append(dict(zip(columnNames, record)))

                            result1 = {}
                            round = []
                            r_id = []
                            l_round = []

                            moved_students1=[]


                            for id in list_round1:
                                moved_students = []
                                r_id.append(id['id'])
                                cursor.execute(
                                    "select id,day_id from round_schedule WHERE round_id = %s and day_id = %s",
                                    [id['id'], day_id[0][0]])
                                rounds_details = cursor.fetchall()
                                cursor.execute(
                                    "select student_id,sequence,transfer_state,source_round_id from transport_participant WHERE round_schedule_id = %s ORDER BY sequence ASC",
                                    [rounds_details[0][0]])
                                round_state_student = cursor.fetchall()



                                if round_state_student:
                                    import datetime

                                    start = datetime.datetime(datetime.datetime.now().year,datetime.datetime.now().month, datetime.datetime.now().day)
                                    end = datetime.datetime(datetime.datetime.now().year,
                                                              datetime.datetime.now().month,
                                                              datetime.datetime.now().day+1)
                                    today=str(datetime.datetime.now().year)+"-"+str(datetime.datetime.now().month)+"-"+str(datetime.datetime.now().day)
                                    for student_state in round_state_student:
                                        type_round="drop_off" if 'drop' == request.data.get('round_type') else "pick_up"
                                        cursor.execute(
                                            "select * FROM student_round_transfer  WHERE student_id = %s  and state= %s and date_from <= %s and date_to >=%s and type =%s ",
                                            [student_state[0], 'approve', today,today, type_round])
                                        student_round_transfer = cursor.fetchall()


                                        if 'drop' == request.data.get('round_type'):
                                            cursor.execute("select display_name_search from student_student WHERE id = %s ",
                                                           [student_state[0]])
                                            student_student2 = cursor.fetchall()
                                            cursor.execute(
                                                "select * FROM school_message  WHERE title = %s  and driver_id= %s and date >= %s and date <= %s and search_type=%s and message=%s",
                                                ['Pick Up By Parent', driver_id, start, datetime.datetime.now(),'buses',student_student2[0][0]])
                                            school_message = cursor.fetchall()
                                            cursor.execute(
                                                "select * FROM pickup_request  WHERE student_name_id = %s  and state= %s and date >= %s and date <= %s",
                                                [student_state[0], 'done',start, datetime.datetime.now()])
                                            pickup_request = cursor.fetchall()
                                            if pickup_request or school_message:

                                                moved_students.append(student_student2[0][0] + "</font></b><br> , has been picked up by parents")

                                        if  student_round_transfer:

                                            cursor.execute(
                                                "SELECT *FROM public.school_day_student_round_transfer_rel WHERE school_day_id =%s and student_round_transfer_id=%s",
                                                [day_id[0][0],student_round_transfer[0][0] ])
                                            school_day_student_round_transfer_rel = cursor.fetchall()

                                            if school_day_student_round_transfer_rel:
                                                if not student_state[3]:
                                                    cursor.execute("select display_name_search from student_student WHERE id = %s ",
                                                                   [student_state[0]])
                                                    student_student21 = cursor.fetchall()
                                                    moved_students.append( "The student <br><b><font color='#CE3337'>"+str(student_student21[0][0])+"</font></b><br> has been moved from this bus for this round only")
                                                else:
                                                    cursor.execute("select display_name_search from student_student WHERE id = %s ",
                                                                   [student_state[0]])
                                                    student_student21 = cursor.fetchall()
                                                    moved_students.append(
                                                        "The student <br><b><font color='#CE3337'>" + str(student_student21[0][
                                                            0]) + "</font></b><br> has been added to this round. Before you start the round please check the availability of the student on the bus and the pickup location of the studen")

                                moved_students1.append(moved_students)
                            if r_id:
                                cursor.execute(
                                    "select id,day_id,round_id from round_schedule WHERE round_id in %s and day_id =%s",
                                    [tuple(r_id), day_id[0][0]])
                                rounds_details = cursor.fetchall()
                                for id in rounds_details:
                                    l_round.append(id[2])

                                # cursor.execute(
                                #     "select name,start_time,pick_up_address,drop_off_address,pick_up_lat,pick_up_lng,drop_off_lat,drop_off_lng,route_id,id,is_active from transport_round WHERE id in %s",
                                #     [tuple(l_round)])
                                # list_round = cursor.fetchall()

                                for rec in range(len(rounds_details)):
                                    day_list = {}
                                    day_name = calendar.day_name[curr_date.weekday()]
                                    cursor.execute(
                                        "select student_id from transport_participant WHERE round_schedule_id = %s",
                                        [rounds_details[rec][0]])
                                    rounds_count_student = cursor.fetchall()
                                    st_id = []
                                    if rounds_count_student:
                                        for k in rounds_count_student:
                                            st_id.append(k[0])
                                        cursor.execute("select display_name_search from student_student WHERE id in %s",
                                                       [tuple(st_id)])
                                        student_student = cursor.fetchall()
                                        student_name = []
                                        for name in student_student:
                                            student_name.append(name[0])
                                        day_list[day_name] = student_name
                                    end = False
                                    start = False
                                    cancel = False

                                    cursor.execute(
                                        "select  name,vehicle_id,driver_id from transport_round WHERE id = %s  ",
                                        [list_round1[rec]['id']])
                                    round_info = cursor.fetchall()
                                    cursor.execute(
                                        "select  id,round_start,round_end,na from round_history WHERE round_id = %s and driver_id=%s and vehicle_id = %s and round_name=%s ORDER BY ID DESC LIMIT 1 ",
                                        [list_round1[rec]['id'], round_info[0][2], round_info[0][1],
                                         list_round1[rec]['id']])
                                    round_history = cursor.fetchall()
                                    if round_history:

                                        now = datetime.date.today()
                                        if round_history[0][2]:
                                            if round_history[0][2].strftime('%Y-%m-%d') == str(now):
                                                start = False
                                                cancel = False
                                                end = True
                                        if (round_history[0][1].strftime('%Y-%m-%d') == str(now)) and not (
                                        round_history[0][2].strftime('%Y-%m-%d') if round_history[0][2] else
                                        round_history[0][2] == str(now)) and (round_history[0][3] != 'cancel'):
                                            start = True
                                            cancel = False
                                            end = False
                                        if (round_history[0][1].strftime('%Y-%m-%d') == str(now)) and round_history[0][
                                            3] == 'cancel':
                                            end = False
                                            start = False
                                            cancel = True
                                    else:
                                        end = False
                                        start = False
                                        cancel = False
                                    result1[rec] = {
                                        "round_time": str(list_round1[rec]['start_time']),
                                        "name": str(list_round1[rec]['name']),
                                        "date": None,
                                        "pick_up_address": list_round1[rec]['pick_up_address'],
                                        "drop_off_address": list_round1[rec]['drop_off_address'],
                                        "pick_up_lat": list_round1[rec]['pick_up_lat'] if list_round1[rec][
                                            'pick_up_lat'] else 0,
                                        "pick_up_lng": list_round1[rec]['pick_up_lng'] if list_round1[rec][
                                            'pick_up_lng'] else 0,
                                        "drop_off_lat": list_round1[rec]['drop_off_lat'] if list_round1[rec][
                                            'drop_off_lat'] else 0,
                                        "drop_off_lng": list_round1[rec]['drop_off_lng'] if list_round1[rec][
                                            'drop_off_lng'] else 0,
                                        "route_id": list_round1[rec]['route_id'],
                                        "round_canceled": cancel,
                                        "round_ended": end,
                                        "round_started": start,
                                        "geofenses": {
                                            "id": 1,
                                            "name": 1,
                                            "shape_type": "polygon",
                                            "shape_attrs": {
                                                "vertices": []
                                            }
                                        },
                                        "round_id": list_round1[rec]['id'],
                                        "moved_students":moved_students1[rec],

                                        "students_list": [day_list]

                                    }


                            cursor.execute(
                                """ select 	allow_driver_change_students_location,allow_driver_to_use_beacon from transport_setting ORDER BY ID DESC LIMIT 1""")
                            login_details = cursor.fetchall()


                            for rec in range(len(result1)):
                                round.append(result1[rec])
                                result = {
                                    "school_settings": {
                                        "change_student_location": login_details[0][0],
                                        "allow_driver_to_use_beacon": login_details[0][1]
                                    },
                                    "rounds": round
                                }

                            return Response(result)
                    else:
                        result = {"status": "Token notFound"
                                  }
                        return Response(result)
                else:
                    result = {"status": "error"
                              }
                    return Response(result)
            result = {"status": "error"
                      }
            return Response(result)
        else:
            result = {"status": "error"
                      }

            return Response(result)


@api_view(['GET'])
def student_list(request, round_id):
    if request.method == 'GET':
        if request.headers:
            if request.headers.get('Authorization'):
                if 'Bearer' in request.headers.get('Authorization'):
                    au = request.headers.get('Authorization').replace('Bearer', '').strip()
                    db_name = Manager.objects.filter(token=au).values_list('db_name')
                    driver_id = Manager.objects.filter(token=au).values_list('driver_id')

                    for e in driver_id:
                        driver_id = e[0]
                    if db_name:
                        for e in db_name:
                            school_name = e[0]
                        # school_name = Manager.pincode('iksQQQ')
                        with connections[school_name].cursor() as cursor:
                            import datetime

                            curr_date = date.today()
                            cursor.execute(
                                "select  id  from school_day where name = %s",
                                [calendar.day_name[curr_date.weekday()]])
                            day_name = cursor.fetchall()
                            cursor.execute("select id,day_id from round_schedule WHERE round_id = %s and day_id = %s",
                                           [round_id, day_name[0][0]])
                            columns3 = (x.name for x in cursor.description)
                            rounds_details = cursor.fetchall()


                            day_list = {}
                            # for z in rounds_details:
                            cursor.execute(
                                "select  write_date,type,id from transport_round WHERE id = %s  ",
                                [round_id])
                            round_info1 = cursor.fetchall()

                            cursor.execute(
                                "select student_id,sequence,transfer_state,source_round_id from transport_participant WHERE round_schedule_id = %s ORDER BY sequence ASC",
                                [rounds_details[0][0]])
                            rounds_count_student = cursor.fetchall()
                            ch_in = 0
                            ch_out = 0
                            today = str(datetime.datetime.now().year) + "-" + str(
                                datetime.datetime.now().month) + "-" + str(datetime.datetime.now().day)
                            if round_info1[0][1] == 'pick_up':
                                ch_out = len(rounds_count_student)
                            else:
                                ch_in = len(rounds_count_student)

                            st_id = []
                            student_info = {}
                            for k in rounds_count_student:
                                st_id.append(k[0])
                            if rounds_count_student:
                                for student_state in rounds_count_student:
                                    type_round = round_info1[0][1]

                                    cursor.execute(
                                        "select * FROM student_round_transfer  WHERE student_id = %s  and state= %s and date_from <= %s and date_to >=%s and type =%s ",
                                        [student_state[0], 'approve', today, today, type_round])
                                    student_round_transfer = cursor.fetchall()

                                    if student_round_transfer:

                                        cursor.execute(
                                            "SELECT *FROM public.school_day_student_round_transfer_rel WHERE school_day_id =%s and student_round_transfer_id=%s",
                                            [day_name[0][0], student_round_transfer[0][0]])
                                        school_day_student_round_transfer_rel = cursor.fetchall()

                                        if school_day_student_round_transfer_rel:
                                            if not student_state[3]:
                                                student_student2 = None

                                                st_id.remove(student_state[0])

                            if st_id:
                                for std_id in st_id:
                                    cursor.execute("select * from student_student WHERE id = %s ",
                                                   [std_id])
                                    columns4 = (x.name for x in cursor.description)

                                    student_student2 = cursor.fetchall()


                                    # s = [dict(zip(columns4, row)) for row in student_student]
                                    student_student12 = []
                                    columnNames = [column[0] for column in cursor.description]



                                    if student_student2:
                                        for record in student_student2:
                                            student_student12.append(dict(zip(columnNames, record)))

                                        in_round = False
                                        out_round = False
                                        abs = False
                                        no_show = False
                                        lat = 0
                                        long = 0
                                        if round_info1[0][1] == 'pick_up':
                                            lat = student_student12[0]['pick_up_lat']
                                            long = student_student12[0]['pick_up_lng']
                                        else:
                                            lat = student_student12[0]['drop_off_lat']
                                            long = student_student12[0]['drop_off_lng']
                                        cursor.execute(
                                            "select  name,vehicle_id,driver_id from transport_round WHERE id = %s  ",
                                            [round_id])
                                        round_info = cursor.fetchall()
                                        cursor.execute(
                                            "select  id,round_start,round_end,na from round_history WHERE round_id = %s and driver_id=%s and vehicle_id = %s and round_name=%s ORDER BY ID DESC LIMIT 1 ",
                                            [round_id, round_info[0][2], round_info[0][1],
                                             round_id])
                                        round_history = cursor.fetchall()

                                        start = datetime.datetime(datetime.datetime.now().year,
                                                                  datetime.datetime.now().month,
                                                                  datetime.datetime.now().day)
                                        if round_history:


                                            now = datetime.date.today()
                                            if round_history[0][1].strftime('%Y-%m-%d') == str(now):

                                                cursor.execute(
                                                    "select  activity_type,lat,long from student_history WHERE round_id = %s and student_id=%s and history_id = %s  ORDER BY ID DESC LIMIT 1 ",
                                                    [round_id, student_student12[0]['id'], round_history[0][0]])
                                                student_history = cursor.fetchall()

                                                if student_history:

                                                    lat = student_history[0][1]
                                                    long = student_history[0][2]
                                                    if student_history[0][0] == 'in' or student_history[0][0] == 'near':

                                                        in_round = True
                                                        out_round = False
                                                        abs = False
                                                        no_show = False
                                                        cursor.execute(
                                                            "UPDATE public.transport_participant SET transport_state = %s,write_date=%s WHERE student_id =%s AND round_schedule_id= %s",
                                                            ['in',datetime.datetime.now(), student_student12[0]['id'],
                                                             rounds_details[0][0]])
                                                        if round_info1[0][1] == 'pick_up':
                                                            ch_in = ch_in + 1
                                                            ch_out = ch_out - 1
                                                        else:
                                                            ch_in = ch_in - 1
                                                            ch_out = ch_out + 1
                                                    elif student_history[0][0] == 'out':
                                                        in_round = False
                                                        out_round = True
                                                        abs = False
                                                        no_show = False
                                                        cursor.execute(
                                                            "UPDATE public.transport_participant SET transport_state = %s,write_date=%s WHERE student_id =%s AND round_schedule_id= %s",
                                                            ['out',datetime.datetime.now(), student_student12[0]['id'],
                                                             rounds_details[0][0]])
                                                        if round_info1[0][1] == 'pick_up':
                                                            ch_in = ch_in + 1
                                                            ch_out = ch_out - 1
                                                        else:

                                                            ch_in = ch_in - 1
                                                            ch_out = ch_out + 1
                                                    elif student_history[0][0] == 'no-show':
                                                        in_round = False
                                                        out_round = False
                                                        abs = False
                                                        no_show = True
                                                        cursor.execute(
                                                            "UPDATE public.transport_participant SET transport_state = %s,write_date=%s WHERE student_id =%s AND round_schedule_id= %s",
                                                            ['no_show',datetime.datetime.now(), student_student12[0]['id'],
                                                             rounds_details[0][0]])
                                                    elif student_history[0][0] == 'absent':

                                                        in_round = False
                                                        out_round = False
                                                        abs = True
                                                        no_show = False
                                                        cursor.execute(
                                                            "UPDATE public.transport_participant SET transport_state = %s,write_date=%s WHERE student_id =%s AND round_schedule_id= %s",
                                                            ['absent',datetime.datetime.now(), student_student12[0]['id'],
                                                             rounds_details[0][0]])
                                                    elif student_history[0][0] == 'absent_all':

                                                        in_round = False
                                                        out_round = False
                                                        abs = True
                                                        no_show = False

                                                        cursor.execute(
                                                            "UPDATE public.transport_participant SET transport_state = %s,write_date=%s WHERE student_id =%s AND round_schedule_id= %s",
                                                            ['absent_all',datetime.datetime.now(), student_student12[0]['id'],
                                                             rounds_details[0][0]])
                                                else:

                                                    cursor.execute(
                                                        "select  activity_type,lat,long from student_history WHERE round_id = %s and student_id=%s and datetime >= %s and datetime <= %s   ORDER BY ID DESC LIMIT 1 ",
                                                        [round_id, student_student12[0]['id'], start,
                                                         datetime.datetime.now()])
                                                    student_history1 = cursor.fetchall()

                                                    if student_history1:

                                                        if student_history1[0][0] == 'absent' or student_history1[0][
                                                            0] == 'absent-all':

                                                            in_round = False
                                                            out_round = False
                                                            abs = True
                                                            no_show = True
                                                    if round_info1[0][1] == 'pick_up':

                                                        cursor.execute(
                                                            "UPDATE public.transport_participant SET transport_state = %s,write_date=%s WHERE student_id =%s AND round_schedule_id= %s",
                                                            ['out',datetime.datetime.now(), student_student12[0]['id'],
                                                             rounds_details[0][0]])
                                                        # ch_out = len(rounds_count_student)
                                                    else:

                                                        cursor.execute(
                                                            "UPDATE public.transport_participant SET transport_state = %s,write_date=%s WHERE student_id =%s AND round_schedule_id= %s",
                                                            ['in',datetime.datetime.now(), student_student12[0]['id'],
                                                             rounds_details[0][0]])
                                                        # ch_in = len(rounds_count_student)
                                            else:

                                                cursor.execute(
                                                    "select  activity_type,lat,long from student_history WHERE round_id = %s and student_id=%s and datetime >= %s and datetime <= %s   ORDER BY ID DESC LIMIT 1 ",
                                                    [round_id, student_student12[0]['id'],start,datetime.datetime.now()])
                                                student_history1 = cursor.fetchall()

                                                if student_history1:

                                                    if round_info1[0][1] == 'pick_up':
                                                        if student_history1[0][0]=='absent' or student_history1[0][0]=='absent-all':

                                                            in_round = False
                                                            out_round = False
                                                            abs = True
                                                            no_show = False
                                                    else:

                                                        if student_history1[0][0] == 'absent' or student_history1[0][
                                                            0] == 'absent-all':
                                                            in_round = False
                                                            out_round = False
                                                            abs = True
                                                            no_show = True



                                        cursor.execute("select display_name_search from student_student WHERE id = %s ",
                                                       [student_student12[0]['id']])
                                        student_student2 = cursor.fetchall()
                                        cursor.execute(
                                            "select * FROM school_message  WHERE title = %s  and driver_id= %s and date >= %s and date <= %s and search_type=%s and message=%s",
                                            ['Pick Up By Parent', driver_id, start, datetime.datetime.now(), 'buses',
                                             student_student2[0][0]])
                                        school_message = cursor.fetchall()
                                        cursor.execute(
                                            "select * FROM pickup_request  WHERE student_name_id = %s and date <= %s and date >= %s and state= %s",
                                            [student_student12[0]['id'], datetime.datetime.now(), start, 'done'])

                                        pickup_request = cursor.fetchall()
                                        if pickup_request or school_message:
                                            if round_info1[0][1] != 'pick_up':
                                                in_round = False
                                                out_round = False
                                                abs = False
                                                no_show = True
                                        cursor.execute("select * from school_parent WHERE id = %s",
                                                       [student_student12[0]['father_id']])
                                        columns_f = (x.name for x in cursor.description)
                                        father = cursor.fetchall()
                                        father_inf = [dict(zip(columns_f, row)) for row in father]
                                        cursor.execute("select * from school_parent WHERE id = %s",
                                                       [student_student12[0]['mother_id']])
                                        columns_m = (x.name for x in cursor.description)
                                        mother = cursor.fetchall()
                                        mother_inf = [dict(zip(columns_m, row)) for row in mother]
                                        student_grade = None

                                        cursor.execute(
                                            "SELECT student_distribution_line_id FROM student_distribution_line_student_student_rel WHERE student_student_id=%s",
                                            [student_student12[0]['id']])
                                        student_distribution_line_id = cursor.fetchall()
                                        if student_distribution_line_id:
                                            cursor.execute(
                                                "SELECT academic_grade_id FROM public.student_distribution_line WHERE id = %s",
                                                [student_distribution_line_id[0][0]])
                                            student_distribution_line = cursor.fetchall()
                                            if student_distribution_line:
                                                cursor.execute(
                                                    "SELECT name FROM public.academic_grade WHERE id = %s",
                                                    [student_distribution_line[0][0]])
                                                academic_grade = cursor.fetchall()
                                                student_grade = academic_grade[0][0]
                                        if student_grade== None:
                                            # ----------------------
                                            cursor.execute(
                                                "select user_id from student_student where id=%s",
                                                [student_student12[0]['id']])
                                            user_id_q = cursor.fetchall()

                                            if user_id_q:
                                                cursor.execute(
                                                    " select partner_id from res_users where id=%s",
                                                    [user_id_q[0][0]])
                                                partner_id_q = cursor.fetchall()

                                                if partner_id_q:
                                                    cursor.execute(
                                                        "select class_id from res_partner where id=%s",
                                                        [partner_id_q[0][0]])
                                                    class_id_q = cursor.fetchall()

                                                    if class_id_q[0][0]:
                                                        cursor.execute(
                                                            "select academic_grade_id from school_class where id=%s",
                                                            [class_id_q[0][0]])
                                                        academic_grade_id_q = cursor.fetchall()

                                                        if academic_grade_id_q:
                                                            cursor.execute(
                                                                "select name from academic_grade where id=%s",
                                                                [academic_grade_id_q[0][0]])
                                                            academic_grade_q = cursor.fetchall()
                                                            student_grade = academic_grade_q[0][0]
                                            # ---------------------

                                        student_info[std_id] = {
                                            "id": student_student12[0]['id'],
                                            "year_id": student_student12[0]['year_id'],
                                            "emergency_call": student_student12[0]['emergency_call'],
                                            "display_name_search": student_student12[0]['display_name_search'],
                                            "user_id": student_student12[0]['user_id'],
                                            "color": student_student12[0]['color'],
                                            "email": student_student12[0]['email'],
                                            "mobile": student_student12[0]['mobile'],
                                            "name": student_student12[0]['display_name_search'],
                                            "contact_phone1": student_student12[0]['contact_phone1'],
                                            "contact_mobile1": student_student12[0]['contact_mobile1'],
                                            "nationality_id": student_student12[0]['nationality_id'],
                                            "admission_date": student_student12[0]['admission_date'],
                                            "second_name": student_student12[0]['second_name'],
                                            "third_name": student_student12[0]['third_name'],
                                            "last_name": student_student12[0]['last_name'],
                                            "mother_tongue": student_student12[0]['mother_tongue'],
                                            "blood_group": student_student12[0]['blood_group'],
                                            "date_of_birth": student_student12[0]['date_of_birth'],
                                            "building_number": student_student12[0]['building_number'],
                                            "building_name": student_student12[0]['building_name'],
                                            "street": student_student12[0]['street'],
                                            "flat_number": student_student12[0]['flat_number'],
                                            "area_id": student_student12[0]['area_id'],
                                            "state_id": student_student12[0]['state_id'],
                                            "address_note": student_student12[0]['address_note'],
                                            "terminate_reason": student_student12[0]['terminate_reason'],
                                            "terminate_date": student_student12[0]['terminate_date'],
                                            "alumni_date": student_student12[0]['alumni_date'],
                                            "national_id": student_student12[0]['national_id'],
                                            "passport_number": student_student12[0]['passport_number'],
                                            "religion_id": student_student12[0]['religion_id'],
                                            "country_id": student_student12[0]['country_id'],
                                            "id_number": student_student12[0]['id_number'],
                                            "is_demo": student_student12[0]['is_demo'],
                                            "birth_certificate_no": student_student12[0]['birth_certificate_no'],
                                            "issued_at": student_student12[0]['issued_at'],
                                            "issue_date": student_student12[0]['issue_date'],
                                            "previous_year_avg": student_student12[0]['previous_year_avg'],
                                            "learning_disabilities": student_student12[0]['learning_disabilities'],
                                            "need_attention": student_student12[0]['need_attention'],
                                            "attention_follow_up_notes": student_student12[0][
                                                'attention_follow_up_notes'],
                                            "special_needs": student_student12[0]['special_needs'],
                                            "health_condition_notes": student_student12[0]['health_condition_notes'],
                                            "allergies": student_student12[0]['allergies'],
                                            "allergies_desc": student_student12[0]['allergies_desc'],
                                            "bus_number": student_student12[0]['bus_number'],
                                            "state": student_student12[0]['state'],
                                            "father_id": student_student12[0]['father_id'],
                                            "mother_id": student_student12[0]['mother_id'],
                                            "family_relation_id": student_student12[0]['family_relation_id'],
                                            "message_main_attachment_id": student_student12[0][
                                                'message_main_attachment_id'],
                                            "create_uid": student_student12[0]['create_uid'],
                                            "create_date": student_student12[0]['create_date'],
                                            "write_uid": student_student12[0]['write_uid'],
                                            "write_date": student_student12[0]['write_date'],
                                            "is_banned": student_student12[0]['is_banned'],
                                            "currency_id": student_student12[0]['currency_id'],
                                            "name_ar": student_student12[0]['name_ar'],
                                            "second_name_ar": student_student12[0]['second_name_ar'],
                                            "third_name_ar": student_student12[0]['third_name_ar'],
                                            "last_name_ar": student_student12[0]['last_name_ar'],
                                            "display_name_ar": student_student12[0]['display_name_ar'],
                                            "moe_grace_period": student_student12[0]['moe_grace_period'],
                                            "deadline_date": student_student12[0]['deadline_date'],
                                            "neighborhood_id": student_student12[0]['neighborhood_id'],
                                            "assembly_id": student_student12[0]['assembly_id'],
                                            "ministry_state_id": student_student12[0]['ministry_state_id'],
                                            "student_emis_no": student_student12[0]['student_emis_no'],
                                            "family_members": student_student12[0]['family_members'],
                                            "borthers": student_student12[0]['borthers'],
                                            "sisters": student_student12[0]['sisters'],
                                            "soas": student_student12[0]['soas'],
                                            "marital_state": student_student12[0]['marital_state'],
                                            "education": student_student12[0]['education'],
                                            "external_financial_aid": student_student12[0]['external_financial_aid'],
                                            "aid_type": student_student12[0]['aid_type'],
                                            "international_refugee_card_status": student_student12[0][
                                                'international_refugee_card_status'],
                                            "district_id": student_student12[0]['district_id'],
                                            "province_id": student_student12[0]['province_id'],
                                            "partner_id": student_student12[0]['partner_id'],
                                            "book_requests": student_student12[0]['book_requests'],
                                            "country_of_birth": student_student12[0]['country_of_birth'],
                                            "city_of_birth": student_student12[0]['city_of_birth'],
                                            "file_name": student_student12[0]['file_name'],
                                            "pickup_by_parent": student_student12[0]['pickup_by_parent'],
                                            "dropoff_by_parent": student_student12[0]['dropoff_by_parent'],
                                            "area_ids": student_student12[0]['area_ids'],
                                            "round_type": student_student12[0]['round_type'],
                                            "contact_person": student_student12[0]['contact_person'],
                                            "family_relation": student_student12[0]['family_relation'],
                                            "contact_person_number": student_student12[0]['contact_person_number'],
                                            "round_address_type": student_student12[0]['round_address_type'],
                                            "pick_up_type": student_student12[0]['pick_up_type'],
                                            "drop_off_type": student_student12[0]['drop_off_type'],
                                            "second_pickup_address": student_student12[0]['second_pickup_address'],
                                            "second_dropoff_address": student_student12[0]['second_dropoff_address'],
                                            "dropoff_as_pickup": student_student12[0]['dropoff_as_pickup'],
                                            "same_as_address": student_student12[0]['same_as_address'],
                                            "pickup_building_number": student_student12[0]['pickup_building_number'],
                                            "pickup_building_name": student_student12[0]['pickup_building_name'],
                                            "pickup_street": student_student12[0]['pickup_street'],
                                            "pickup_flat_number": student_student12[0]['pickup_flat_number'],
                                            "pickup_area_id": student_student12[0]['pickup_area_id'],
                                            "pickup_state_id": student_student12[0]['pickup_state_id'],
                                            "pickup_address_note": student_student12[0]['pickup_address_note'],
                                            "sec_pickup_building_number": student_student12[0][
                                                'sec_pickup_building_number'],
                                            "sec_pickup_building_name": student_student12[0][
                                                'sec_pickup_building_name'],
                                            "sec_pickup_street": student_student12[0]['sec_pickup_street'],
                                            "sec_pickup_flat_number": student_student12[0]['sec_pickup_flat_number'],
                                            "sec_pickup_area_id": student_student12[0]['sec_pickup_area_id'],
                                            "sec_pickup_state_id": student_student12[0]['sec_pickup_state_id'],
                                            "sec_pickup_address_note": student_student12[0]['sec_pickup_address_note'],
                                            "dropoff_building_number": student_student12[0]['dropoff_building_number'],
                                            "dropoff_building_name": student_student12[0]['dropoff_building_name'],
                                            "dropoff_street": student_student12[0]['dropoff_street'],
                                            "dropoff_flat_number": student_student12[0]['dropoff_flat_number'],
                                            "dropoff_area_id": student_student12[0]['dropoff_area_id'],
                                            "dropoff_state_id": student_student12[0]['dropoff_state_id'],
                                            "dropoff_address_note": student_student12[0]['dropoff_address_note'],
                                            "sec_dropoff_building_number": student_student12[0][
                                                'sec_dropoff_building_number'],
                                            "sec_dropoff_building_name": student_student12[0][
                                                'sec_dropoff_building_name'],
                                            "sec_dropoff_street": student_student12[0]['sec_dropoff_street'],
                                            "sec_dropoff_flat_number": student_student12[0]['sec_dropoff_flat_number'],
                                            "sec_dropoff_area_id": student_student12[0]['sec_dropoff_area_id'],
                                            "sec_dropoff_state_id": student_student12[0]['sec_dropoff_state_id'],
                                            "sec_dropoff_address_note": student_student12[0][
                                                'sec_dropoff_address_note'],
                                            "is_suspended": student_student12[0]['is_suspended'],
                                            "sequence": student_student12[0]['sequence'],
                                            "password": student_student12[0]['password'],
                                            "image_url": 'https://trackware-schools.s3.eu-central-1.amazonaws.com/' +
                                                         student_student12[0]['image_url'] if student_student12[0][
                                                'image_url'] else student_student12[0]['image_url'],
                                            "round_id": student_student12[0]['round_id'],
                                            "responsible_id_value": student_student12[0]['responsible_id_value'],
                                            "grade": student_grade,
                                            # "first_mandatory": student_student[std][134],

                                            # "second_mandatory": student_student[std][135],
                                            # "third_mandatory": student_student[std][136],
                                            # "last_mandatory": student_student[std][137],
                                            "section_id_value": student_student12[0]['section_id_value'],
                                            # "grade":student_student[std][147],
                                            # "laravel_through_key": s[std]['laravel_through_key'],
                                            "parents_info": [
                                                {
                                                    "father": {
                                                        "mobile_token": father_inf[0][
                                                            'mobile_token'] if father_inf else "",
                                                        # "mobile_pn_registration_id": father_inf[0]['mobile_pn_registration_id']if father_inf else "",
                                                        # "invite_count": father_inf[0]['invite_count']if father_inf else "",
                                                        "settings": father_inf[0]['settings'] if father_inf else "",
                                                        "number": father_inf[0]['mobile'] if father_inf else "",
                                                        "id": father_inf[0]['id'] if father_inf else -1

                                                    },
                                                    "mother": {
                                                        "mobile_token": mother_inf[0][
                                                            'mobile_token'] if mother_inf else "",
                                                        # "mobile_pn_registration_id": mother_inf[0]['mobile_pn_registration_id']if mother_inf else"",
                                                        # "invite_count": mother_inf[0]['invite_count']if mother_inf else"",
                                                        "settings": mother_inf[0]['settings'] if mother_inf else "",
                                                        # {
                                                        #     "notifications": {
                                                        #         "locale": "ar",
                                                        #         "nearby": False,
                                                        #         "check_in": False,
                                                        #         "check_out": False
                                                        #     }
                                                        # },
                                                        "number": mother_inf[0]['mobile'] if mother_inf else "",
                                                        "id": mother_inf[0]['id'] if mother_inf else -1
                                                    }
                                                }
                                            ],
                                            "avatar": 'https://trackware-schools.s3.eu-central-1.amazonaws.com/' +student_student12[0]['image_url'] if student_student12[0][
                                                'image_url'] else "https://s3.eu-central-1.amazonaws.com/trackware.schools/public_images/default_student.png",
                                            "check_in": in_round,
                                            "check_out": out_round,
                                            "absent": abs,
                                            "lat": lat,
                                            "lng": long,
                                            "no_show": no_show,
                                        }


                                student = []

                                for std_inf in st_id:
                                    student.append(student_info[std_inf])
                                cursor.execute(
                                    "UPDATE public.transport_round SET total_checkedout_students= %s , total_checkedin_students= %s WHERE id=%s",
                                    [ch_out, ch_in, round_id])

                                result = {"students_list": student
                                          }

                                return Response(result)
                    if request.method == 'POST':
                        result = {"status": "error"
                                  }
                        return Response(result)
                    else:
                        result = {"status": "Token notFound"
                                  }
                        return Response(result)
                else:
                    result = {"status": "error"
                              }
                    return Response(result)
            result = {"status": "error"
                      }
            return Response(result)
        else:
            result = {"status": "error"
                      }

            return Response(result)


@api_view(['POST'])
def recent_notifications(request):
    if request.method == 'POST':
        if request.headers:
            if request.headers.get('Authorization'):
                if 'Bearer' in request.headers.get('Authorization'):
                    au = request.headers.get('Authorization').replace('Bearer', '').strip()
                    db_name = Manager.objects.filter(token=au).values_list('db_name')
                    driver_id = Manager.objects.filter(token=au).values_list('driver_id')
                    notifications = []
                    for e in driver_id:
                        driver_id = e[0]
                    if db_name:
                        for e in db_name:
                            school_name = e[0]
                            school_name = Manager.pincode(school_name)
                            day_count = request.data.get('day_count')
                            with connections[school_name].cursor() as cursor:
                                cursor.execute(
                                    "select  name from res_partner WHERE id = %s",
                                    [driver_id])
                                driver_name = cursor.fetchall()
                                cursor.execute(
                                    "select  id from transport_round WHERE driver_id = %s",
                                    [driver_id])
                                transport_round = cursor.fetchall()
                                transport_rounds = []
                                for rec in transport_round:
                                    transport_rounds.append(rec[0])
                                if transport_rounds:
                                    cursor.execute(
                                        "select  round_id from round_schedule WHERE round_id in %s AND day_id =%s ",
                                        [tuple(transport_rounds), day_count])
                                    round_schedule = cursor.fetchall()
                                    round_schedules = []
                                    for rec in round_schedule:
                                        round_schedules.append(rec[0])
                                    if round_schedules:
                                        cursor.execute(
                                            "select  message_ar,create_date,type from sh_message_wizard WHERE round_id in %s AND sender_name = %s AND from_type='App\Model\Driver' ",
                                            [tuple(round_schedules), driver_name[0][0]])
                                        sh_message_wizard = cursor.fetchall()
                                        for rec in range(len(sh_message_wizard)):
                                            notifications.append({
                                                "message": sh_message_wizard[rec][0],
                                                "date": sh_message_wizard[rec][1],
                                                "image": "https://s3.eu-central-1.amazonaws.com/notifications-images/mobile-notifications-icons/notification_icon_check_in_drop.png"
                                            })

                                        result = {"notifications": notifications}
                                        return Response(result)

                                    result = {"notifications": ""}
                                    return Response(result)

                                result = {"notifications": ""}
                                return Response(result)
                    else:
                        result = {'status': 'error'}
                        return Response(result)
                else:
                    result = {'status': 'error'}
                    return Response(result)
            else:
                result = {'status': 'error'}
                return Response(result)
        else:
            result = {'status': 'error'}
            return Response(result)

def save_message_wizard(school_name,round_id,date,from_type,message_title,message_title_ar,message_body,message_body_ar,driver_name):
    with connections[school_name].cursor() as cursor:
        cursor.execute(
            "INSERT INTO sh_message_wizard(round_id,create_date,from_type,type,message_en,message_ar,sender_name,type_ar)VALUES (%s,%s,%s,%s,%s,%s,%s,%s);",
            [round_id, date, from_type, message_title,
             message_body, message_body_ar,
             driver_name[0][0], message_title_ar])

@api_view(['POST'])
def set_round_status(request):
    if request.method == 'POST':
        if request.headers:
            if request.headers.get('Authorization'):
                if 'Bearer' in request.headers.get('Authorization'):
                    au = request.headers.get('Authorization').replace('Bearer', '').strip()
                    db_name = Manager.objects.filter(token=au).values_list('db_name')
                    driver_id = Manager.objects.filter(token=au).values_list('driver_id')
                    notifications = []
                    for e in driver_id:
                        driver_id = e[0]
                    if db_name:

                        for e in db_name:
                            school_name = e[0]
                            school_name = Manager.pincode(school_name)
                            with connections[school_name].cursor() as cursor:

                                round_id = request.data.get('round_id')
                                lat = request.data.get('lat')
                                long = request.data.get('long')
                                distance = request.data.get('distance')
                                status = request.data.get('status')
                                assistant_id = request.data.get('assistant_id')
                                cursor.execute(
                                    "select  name,vehicle_id,driver_id ,type from transport_round WHERE id = %s  ",
                                    [round_id])
                                round_info = cursor.fetchall()
                                curr_date = date.today()
                                cursor.execute(
                                    "select  id  from school_day where name = %s",
                                    [calendar.day_name[curr_date.weekday()]])
                                day_name = cursor.fetchall()
                                cursor.execute(
                                    "select id,day_id from round_schedule WHERE round_id = %s and day_id = %s",
                                    [round_id, day_name[0][0]])
                                columns3 = (x.name for x in cursor.description)
                                rounds_details = cursor.fetchall()
                                day_list = {}
                                cursor.execute(
                                    "select  write_date,type,id from transport_round WHERE id = %s  ",
                                    [round_id])
                                round_info1 = cursor.fetchall()

                                cursor.execute(
                                    "select student_id from transport_participant WHERE round_schedule_id = %s ORDER BY sequence ASC",
                                    [rounds_details[0][0]])
                                columns4 = (x.name for x in cursor.description)
                                rounds_count_student = cursor.fetchall()
                                cursor.execute(
                                    "select  name from res_partner WHERE id = %s",
                                    [driver_id])
                                driver_name = cursor.fetchall()
                                if status == 'start':

                                    # import datetime

                                    st_id = []
                                    for k in rounds_count_student:
                                        cursor.execute(
                                            "select  display_name_search,id from student_student WHERE id= %s",
                                            [k[0]])

                                        student_name = cursor.fetchall()
                                        cursor.execute(
                                            "select father_id,mother_id,responsible_id_value from student_student WHERE id = %s ",
                                            [k[0]])

                                        student_student2 = cursor.fetchall()

                                        for rec in student_student2[0]:
                                            # yousef ahmad 123
                                            lang="en"
                                            mobile_token1 = ManagerParent.objects.filter(Q(parent_id=rec), Q(db_name=school_name),
                                                            Q(is_active=True)).values_list('mobile_token').order_by('-pk')
                                            cursor.execute("select  settings from school_parent WHERE id = %s", [rec])
                                            settings = cursor.fetchall()
                                            if settings:

                                                if not ('None' in str(settings)):

                                                    data = json.loads(settings[0][0])
                                                    title = ''
                                                    message = ''

                                                    if type(data['notifications']) is dict:
                                                        if "ar" in data['notifications']['locale']:
                                                            lang = "ar"
                                                    else:
                                                        li = list(data['notifications'].split(","))
                                                        lang = "ar" if "ar" in li[3] else 'en'
                                                # print("assssssssssss",mobile_token1[0][0])
                                                # for e in mobile_token1:
                                                #     print(e[0])
                                                    # mobile_token.append(e[0])
                                                # if mobile_token1:
                                                #
                                                #     registration_id = mobile_token1[0][0]
                                                #     # message_title = "School Departure"
                                                #     message_title = "Pick-up round"
                                                #     message_title_ar = "الجولة الصباحية"
                                                #     # message_body = student_name[0][0] + "  has just been checked into the bus."
                                                #     message_body = "The pickup round is started, please have your children" + \
                                                #                    student_name[0][
                                                #                        0] + " ready."
                                                #
                                                #     message_body_ar = "بدأت الجولة الصباحية, الرجاء ان يكون " + \
                                                #                       student_name[0][0] + " مستعداً"
                                                #     date_string = datetime.datetime.now().strftime(
                                                #         "%Y-%m-%d %H:%M:%S")
                                                #     r = datetime.datetime.strptime(date_string,
                                                #                                    '%Y-%m-%d %H:%M:%S')
                                                #
                                                #     # if round_info1[0][1] == 'pick_up' :
                                                #     if round_info1[0][1] == 'pick_up':
                                                #         cursor.execute(
                                                #             "select  name,vehicle_id,driver_id from transport_round WHERE id = %s  ",
                                                #             [round_id])
                                                #         round_info22 = cursor.fetchall()
                                                #         cursor.execute(
                                                #             "select  id,round_start,round_end,na from round_history WHERE round_id = %s and driver_id=%s and vehicle_id = %s and round_name=%s ORDER BY ID DESC LIMIT 1 ",
                                                #             [round_id, round_info22[0][2], round_info22[0][1],
                                                #              round_id])
                                                #         round_history = cursor.fetchall()
                                                #
                                                #         start = datetime.datetime(datetime.datetime.now().year,
                                                #                                   datetime.datetime.now().month,
                                                #                                   datetime.datetime.now().day)
                                                #         if round_history:
                                                #
                                                #             now = datetime.date.today()
                                                #             if round_history[0][1].strftime('%Y-%m-%d') == str(now):
                                                #                 cursor.execute(
                                                #                     "select  activity_type,lat,long from student_history WHERE round_id = %s and student_id=%s and history_id = %s  ORDER BY ID DESC LIMIT 1 ",
                                                #                     [round_id, student_name[0][1], round_history[0][0]])
                                                #                 student_history = cursor.fetchall()
                                                #                 cursor.execute(
                                                #                     "select  activity_type,lat,long from student_history WHERE round_id = %s and student_id=%s and datetime >= %s and datetime <= %s   ORDER BY ID DESC LIMIT 1 ",
                                                #                     [round_id, student_name[0][1], start,
                                                #                      datetime.datetime.now()])
                                                #                 student_history1 = cursor.fetchall()
                                                #                 if student_history1:
                                                #                     if student_history1[0][0] == 'absent' or \
                                                #                             student_history1[0][0] == 'absent-all' or \
                                                #                             student_history1[0][0] == 'no-show':
                                                #                         continue
                                                #             else:
                                                #                 cursor.execute(
                                                #                     "select  activity_type,lat,long from student_history WHERE round_id = %s and student_id=%s and datetime >= %s and datetime <= %s   ORDER BY ID DESC LIMIT 1 ",
                                                #                     [round_id, student_name[0][1], start,
                                                #                      datetime.datetime.now()])
                                                #                 student_history1 = cursor.fetchall()
                                                #
                                                #                 if student_history1:
                                                #                     if student_history1[0][0] == 'absent' or \
                                                #                             student_history1[0][0] == 'absent-all' or \
                                                #                             student_history1[0][0] == 'no-show':
                                                #                         continue
                                                #
                                                #         cursor.execute(
                                                #             "INSERT INTO sh_message_wizard(round_id,create_date,from_type, type, message_en,message_ar,sender_name,type_ar)VALUES (%s,%s,%s,%s,%s,%s,%s,%s);",
                                                #             [round_id, r, 'App\Model\sta' + str(rec), message_title,
                                                #              message_body, message_body_ar,
                                                #              driver_name[0][0],message_title_ar])
                                                #         push_service = FCMNotification(
                                                #             api_key="AAAAzysR6fk:APA91bFX6siqzUm-MQdhOWlno2PCOMfFVFIHmcfzRwmStaQYnUUJfDZBkC2kd2_s-4pk0o5jxrK9RsNiQnm6h52pzxDbfLijhXowIvVL2ReK7Y0FdZAYzmRekWTtOwsyG4au7xlRz1zD")
                                                #
                                                #         if mobile_token1[0][0] and not ("token" in mobile_token1[0][0]):
                                                #             print("dddddddddddddddddd")
                                                #             notify_single_device = push_service.notify_single_device(
                                                #                 registration_id=registration_id[0],
                                                #                 message_title=message_title if lang=="en" else message_title_ar ,
                                                #                 message_body=message_body if lang=="en" else message_body_ar)
                                        mobile_token=[]
                                        for e in mobile_token1:
                                            mobile_token.append(e[0])

                                        registration_id = mobile_token
                                        # message_title = "School Departure"
                                        message_title = "Pick-up round"
                                        message_title_ar = "الجولة الصباحية"
                                        # message_body = student_name[0][0] + "  has just been checked into the bus."
                                        message_body = "The pickup round is started, please have your children " + \
                                                       student_name[0][
                                                           0] + " ready."

                                        message_body_ar =  "بدأت الجولة الصباحية, الرجاء ان يكون "+student_name[0][0]+" مستعداً"
                                        date_string = datetime.datetime.now().strftime(
                                            "%Y-%m-%d %H:%M:%S")
                                        r = datetime.datetime.strptime(date_string,
                                                                       '%Y-%m-%d %H:%M:%S')

                                        # if round_info1[0][1] == 'pick_up' :
                                        if round_info1[0][1]== 'pick_up' :
                                                cursor.execute(
                                                    "select  name,vehicle_id,driver_id from transport_round WHERE id = %s  ",
                                                    [round_id])
                                                round_info22 = cursor.fetchall()
                                                cursor.execute(
                                                    "select  id,round_start,round_end,na from round_history WHERE round_id = %s and driver_id=%s and vehicle_id = %s and round_name=%s ORDER BY ID DESC LIMIT 1 ",
                                                    [round_id, round_info22[0][2], round_info22[0][1],
                                                     round_id])
                                                round_history = cursor.fetchall()

                                                start = datetime.datetime(datetime.datetime.now().year,
                                                                          datetime.datetime.now().month,
                                                                      datetime.datetime.now().day)
                                                if round_history:

                                                    now = datetime.date.today()
                                                    if round_history[0][1].strftime('%Y-%m-%d') == str(now):
                                                        cursor.execute(
                                                            "select  activity_type,lat,long from student_history WHERE round_id = %s and student_id=%s and history_id = %s  ORDER BY ID DESC LIMIT 1 ",
                                                            [round_id, student_name[0][1], round_history[0][0]])
                                                        student_history = cursor.fetchall()
                                                        cursor.execute(
                                                            "select  activity_type,lat,long from student_history WHERE round_id = %s and student_id=%s and datetime >= %s and datetime <= %s   ORDER BY ID DESC LIMIT 1 ",
                                                            [round_id,  student_name[0][1], start,
                                                             datetime.datetime.now()])
                                                        student_history1 = cursor.fetchall()
                                                        if student_history1:
                                                            if student_history1[0][0] == 'absent' or student_history1[0][0] == 'absent-all' or student_history1[0][0] ==  'no-show':
                                                                continue
                                                    else:
                                                        cursor.execute(
                                                            "select  activity_type,lat,long from student_history WHERE round_id = %s and student_id=%s and datetime >= %s and datetime <= %s   ORDER BY ID DESC LIMIT 1 ",
                                                            [round_id, student_name[0][1], start,
                                                             datetime.datetime.now()])
                                                        student_history1 = cursor.fetchall()

                                                        if student_history1:
                                                            if student_history1[0][0] == 'absent' or \
                                                                    student_history1[0][0] == 'absent-all' or \
                                                                    student_history1[0][0] == 'no-show':
                                                                continue



                                                # cursor.execute(
                                                #     "INSERT INTO sh_message_wizard(round_id,create_date,from_type,type,message_en,message_ar,sender_name,type_ar)VALUES (%s,%s,%s,%s,%s,%s,%s,%s);",
                                                #     [round_id, r, 'App\Model\sta' + str(rec), message_title,
                                                #      message_body, message_body_ar,
                                                #      driver_name[0][0],message_title_ar])
                                                save_message_wizard(school_name, round_id, r, 'App\Model\sta' + str(rec),
                                                                    message_title, message_title_ar, message_body,
                                                                    message_body_ar, driver_name[0][0])
                                                push_service = FCMNotification(api_key="AAAAzysR6fk:APA91bFX6siqzUm-MQdhOWlno2PCOMfFVFIHmcfzRwmStaQYnUUJfDZBkC2kd2_s-4pk0o5jxrK9RsNiQnm6h52pzxDbfLijhXowIvVL2ReK7Y0FdZAYzmRekWTtOwsyG4au7xlRz1zD")

                                                if mobile_token and not("token" in mobile_token):
                                                    notify_single_device = push_service.notify_single_device(
                                                        registration_id=registration_id[0],
                                                        message_title=message_title if lang =="en" else message_title_ar,
                                                        message_body=message_body if lang =="en" else message_body_ar)

                                    cursor.execute(
                                        "select  round_start,id from round_history WHERE round_id = %s and driver_id=%s and vehicle_id = %s and round_name=%s ORDER BY ID DESC LIMIT 1 ",
                                        [round_id, round_info[0][2], round_info[0][1], round_id])
                                    round_history = cursor.fetchall()
                                    if round_history:
                                        now = datetime.date.today()
                                        if round_history[0][0].strftime('%Y-%m-%d') == str(now):
                                            cursor.execute(
                                                "UPDATE public.round_history SET na= %s WHERE id=%s",
                                                ['cancel', round_history[0][1]])
                                        else:
                                            curr_date = date.today()
                                            day_name = calendar.day_name[curr_date.weekday()]
                                            cursor.execute(
                                                "select  id  from school_day where name = %s",
                                                [calendar.day_name[curr_date.weekday()]])
                                            day_name = cursor.fetchall()
                                            cursor.execute(
                                                "select id,day_id from round_schedule WHERE round_id = %s and day_id = %s",
                                                [round_id, day_name[0][0]])
                                            columns3 = (x.name for x in cursor.description)
                                            rounds_details = cursor.fetchall()
                                            day_list = {}
                                            # for z in rounds_details:
                                            cursor.execute(
                                                "select student_id from transport_participant WHERE round_schedule_id = %s",
                                                [rounds_details[0][0]])
                                            columns4 = (x.name for x in cursor.description)
                                            rounds_count_student = cursor.fetchall()
                                            ch_in = 0
                                            ch_out = 0
                                            if round_info[0][3] == 'pick_up':
                                                ch_in = len(rounds_count_student)
                                            else:
                                                ch_out = len(rounds_count_student)

                                            cursor.execute(
                                                "UPDATE public.transport_round SET total_checkedout_students= %s , total_checkedin_students= %s WHERE id=%s",
                                                [ch_out, ch_in, round_id])
                                            stds = []
                                            for rec in rounds_count_student:
                                                stds.append(rec[0])

                                            cursor.execute(
                                                "UPDATE public.transport_participant SET transport_state = %s,write_date=%s WHERE student_id in %s AND round_schedule_id= %s",
                                                ["",datetime.datetime.now(), tuple(stds), rounds_details[0][0]])

                                            cursor.execute(
                                                "INSERT INTO  round_history (round_name,round_id,distance,vehicle_id,driver_id,round_start,attendant_id) VALUES (%s,%s,%s,%s,%s,%s,%s); ",
                                                [round_id, round_id, distance, round_info[0][1], round_info[0][2],
                                                 datetime.datetime.now(), assistant_id])
                                    else:
                                        cursor.execute(
                                            "INSERT INTO  round_history (round_name,round_id,distance,vehicle_id,driver_id,round_start,attendant_id) VALUES (%s,%s,%s,%s,%s,%s,%s); ",
                                            [round_id, round_id, distance, round_info[0][1], round_info[0][2],
                                             datetime.datetime.now(), assistant_id])
                                elif status == 'end' or status == 'force_end':
                                    st_id = []

                                    for k in rounds_count_student:
                                        cursor.execute(
                                            "select  display_name_search from student_student WHERE id= %s",
                                            [k[0]])

                                        student_name = cursor.fetchall()
                                        cursor.execute(
                                            "select father_id,mother_id,responsible_id_value from student_student WHERE id = %s ",
                                            [k[0]])
                                        columns4 = (x.name for x in cursor.description)
                                        student_student2 = cursor.fetchall()
                                        for rec in student_student2[0]:
                                            lang ="en"
                                            cursor.execute("select  settings from school_parent WHERE id = %s", [rec])
                                            settings = cursor.fetchall()
                                            if settings:

                                                if not ('None' in str(settings)):

                                                    data = json.loads(settings[0][0])

                                                    if type(data['notifications']) is dict:
                                                        if "ar" in data['notifications']['locale']:
                                                            lang = "ar"
                                                    else:
                                                        li = list(data['notifications'].split(","))
                                                        lang = "ar" if "ar" in li[3] else 'en'
                                            mobile_token1 = ManagerParent.objects.filter(Q(parent_id=rec),
                                                                                         Q(db_name=school_name),
                                                                                         Q(is_active=True)).values_list(
                                                'mobile_token').order_by('-pk')
                                            # cursor.execute(
                                            #     "select  id,round_start from round_history WHERE round_id = %s and driver_id=%s and vehicle_id = %s and round_name=%s ORDER BY ID DESC LIMIT 1 ",
                                            #     [round_id, round_info[0][2], round_info[0][1], round_id])
                                            # round_history = cursor.fetchall()
                                            # if round_history:
                                            #     now = datetime.date.today()
                                            #     if round_history[0][1].strftime('%Y-%m-%d') == str(now):
                                            #         cursor.execute(
                                            #             "select  datetime,id,time_out,bus_check_in from round_student_history WHERE round_id = %s and student_id=%s and history_id = %s  ORDER BY ID DESC LIMIT 1 ",
                                            #             [round_id, k[0], round_history[0][0]])
                                            #         student_history = cursor.fetchall()
                                            #         if student_history:
                                            #             if round_info[0][3] == 'pick_up':
                                            #                 if student_history[0][3]:
                                            #                     cursor.execute(
                                            #                         "UPDATE public.round_student_history SET time_out = %s WHERE id =%s ",
                                            #                         [datetime.datetime.now(), student_history[0][1]])
                                            #                     push_service = FCMNotification(
                                            #                         api_key="AAAAzysR6fk:APA91bFX6siqzUm-MQdhOWlno2PCOMfFVFIHmcfzRwmStaQYnUUJfDZBkC2kd2_s-4pk0o5jxrK9RsNiQnm6h52pzxDbfLijhXowIvVL2ReK7Y0FdZAYzmRekWTtOwsyG4au7xlRz1zD")
                                            #                     registration_id = mobile_token1[0][0]
                                            #                     message_title = " Bus Notification"
                                            #                     message_title_ar = 'اشعار من الحافلة'
                                            #                     message_body_ar = " وصل إلى المدرسة." + student_name[0][
                                            #                         0]
                                            #
                                            #                     message_body = student_name[0][
                                            #                                        0] + "  has just reached the school."
                                            #                     if mobile_token1[0][0]and not ("token" in mobile_token1[0][0]):
                                            #                         notify_single_device = push_service.notify_single_device(
                                            #                             registration_id=registration_id[0],
                                            #                             message_title=message_title if lang=="en" else message_title_ar,
                                            #                             message_body=message_body if lang=="en" else message_body_ar )
                                            #             else:
                                            #                 if student_history[0][2]:
                                            #                     cursor.execute(
                                            #                         "UPDATE public.round_student_history SET bus_check_in = %s WHERE id =%s ",
                                            #                         [datetime.datetime.now(), student_history[0][1]])
                                        mobile_token = []
                                        for e in mobile_token1:
                                            mobile_token.append(e[0])
                                        # if round_info[0][3] == 'pick_up':
                                            # push_service = FCMNotification(
                                            #     api_key="AAAAzysR6fk:APA91bFX6siqzUm-MQdhOWlno2PCOMfFVFIHmcfzRwmStaQYnUUJfDZBkC2kd2_s-4pk0o5jxrK9RsNiQnm6h52pzxDbfLijhXowIvVL2ReK7Y0FdZAYzmRekWTtOwsyG4au7xlRz1zD")
                                            # registration_id = mobile_token
                                            # message_title = " Bus Notification"
                                            #
                                            # message_body = student_name[0][0] + "  has just reached the school."
                                            # if mobile_token and not ("token" in mobile_token):
                                            #     notify_single_device = push_service.notify_single_device(
                                            #         registration_id=registration_id[0],
                                            #         message_title=message_title,
                                            #         message_body=message_body)
                                    # for k in rounds_count_student:
                                        cursor.execute(
                                            "select  id,round_start from round_history WHERE round_id = %s and driver_id=%s and vehicle_id = %s and round_name=%s ORDER BY ID DESC LIMIT 1 ",
                                            [round_id, round_info[0][2], round_info[0][1], round_id])
                                        round_history = cursor.fetchall()
                                        if round_history:
                                            now = datetime.date.today()
                                            if round_history[0][1].strftime('%Y-%m-%d') == str(now):
                                                cursor.execute(
                                                    "select  datetime,id,time_out,bus_check_in from round_student_history WHERE round_id = %s and student_id=%s and history_id = %s  ORDER BY ID DESC LIMIT 1 ",
                                                    [round_id, k[0], round_history[0][0]])
                                                student_history = cursor.fetchall()
                                                if student_history:
                                                    if  round_info[0][3] == 'pick_up':
                                                        if student_history[0][3]:
                                                            cursor.execute(
                                                                "UPDATE public.round_student_history SET time_out = %s WHERE id =%s ",
                                                                [datetime.datetime.now(), student_history[0][1]])
                                                            push_service = FCMNotification(
                                                                api_key="AAAAzysR6fk:APA91bFX6siqzUm-MQdhOWlno2PCOMfFVFIHmcfzRwmStaQYnUUJfDZBkC2kd2_s-4pk0o5jxrK9RsNiQnm6h52pzxDbfLijhXowIvVL2ReK7Y0FdZAYzmRekWTtOwsyG4au7xlRz1zD")
                                                            registration_id = mobile_token
                                                            message_title = " Bus Notification"
                                                            message_title_ar = 'اشعار من الحافلة'
                                                            message_body_ar = " وصل إلى المدرسة." + student_name[0][0]

                                                            message_body = student_name[0][
                                                                               0] + "  has just reached the school."
                                                            if mobile_token and not ("token" in mobile_token):
                                                                notify_single_device = push_service.notify_single_device(
                                                                    registration_id=registration_id[0],
                                                                    message_title=message_title if lang=='en' else message_title_ar,
                                                                    message_body=message_body if lang=='en' else message_body_ar)
                                                    else:
                                                        if student_history[0][2]:
                                                            cursor.execute(
                                                                "UPDATE public.round_student_history SET bus_check_in = %s WHERE id =%s ",
                                                                [datetime.datetime.now(),student_history[0][1]])

                                    cursor.execute(
                                        "select  round_start,id from round_history WHERE round_id = %s and driver_id=%s and vehicle_id = %s and round_name=%s ORDER BY ID DESC LIMIT 1 ",
                                        [round_id, round_info[0][2], round_info[0][1], round_id])
                                    round_history = cursor.fetchall()
                                    if round_history:
                                        now = datetime.date.today()
                                        if round_history[0][0].strftime('%Y-%m-%d') == str(now):
                                            cursor.execute(
                                                "UPDATE public.round_history SET round_end= %s,na= %s WHERE id=%s",
                                                [datetime.datetime.now(),'end', round_history[0][1]])
                                elif status == 'cancel':

                                    cursor.execute(
                                        "select  round_start,id from round_history WHERE round_id = %s and driver_id=%s and vehicle_id = %s and round_name=%s ORDER BY ID DESC LIMIT 1 ",
                                        [round_id, round_info[0][2], round_info[0][1], round_id])
                                    round_history = cursor.fetchall()
                                    if round_history:
                                        now = datetime.date.today()
                                        if round_history[0][0].strftime('%Y-%m-%d') == str(now):
                                            cursor.execute(
                                                "UPDATE public.round_history SET na= %s WHERE id=%s",
                                                ['cancel', round_history[0][1]])
                                cursor.execute(
                                    "UPDATE public.transport_round SET is_active= not(is_active), pick_up_lat=%s ,pick_up_lng=%s ,drop_off_lat=%s ,drop_off_lng=%s,write_date=%s WHERE id=%s",
                                    [lat, long, lat, long,datetime.datetime.now(), round_id])
                                result = {'status': 'OK'}
                                return Response(result)
                    else:
                        result = {'status': 'error'}
                        return Response(result)
                else:
                    result = {'status': 'error'}
                    return Response(result)
            else:
                result = {'status': 'error'}
                return Response(result)
        else:
            result = {'status': 'error'}
            return Response(result)


@api_view(['POST'])
def students_bus_checks(request):

    if request.method == 'POST':
        if request.headers:
            if request.headers.get('Authorization'):
                if 'Bearer' in request.headers.get('Authorization'):
                    au = request.headers.get('Authorization').replace('Bearer', '').strip()
                    db_name = Manager.objects.filter(token=au).values_list('db_name')
                    driver_id = Manager.objects.filter(token=au).values_list('driver_id')
                    if db_name:
                        for e in db_name:

                            school_name = e[0]
                            school_name = Manager.pincode(school_name)
                            with connections[school_name].cursor() as cursor:

                                students = request.data.get('students')

                                for rec in students:


                                    round_id = rec['round_id']
                                    status = rec['status']
                                    # day_count = rec['day_count']
                                    lat = rec['lat']
                                    long = rec['long']
                                    student_id = rec['student_id']
                                    if "waiting_minutes" in rec:
                                        waiting_minutes = rec['waiting_minutes']
                                    else:
                                        waiting_minutes=""
                                    curr_date = date.today()
                                    cursor.execute(
                                        "select  name,vehicle_id,driver_id,type,total_checkedout_students,total_checkedin_students from transport_round WHERE id = %s  ",
                                        [round_id])
                                    round_info = cursor.fetchall()
                                    cursor.execute(
                                        "select  id,round_start from round_history WHERE round_id = %s and driver_id=%s and vehicle_id = %s and round_name=%s ORDER BY ID DESC LIMIT 1 ",
                                        [round_id, round_info[0][2], round_info[0][1], round_id])
                                    round_history = cursor.fetchall()
                                    if round_history:
                                        now = datetime.date.today()
                                        if round_history[0][1].strftime('%Y-%m-%d') == str(now):
                                            cursor.execute(
                                                "select  datetime,id from round_student_history WHERE round_id = %s and student_id=%s and history_id = %s  ORDER BY ID DESC LIMIT 1 ",
                                                [round_id, student_id, round_history[0][0]])
                                            student_history = cursor.fetchall()
                                            if student_history:
                                                cursor.execute(
                                                    "INSERT INTO  student_history (round_id,student_id,bus_check_in,datetime,history_id,lat,long,activity_type) VALUES (%s,%s,%s,%s,%s,%s,%s,%s); ",
                                                    [round_id, student_id, datetime.datetime.now(),
                                                     datetime.datetime.now(), round_history[0][0], lat, long, status])
                                                if status == 'in':

                                                    cursor.execute(
                                                        "UPDATE public.round_student_history SET bus_check_in = %s WHERE id =%s ",
                                                        [datetime.datetime.now(), student_history[0][1]])
                                                    if round_info[0][3] == 'pick_up':
                                                        ch_in = round_info[0][5] + 1
                                                        ch_out = round_info[0][4] - 1
                                                    else:
                                                        ch_in = round_info[0][5] - 1
                                                        ch_out = round_info[0][4] + 1

                                                    cursor.execute(
                                                        "UPDATE public.transport_round SET total_checkedout_students= %s , total_checkedin_students= %s WHERE id=%s",
                                                        [ch_out, ch_in, round_id])

                                                elif status == 'out':
                                                    cursor.execute(
                                                        "UPDATE public.round_student_history SET time_out = %s WHERE id =%s ",
                                                        [datetime.datetime.now(), student_history[0][1]])
                                                    if round_info[0][3] == 'pick_up':
                                                        ch_in = round_info[0][5] + 1
                                                        ch_out = round_info[0][4] - 1
                                                    else:
                                                        ch_in = round_info[0][5] - 1
                                                        ch_out = round_info[0][4] + 1

                                                    cursor.execute(
                                                        "UPDATE public.transport_round SET total_checkedout_students= %s , total_checkedin_students= %s WHERE id=%s",
                                                        [ch_out, ch_in, round_id])

                                            else:

                                                if round_info[0][3] == 'pick_up':
                                                    ch_in = round_info[0][5] + 1
                                                    ch_out = round_info[0][4] - 1
                                                else:
                                                    ch_in = round_info[0][5] - 1
                                                    ch_out = round_info[0][4] + 1

                                                cursor.execute(
                                                    "UPDATE public.transport_round SET total_checkedout_students= %s , total_checkedin_students= %s WHERE id=%s",
                                                    [ch_out, ch_in, round_id])

                                                if status =='out' or status =='in':


                                                    cursor.execute(
                                                        "INSERT INTO  round_student_history (round_id,student_id,driver_waiting,bus_check_in,datetime,history_id) VALUES (%s,%s,%s,%s,%s,%s); ",
                                                        [round_id, student_id, waiting_minutes, datetime.datetime.now(),
                                                         datetime.datetime.now(), round_history[0][0]])
                                                else:
                                                    cursor.execute(
                                                        "INSERT INTO  round_student_history (round_id,student_id,history_id,driver_waiting,datetime) VALUES (%s,%s,%s,%s,%s); ",
                                                        [round_id, student_id, round_history[0][0],waiting_minutes,datetime.datetime.now()])

                                                cursor.execute(
                                                    "INSERT INTO  student_history (round_id,student_id,bus_check_in,datetime,history_id,lat,long,activity_type) VALUES (%s,%s,%s,%s,%s,%s,%s,%s); ",
                                                    [round_id, student_id, datetime.datetime.now(),
                                                     datetime.datetime.now(), round_history[0][0], lat, long, status])

                                    cursor.execute(
                                        "select  id  from school_day where name = %s",
                                        [calendar.day_name[curr_date.weekday()]])
                                    day_id = cursor.fetchall()
                                    cursor.execute(
                                        "select  id from round_schedule WHERE round_id = %s AND day_id =%s ",
                                        [round_id, day_id[0][0]])
                                    round_schedule = cursor.fetchall()
                                    if status!='near':
                                        cursor.execute(
                                            "UPDATE public.transport_participant SET transport_state = %s WHERE student_id =%s AND round_schedule_id= %s",
                                            [status, student_id, round_schedule[0][0]])

                                    cursor.execute(
                                        "select  father_id,mother_id,responsible_id_value from student_student WHERE id= %s",
                                        [student_id])
                                    student_info = cursor.fetchall()
                                    cursor.execute(
                                        "select  display_name_search from student_student WHERE id= %s",
                                        [student_id])
                                    student_name = cursor.fetchall()

                                    if type(driver_id) is not int:
                                        for e in driver_id:
                                            driver_id = e[0]
                                    cursor.execute(
                                        "select  bus_no  from fleet_vehicle WHERE driver_id = %s  ",
                                        [driver_id])
                                    bus_num = cursor.fetchall()
                                    cursor.execute(
                                        "select name from res_partner WHERE id = %s  ",
                                        [driver_id])
                                    driver_name = cursor.fetchall()
                                    mobile_token = []
                                    id=[]
                                    if student_info:
                                        if student_info[0][0]:
                                            id.append(student_info[0][0])
                                        if student_info[0][1]:
                                            id.append(student_info[0][1])
                                        if student_info[0][2]:
                                            id.append(student_info[0][2])
                                        id = list(dict.fromkeys(id))
                                        for rec in id:
                                            cursor.execute("select  settings from school_parent WHERE id = %s", [rec])
                                            settings = cursor.fetchall()


                                            mobile_token1 = ManagerParent.objects.filter(Q(parent_id=rec),
                                                                                         Q(db_name=school_name),
                                                                                         Q(is_active=True)).values_list( 'mobile_token').order_by('-pk')

                                            if settings:

                                                if not('None' in str(settings)) :

                                                    data = json.loads(settings[0][0])
                                                    # if data['notifications']['check_in']:
                                                    lang ="en"
                                                    title=''
                                                    message=''
                                                    title_ar = ''
                                                    message_ar = ''
                                                    if type(data['notifications']) is dict:
                                                        if "ar" in data['notifications']['locale']:
                                                            lang = "ar"

                                                        for e in mobile_token1:

                                                            if status == 'in' or status == 'near':
                                                                if data['notifications']['check_in']:
                                                                    mobile_token.append(e[0])
                                                                title = 'Bus notification'
                                                                title_ar = "اشعار من الحافلة"
                                                                if round_info[0][3] != 'pick_up':
                                                                    title = "School Departure"

                                                                message_ar = "صعد إلى الحافلة" + student_name[0][
                                                                    0] + str(bus_num[
                                                                                 0][0])
                                                                message = student_name[0][
                                                                              0] + ' has just been checked into the bus'
                                                                date_string = datetime.datetime.now().strftime(
                                                                    "%Y-%m-%d %H:%M:%S")
                                                                r = datetime.datetime.strptime(date_string,
                                                                                               '%Y-%m-%d %H:%M:%S')

                                                                # if round_info[0][3]=='pick_up':
                                                                #
                                                                # cursor.execute(
                                                                #     "INSERT INTO sh_message_wizard(round_id,create_date,from_type,type,message_en,message_ar,sender_name,type_ar)VALUES (%s,%s,%s,%s,%s,%s,%s,%s);",
                                                                #     [round_id, r, 'App\Model\sta'+str(rec), title,
                                                                #      message, message_ar,
                                                                #      driver_name[0][0],title_ar])
                                                                save_message_wizard(school_name, round_id, r,
                                                                                    'App\Model\sta'+str(rec),
                                                                                    title, title_ar,
                                                                                    message,
                                                                                    message_ar, driver_name[0][0])


                                                            elif  status == 'out':
                                                                date_string = datetime.datetime.now().strftime(
                                                                    "%Y-%m-%d %H:%M:%S")
                                                                r = datetime.datetime.strptime(date_string,
                                                                                               '%Y-%m-%d %H:%M:%S')
                                                                if data['notifications']['check_out']:
                                                                    mobile_token.append(e[0])
                                                                title = 'Checkout Notification'
                                                                title_ar='اشعار من الحافلة'
                                                                message_ar='وصل إلى المنزل.' + student_name[0][
                                                                              0]
                                                                message = 'The bus ' +str( bus_num[
                                                                    0]) + ' has arrived at your home and ' + \
                                                                          student_name[0][
                                                                              0] + ' has been checked out of the bus. '
                                                                # cursor.execute(
                                                                #     "INSERT INTO sh_message_wizard(round_id,create_date,from_type,type,message_en,message_ar,sender_name,type_ar)VALUES (%s,%s,%s,%s,%s,%s,%s,%s);",
                                                                #     [round_id, r, 'App\Model\sta'+str(rec),
                                                                #      title,
                                                                #      message, message_ar,
                                                                #      driver_name[0][0],title_ar])
                                                                save_message_wizard(school_name, round_id, r,
                                                                                    'App\Model\sta' + str(rec),
                                                                                    title, title_ar,
                                                                                    message,
                                                                                    message_ar, driver_name[0][0])

                                                            else:
                                                                date_string = datetime.datetime.now().strftime(
                                                                    "%Y-%m-%d %H:%M:%S")
                                                                r = datetime.datetime.strptime(date_string,
                                                                                               '%Y-%m-%d %H:%M:%S')
                                                                if status == 'no-show':
                                                                    mobile_token.append(e[0])
                                                                    title_ar = ' إشعار الغياب'
                                                                    title = ' No Show Notification'
                                                                    message_ar="لم يظهر اليوم."+student_name[0][ 0]
                                                                    message = student_name[0][
                                                                                  0] + ' did not check into the bus today'
                                                                    # cursor.execute(
                                                                    #     "INSERT INTO sh_message_wizard(round_id,create_date,from_type,type,message_en,message_ar,sender_name,type_ar)VALUES (%s,%s,%s,%s,%s,%s,%s,%s);",
                                                                    #     [round_id, r, 'App\Model\sta'+str(rec),
                                                                    #      title,
                                                                    #      message, message_ar,
                                                                    #      driver_name[0][0],title_ar])
                                                                    save_message_wizard(school_name, round_id, r,
                                                                                        'App\Model\sta' + str(rec),
                                                                                        title, title_ar,
                                                                                        message,
                                                                                        message_ar, driver_name[0][0])

                                                                elif status == 'absent':

                                                                    mobile_token.append(e[0])
                                                                    title = 'Absence notification'
                                                                    title_ar = 'اشعار من الحافلة'
                                                                    message_ar="غائب اليوم." +student_name[0][0]
                                                                    message = ' Your child ' + student_name[0][
                                                                        0] + ' has not checked into the bus and is absent today.'
                                                                    date_string = datetime.datetime.now().strftime(
                                                                        "%Y-%m-%d %H:%M:%S")
                                                                    r = datetime.datetime.strptime(date_string,
                                                                                                   '%Y-%m-%d %H:%M:%S')
                                                                    # cursor.execute(
                                                                    #     "INSERT INTO sh_message_wizard(round_id,create_date,from_type,type,message_en,message_ar,sender_name,type_ar)VALUES (%s,%s,%s,%s,%s,%s,%s,%s);",
                                                                    #     [round_id, r, 'App\Model\sta'+str(rec),
                                                                    #      title,
                                                                    #      message, message_ar,
                                                                    #      driver_name[0][0],title_ar])
                                                                    save_message_wizard(school_name, round_id, r,
                                                                                        'App\Model\sta' + str(rec),
                                                                                        title, title_ar,
                                                                                        message,
                                                                                        message_ar, driver_name[0][0])
                                                                elif status == 'near':
                                                                    date_string = datetime.datetime.now().strftime(
                                                                        "%Y-%m-%d %H:%M:%S")
                                                                    r = datetime.datetime.strptime(date_string,
                                                                                                   '%Y-%m-%d %H:%M:%S')
                                                                    if round_info[0][3] == 'pick_up':
                                                                        title_ar="الباص قريب منك"
                                                                        title = 'The bus is near you.'
                                                                        message =' You are next on the route. Please have '+student_name[0][
                                                                            0]+' ready to leave'
                                                                        message_ar="انت التالي, الحافلة اقتربت منك, الرجاء ان يكون"+student_name[0][
                                                                            0]+"مستعداً"
                                                                    else:
                                                                            title_ar = "الباص قريب منك"
                                                                            title = 'The bus is near you.'
                                                                            message = ' You are next on the route. ' + student_name[0][ 0] + ' is about to arrive.'
                                                                            message_ar = " علو وصول إلى المنزل " +student_name[0][0]



                                                    else:



                                                       notifications = list(data['notifications'].split(" "))
                                                       li = list(data['notifications'].split(","))
                                                       lang = "ar" if "ar" in li[3] else 'en'
                                                       date_string = datetime.datetime.now().strftime(
                                                           "%Y-%m-%d %H:%M:%S")
                                                       r = datetime.datetime.strptime(date_string,
                                                                                      '%Y-%m-%d %H:%M:%S')

                                                       for e in mobile_token1:

                                                           if  status == 'in' or status == 'near':

                                                               print(notifications[3])
                                                               # if 'true'in notifications[3] or notifications[3]=="true," :
                                                               mobile_token.append(e[0])
                                                               title = 'Bus notification'
                                                               title_ar = "اشعار من الحافلة"
                                                               if round_info[0][3] != 'pick_up':
                                                                   title = "School Departure"

                                                               message_ar = "صعد إلى الحافلة" + student_name[0][
                                                                   0] + str(bus_num[
                                                                                0][0])
                                                               message = student_name[0][
                                                                             0] + ' has just been checked into the bus'
                                                               date_string = datetime.datetime.now().strftime(
                                                                   "%Y-%m-%d %H:%M:%S")
                                                               r = datetime.datetime.strptime(date_string,
                                                                                              '%Y-%m-%d %H:%M:%S')
                                                               # if round_info[0][3]=="pick_up":
                                                               # cursor.execute(
                                                               #     "INSERT INTO sh_message_wizard(round_id,create_date,from_type,type,message_en,message_ar,sender_name,type_ar)VALUES (%s,%s,%s,%s,%s,%s,%s,%s);",
                                                               #     [round_id, r, 'App\Model\sta'+str(rec), title,
                                                               #      message, message_ar,
                                                               #      driver_name[0][0],title_ar])
                                                               save_message_wizard(school_name, round_id, r,
                                                                                   'App\Model\sta' + str(rec),
                                                                                   title, title_ar,
                                                                                   message,
                                                                                   message_ar, driver_name[0][0])


                                                           elif  status == 'out':

                                                               if notifications[5]=="true," :

                                                                 mobile_token.append(e[0])
                                                               title = 'Checkout Notification'
                                                               title_ar = 'اشعار من الحافلة'
                                                               message_ar = 'وصل إلى المنزل.' + student_name[0][0]
                                                               message = 'The bus ' + str(bus_num[
                                                                   0][0]) + 'has arrived at your home and ' + \
                                                                         student_name[0][
                                                                             0] + ' has been checked out of the bus. '

                                                               # cursor.execute(
                                                               #     "INSERT INTO sh_message_wizard(round_id,create_date,from_type,type,message_en,message_ar,sender_name,type_ar)VALUES (%s,%s,%s,%s,%s,%s,%s,%s);",
                                                               #     [round_id, r, 'App\Model\sta'+str(rec),
                                                               #      title,
                                                               #      message, message_ar,
                                                               #      driver_name[0][0],title_ar])
                                                               save_message_wizard(school_name, round_id, r,
                                                                                   'App\Model\sta' + str(rec),
                                                                                   title, title_ar,
                                                                                   message,
                                                                                   message_ar, driver_name[0][0])
                                                           else:


                                                               if status == 'no-show':
                                                                   mobile_token.append(e[0])
                                                                   title = ' No Show Notification'
                                                                   title_ar = ' إشعار الغياب'
                                                                   message_ar = "لم يظهر اليوم." + student_name[0][0]
                                                                   message = student_name[0][
                                                                                 0] + ' did not check into the bus today'
                                                                   # cursor.execute(
                                                                   #     "INSERT INTO sh_message_wizard(round_id,create_date,from_type,type,message_en,message_ar,sender_name,type_ar)VALUES (%s,%s,%s,%s,%s,%s,%s,%s);",
                                                                   #     [round_id, r, 'App\Model\sta'+str(rec),
                                                                   #      title,
                                                                   #      message, message_ar,
                                                                   #      driver_name[0][0],title_ar])
                                                                   save_message_wizard(school_name, round_id, r,
                                                                                       'App\Model\sta' + str(rec),
                                                                                       title, title_ar,
                                                                                       message,
                                                                                       message_ar, driver_name[0][0])
                                                               # yousef aa
                                                               elif status == 'absent':

                                                                   mobile_token.append(e[0])
                                                                   title = 'Absence notification'
                                                                   title_ar = 'اشعار من الحافلة'
                                                                   message_ar = "غائب اليوم." + student_name[0][0]
                                                                   message = ' Your child ' + student_name[0][
                                                                       0] + ' has not checked into the bus and is absent today.'
                                                                   date_string = datetime.datetime.now().strftime(
                                                                       "%Y-%m-%d %H:%M:%S")
                                                                   r = datetime.datetime.strptime(date_string,
                                                                                                  '%Y-%m-%d %H:%M:%S')
                                                                   # cursor.execute(
                                                                   #     "INSERT INTO sh_message_wizard(round_id,create_date,from_type,type,message_en,message_ar,sender_name,type_ar)VALUES (%s,%s,%s,%s,%s,%s,%s,%s);",
                                                                   #     [round_id, r, 'App\Model\sta'+str(rec),
                                                                   #      'Absence notification',
                                                                   #      message, message_ar,
                                                                   #      driver_name[0][0],title_ar])
                                                                   save_message_wizard(school_name, round_id, r,
                                                                                       'App\Model\sta' + str(rec),
                                                                                       'Absence notification', title_ar,
                                                                                       message,
                                                                                       message_ar, driver_name[0][0])
                                                               elif status == 'out':
                                                                   title = 'Checkout Notification'
                                                                   title_ar = 'اشعار من الحافلة'
                                                                   message_ar = 'وصل إلى المنزل.' + student_name[0][0]
                                                                   message = 'The bus ' + str(bus_num[
                                                                       0][0]) + 'has arrived at your home and ' + \
                                                                             student_name[0][
                                                                                 0] + ' has been checked out of the bus. '

                                                                   # cursor.execute(
                                                                   #     "INSERT INTO sh_message_wizard(round_id,create_date,from_type,type,message_en,message_ar,sender_name,type_ar)VALUES (%s,%s,%s,%s,%s,%s,%s,%s);",
                                                                   #     [round_id, r, 'App\Model\sta' + str(rec),
                                                                   #      title,
                                                                   #      message, message_ar,
                                                                   #      driver_name[0][0],title_ar])
                                                                   save_message_wizard(school_name, round_id, r,
                                                                                       'App\Model\sta' + str(rec),
                                                                                       title, title_ar,
                                                                                       message,
                                                                                       message_ar, driver_name[0][0])
                                                               elif status == 'near':
                                                                   if round_info[0][3] == 'pick_up':
                                                                       title_ar = "الباص قريب منك"
                                                                       title = 'The bus is near you.'
                                                                       message = ' You are next on the route. Please have ' + \
                                                                                 student_name[0][
                                                                                     0] + ' ready to leave'
                                                                       message_ar = "انت التالي, الحافلة اقتربت منك, الرجاء ان يكون" + \
                                                                                    student_name[0][
                                                                                        0] + "مستعداً"
                                                                   else:
                                                                       title_ar = "الباص قريب منك"
                                                                       title = 'The bus is near you.'
                                                                       message_ar = " علو وصول إلى المنزل " + student_name[0][0]
                                                                       message = ' You are next on the route. ' + student_name[0][ 0] + ' is about to arrive.'
                                                    if not(round_info[0][3] == 'pick_up') and status == 'in':
                                                        continue
                                                    print("2060-----------------------")
                                                    print(mobile_token1)
                                                    print(mobile_token)
                                                    if mobile_token1:
                                                        mobile_token = []
                                                        for e in mobile_token1:
                                                            mobile_token.append(e[0])
                                                        push_service = FCMNotification(
                                                            api_key="AAAAzysR6fk:APA91bFX6siqzUm-MQdhOWlno2PCOMfFVFIHmcfzRwmStaQYnUUJfDZBkC2kd2_s-4pk0o5jxrK9RsNiQnm6h52pzxDbfLijhXowIvVL2ReK7Y0FdZAYzmRekWTtOwsyG4au7xlRz1zD")
                                                        registration_id = mobile_token
                                                        message_title = title if lang =="en" else title_ar
                                                        message_body = message if lang =="en" else message_ar
                                                        if mobile_token and not ("token" in mobile_token):
                                                            notify_single_device = push_service.notify_single_device(
                                                                registration_id=registration_id[0],
                                                                message_title=message_title,
                                                                message_body=message_body)


                                                else:

                                                    if status == 'in' or status == 'near':
                                                        print("ssssssssssssssssssss2082",e[0])
                                                        mobile_token.append(e[0])
                                                        title = 'Bus notification'
                                                        title_ar ="اشعار من الحافلة"
                                                        if round_info[0][3] != 'pick_up':
                                                            title = "School Departure"
                                                            title_ar = "اشعار من الحافلة"

                                                        message_ar = "صعد إلى الحافلة"+ student_name[0][0] + str(bus_num[
                                                                   0][0])
                                                        message = student_name[0][0] + ' has just been checked into the bus'
                                                        date_string = datetime.datetime.now().strftime(
                                                            "%Y-%m-%d %H:%M:%S")
                                                        r = datetime.datetime.strptime(date_string,
                                                                                       '%Y-%m-%d %H:%M:%S')

                                                        # cursor.execute(
                                                        #     "INSERT INTO sh_message_wizard(round_id,create_date,from_type,type,message_en,message_ar,sender_name,type_ar)VALUES (%s,%s,%s,%s,%s,%s,%s,%s);",
                                                        #     [round_id, r, 'App\Model\sta'+str(rec), title, message, message_ar,
                                                        #      driver_name[0][0],title_ar])
                                                        save_message_wizard(school_name, round_id, r,
                                                                            'App\Model\sta' + str(rec),
                                                                            title, title_ar,
                                                                            message,
                                                                            message_ar, driver_name[0][0])


                                                    elif status == 'out':
                                                        mobile_token.append(e[0])
                                                        title = 'Checkout Notification'
                                                        title_ar = 'اشعار من الحافلة'
                                                        message_ar = 'وصل إلى المنزل.' + student_name[0][0]
                                                        message = 'The bus ' +str(bus_num[0]) + 'has arrived at your home and ' + \
                                                                  student_name[0][0] + ' has been checked out of the bus. '

                                                        date_string = datetime.datetime.now().strftime(
                                                            "%Y-%m-%d %H:%M:%S")
                                                        r = datetime.datetime.strptime(date_string,
                                                                                       '%Y-%m-%d %H:%M:%S')
                                                        if round_info[0][3] == 'pick_up':

                                                            # cursor.execute(
                                                            #     "INSERT INTO sh_message_wizard(round_id,create_date,from_type,type,message_en,message_ar,sender_name,type_ar)VALUES (%s,%s,%s,%s,%s,%s,%s,%s);",
                                                            #     [round_id, r, 'App\Model\sta'+str(rec), title,message, message_ar,driver_name[0][0],title_ar])
                                                            save_message_wizard(school_name, round_id, r,
                                                                                'App\Model\sta' + str(rec),
                                                                                title, title_ar,
                                                                                message,
                                                                                message_ar, driver_name[0][0])
                                                    else:
                                                        if status == 'no-show':
                                                            mobile_token.append(e[0])
                                                            title = ' No Show Notification'
                                                            title_ar = ' إشعار الغياب'
                                                            message_ar = "لم يظهر اليوم." + student_name[0][0]
                                                            message = student_name[0][0] + ' did not check into the bus today'
                                                            date_string = datetime.datetime.now().strftime(
                                                                "%Y-%m-%d %H:%M:%S")
                                                            r = datetime.datetime.strptime(date_string,
                                                                                           '%Y-%m-%d %H:%M:%S')
                                                            # cursor.execute(
                                                            #     "INSERT INTO sh_message_wizard(round_id,create_date,from_type,type,message_en,message_ar,sender_name,type_ar)VALUES (%s,%s,%s,%s,%s,%s,%s,%s);",
                                                            #     [round_id, r, 'App\Model\sta'+str(rec), title,
                                                            #      message, message_ar,
                                                            #      driver_name[0][0],title_ar])
                                                            save_message_wizard(school_name, round_id, r,
                                                                                'App\Model\sta' + str(rec),
                                                                                title, title_ar,
                                                                                message,
                                                                                message_ar, driver_name[0][0])
                                                        # yousef    qqqq
                                                        elif status == 'absent':

                                                            mobile_token.append(e[0])
                                                            title = 'Absence notification'
                                                            title_ar = 'اشعار من الحافلة'
                                                            message_ar = "غائب اليوم." + student_name[0][0]
                                                            message = ' Your child ' + student_name[0][
                                                                0] + ' has not checked into the bus and is absent today.'
                                                            date_string = datetime.datetime.now().strftime(
                                                                "%Y-%m-%d %H:%M:%S")
                                                            r = datetime.datetime.strptime(date_string,
                                                                                           '%Y-%m-%d %H:%M:%S')
                                                            # cursor.execute(
                                                            #     "INSERT INTO sh_message_wizard(round_id,create_date,from_type, type, message_en,message_ar,sender_name,type_ar)VALUES (%s,%s,%s,%s,%s,%s,%s,%s);",
                                                            #     [round_id, r, 'App\Model\sta'+str(rec), 'Absence notification',
                                                            #      message, message_ar,
                                                            #      driver_name[0][0],title_ar])
                                                            save_message_wizard(school_name, round_id, r,
                                                                                'App\Model\sta' + str(rec),
                                                                                'Absence notification', title_ar,
                                                                                message,
                                                                                message_ar, driver_name[0][0])

                                                    if not(round_info[0][3] == 'pick_up') and status == 'in':
                                                        continue
                                                    if mobile_token:
                                                        # notifications = list(data['notifications'].split(" "))
                                                        # li = list(data['notifications'].split(","))
                                                        lang = "ar" if "ar" in li[3] else 'en'
                                                        mobile_token = []

                                                        for e in mobile_token1:
                                                            mobile_token.append(e[0])

                                                        push_service = FCMNotification(
                                                            api_key="AAAAzysR6fk:APA91bFX6siqzUm-MQdhOWlno2PCOMfFVFIHmcfzRwmStaQYnUUJfDZBkC2kd2_s-4pk0o5jxrK9RsNiQnm6h52pzxDbfLijhXowIvVL2ReK7Y0FdZAYzmRekWTtOwsyG4au7xlRz1zD")
                                                        registration_id = mobile_token
                                                        message_title = title if "en" =="en" else title_ar
                                                        message_body = message if "en" =="en" else message_ar
                                                        print("--------------------------2192")
                                                        print(mobile_token)

                                                        if mobile_token and not ("token" in mobile_token):

                                                            notify_single_device = push_service.notify_single_device(
                                                                registration_id=registration_id[0],
                                                                message_title=message_title,
                                                                message_body=message_body)



                                result = {'status': 'OK'}
                                return Response(result)
                    else:
                        result = {'status': 'error'}
                        return Response(result)
                else:
                    result = {'status': 'error'}
                    return Response(result)
            else:
                result = {'status': 'error'}
                return Response(result)
        else:
            result = {'status': 'error'}
            return Response(result)


@api_view(['POST'])
def reordered_students(request):
    if request.method == 'POST':

        if request.headers:
            if request.headers.get('Authorization'):
                if 'Bearer' in request.headers.get('Authorization'):
                    ordered_students_ids = request.data.get('ordered_students_ids')
                    round_id = request.data.get('round_id')
                    au = request.headers.get('Authorization').replace('Bearer', '').strip()
                    db_name = Manager.objects.filter(token=au).values_list('db_name')
                    if db_name:
                        for e in db_name:
                            school_name = e[0]
                            school_name = Manager.pincode(school_name)
                            with connections[school_name].cursor() as cursor:
                                cursor.execute(
                                    "select  name,driver_id,type  from transport_round WHERE id = %s  ",
                                    [round_id])
                                round_info = cursor.fetchall()
                                cursor.execute(
                                    "select  name  from res_partner WHERE id = %s  ",
                                    [round_info[0][1]])
                                driver_id = cursor.fetchall()
                                for rec in range(len(ordered_students_ids) - 1):
                                    student_ids = []
                                    student_ids.append(ordered_students_ids[rec])
                                    student_ids.append(ordered_students_ids[rec + 1])
                                    cursor.execute("select display_name_search from student_student WHERE id in %s",
                                                   [tuple(student_ids)])
                                    student_transferred = cursor.fetchall()

                                    message_en = 'The driver ' + driver_id[0][
                                        0] + ' has changed the planed route of the round ' + round_info[0][
                                                     0] + '.The driver' + round_info[0][2] + ' the student ' + \
                                                 student_transferred[0][0] + ' before the student' + \
                                                 student_transferred[1][0] + ' .'
                                    date_string = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                    r = datetime.datetime.strptime(date_string, '%Y-%m-%d %H:%M:%S')
                                    cursor.execute(
                                        "INSERT INTO sh_message_wizard(round_id,create_date,from_type, type, message_en,sender_name)VALUES (%s,%s,%s,%s,%s,%s);",
                                        [round_id,r, 'App\Model\Driver', 'route_changed', message_en, driver_id[0][0]])
                                result = {"status": "ok"}
                                return Response(result)
                    else:
                        result = {'status': 'error'}
                        return Response(result)
                else:
                    result = {'status': 'error'}
                    return Response(result)
            else:
                result = {'status': 'error'}
                return Response(result)
        else:
            result = {'status': 'error'}
            return Response(result)
@api_view(['POST'])
def notify(request):
    if request.method == 'POST':
        print(request.data)
        if request.headers:
            if request.headers.get('Authorization'):
                if 'Bearer' in request.headers.get('Authorization'):
                    au = request.headers.get('Authorization').replace('Bearer', '').strip()
                    db_name = Manager.objects.filter(token=au).values_list('db_name')

                    if db_name:
                        for e in db_name:
                            school_name = e[0]

                        school_name = Manager.pincode(school_name)

                        # type = request.data.get('location_type')

                        # round_type = request.data.get('round_type')
                        # student_id = request.data[0].get('student_id')
                        # name = request.data[0].get('notification_type')

                        if not ("arrive_alarm" in  str(request.data)):
                            name = request.data.get('name')
                            round_id = request.data.get('round_id')
                            lat = request.data.get('lat')
                            long = request.data.get('long')
                        elif request.data[0].get('notification_type')=='arrive_alarm':
                            name="arrive_alarm"



                        if name == 'battery_low':
                            with connections[school_name].cursor() as cursor:
                                driver_id = Manager.objects.filter(token=au).values_list('driver_id')
                                for e in driver_id:
                                    driver_id = e[0]
                                date_string = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                r = datetime.datetime.strptime(date_string, '%Y-%m-%d %H:%M:%S')
                                cursor.execute(
                                    "select  bus_no  from fleet_vehicle WHERE driver_id = %s  ",
                                    [driver_id])
                                bus_num = cursor.fetchall()
                                cursor.execute(
                                    "select  name  from res_partner WHERE id = %s  ",
                                    [driver_id])
                                driver_id = cursor.fetchall()


                                message_en="The battery of the tracking device in the bus "+ str(bus_num[0][0])+" is running out of charge"
                                cursor.execute(
                                        "INSERT INTO sh_message_wizard(create_date,from_type, type, message_en,sender_name)VALUES (%s,%s,%s,%s,%s);",
                                        [r, 'App\Model\Driver', 'battery_low', message_en, driver_id[0][0]])
                                result = {'status': "ok"}
                                return Response(result)
                        elif name == 'network':
                            with connections[school_name].cursor() as cursor:
                                driver_id = Manager.objects.filter(token=au).values_list('driver_id')
                                for e in driver_id:
                                    driver_id = e[0]
                                date_string = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                r = datetime.datetime.strptime(date_string, '%Y-%m-%d %H:%M:%S')
                                cursor.execute(
                                    "select  bus_no  from fleet_vehicle WHERE driver_id = %s  ",
                                    [driver_id])
                                bus_num = cursor.fetchall()
                                cursor.execute(
                                    "select  name  from res_partner WHERE id = %s  ",
                                    [driver_id])
                                driver_id = cursor.fetchall()

                                message_en = "The battery of the tracking device in the bus " +  str(bus_num[0][0]) + " is running out of charge"
                                cursor.execute(
                                    "INSERT INTO sh_message_wizard(create_date,from_type, type, message_en,sender_name)VALUES (%s,%s,%s,%s,%s);",
                                    [r, 'App\Model\Driver', 'network', message_en, driver_id[0][0]])
                                result = {'status': "ok"}
                                return Response(result)
                        elif name == 'gps_off':
                            with connections[school_name].cursor() as cursor:
                                driver_id = Manager.objects.filter(token=au).values_list('driver_id')
                                for e in driver_id:
                                    driver_id = e[0]
                                date_string = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                r = datetime.datetime.strptime(date_string, '%Y-%m-%d %H:%M:%S')
                                cursor.execute(
                                    "select  bus_no  from fleet_vehicle WHERE driver_id = %s  ",
                                    [driver_id])
                                bus_num = cursor.fetchall()
                                cursor.execute(
                                    "select  name  from res_partner WHERE id = %s  ",
                                    [driver_id])
                                driver_id = cursor.fetchall()

                                message_en = "The battery of the tracking device in the bus " +  str(bus_num[0][0]) + " is running out of charge"
                                cursor.execute(
                                    "INSERT INTO sh_message_wizard(create_date,from_type, type, message_en,sender_name)VALUES (%s,%s,%s,%s,%s);",
                                    [r, 'App\Model\Driver', 'gps_off', message_en, driver_id[0][0]])
                                result = {'status': "ok"}
                                return Response(result)
                        elif name == 'route_changed':
                            with connections[school_name].cursor() as cursor:
                                driver_id = Manager.objects.filter(token=au).values_list('driver_id')
                                for e in driver_id:
                                    driver_id = e[0]
                                original_student_id = request.data.get('original_student_id')
                                picked_student_id = request.data.get('picked_student_id')
                                date_string = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                r = datetime.datetime.strptime(date_string, '%Y-%m-%d %H:%M:%S')
                                cursor.execute("select display_name_search from student_student WHERE id = %s",
                                               [picked_student_id])
                                student_picked = cursor.fetchall()
                                cursor.execute("select display_name_search from student_student WHERE id = %s",
                                               [original_student_id])
                                student_original = cursor.fetchall()


                                cursor.execute(
                                    "select   bus_no from fleet_vehicle WHERE driver_id = %s  ",
                                    [driver_id])
                                bus_num = cursor.fetchall()
                                cursor.execute(
                                    "select  name  from res_partner WHERE id = %s  ",
                                    [driver_id])
                                driver_id = cursor.fetchall()
                                cursor.execute(
                                    "select  name,driver_id,type  from transport_round WHERE id = %s  ",
                                    [round_id])
                                round_info = cursor.fetchall()
                                message_en = 'The driver ' + driver_id[0][
                                    0] + ' has changed the planed route of the round ' + round_info[0][
                                                0] + '.The driver' + round_info[0][2] + ' the student ' + \
                                            student_picked[0][0] + ' before the student' + \
                                            student_original[0][0] + ' .'

                                cursor.execute(
                                    "INSERT INTO sh_message_wizard(create_date,from_type, type, message_en,sender_name)VALUES (%s,%s,%s,%s,%s);",
                                    [r, 'App\Model\Driver', 'route_changed', message_en, driver_id[0][0]])
                                result = {'status': "ok"}
                                return Response(result)
                        elif name == 'user_speed_exceeded':
                            with connections[school_name].cursor() as cursor:
                                driver_id = Manager.objects.filter(token=au).values_list('driver_id')
                                for e in driver_id:
                                    driver_id = e[0]
                                speed = request.data.get('speed')
                                date_string = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                r = datetime.datetime.strptime(date_string, '%Y-%m-%d %H:%M:%S')
                                cursor.execute(
                                    "select  bus_no  from fleet_vehicle WHERE driver_id = %s  ",
                                    [driver_id])
                                bus_num = cursor.fetchall()
                                cursor.execute(
                                    "select  name  from res_partner WHERE id = %s  ",
                                    [driver_id])
                                driver_id = cursor.fetchall()

                                message_en = "The battery of the tracking device in the bus " +  str(bus_num[0][0]) + " is running out of charge"
                                cursor.execute(
                                    "INSERT INTO sh_message_wizard(create_date,from_type, type, message_en,sender_name)VALUES (%s,%s,%s,%s,%s);",
                                    [r, 'App\Model\Driver', 'user_speed_exceeded', message_en, driver_id[0][0]])
                                result = {'status': "ok"}
                                return Response(result)
                        elif name == 'user_no_move_time_exceeded':
                                with connections[school_name].cursor() as cursor:
                                    driver_id = Manager.objects.filter(token=au).values_list('driver_id')
                                    for e in driver_id:
                                        driver_id = e[0]
                                    date_string = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                    r = datetime.datetime.strptime(date_string, '%Y-%m-%d %H:%M:%S')
                                    cursor.execute(
                                        "select  name  from res_partner WHERE id = %s  ",
                                        [driver_id])
                                    driver_id = cursor.fetchall()

                                    message_en = "	The driver "+driver_id[0][0]+" has stopped in . The allowed time is 1 minute(s)"
                                    cursor.execute(
                                        "INSERT INTO sh_message_wizard(create_date,from_type, type, message_en,sender_name)VALUES (%s,%s,%s,%s,%s);",
                                        [r, 'App\Model\Driver', 'user_no_move_time_exceeded', message_en, driver_id[0][0]])
                                    result = {'status': "ok"}
                                    return Response(result)
                        elif name == 'emergency':
                                print(request.data)
                                emergency_text = request.data.get('emergency_text')
                                students_ids = request.data.get('students_ids')
                                with connections[school_name].cursor() as cursor:

                                    driver_id = Manager.objects.filter(token=au).values_list('driver_id')
                                    for e in driver_id:
                                        driver_id = e[0]
                                    date_string = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                    r = datetime.datetime.strptime(date_string, '%Y-%m-%d %H:%M:%S')
                                    cursor.execute(
                                        "select  name  from res_partner WHERE id = %s  ",
                                        [driver_id])
                                    driver_id = cursor.fetchall()
                                    for students in students_ids:
                                        cursor.execute(
                                            "select father_id,mother_id,responsible_id_value from student_student WHERE id = %s ",
                                            [students])
                                        columns4 = (x.name for x in cursor.description)
                                        student_student2 = cursor.fetchall()
                                        for parent_id in student_student2:
                                            print("kkkkkk",parent_id)
                                            cursor.execute(
                                                "INSERT INTO sh_message_wizard(round_id,create_date,from_type, type, message_en,sender_name,message_ar)VALUES (%s,%s,%s,%s,%s,%s,%s);",
                                                [round_id, r, 'App\Model\sta' + str(parent_id[0]), 'emergency_student', emergency_text,
                                                 driver_id[0][0], emergency_text])
                                    #     'App\Model\sta' + str(parent_id)
                                    # cursor.execute(
                                    #     "INSERT INTO sh_message_wizard(round_id,create_date,from_type, type, message_en,sender_name,message_ar)VALUES (%s,%s,%s,%s,%s,%s,%s);",
                                    #     [round_id,r, 'App\Model\Driver', 'emergency', emergency_text, driver_id[0][0],emergency_text])
                                    result = {'status': "ok"}
                                    return Response(result)
                        elif name == 'changed_location':
                                with connections[school_name].cursor() as cursor:
                                    parent_id = Manager.objects.filter(token=au).values_list('driver_id')
                                    for e in parent_id:
                                        parent_id = e[0]
                                    student_id = request.data.get('student_id')
                                    driver_id = parent_id
                                    date_string = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                    r = datetime.datetime.strptime(date_string, '%Y-%m-%d %H:%M:%S')
                                    cursor.execute(
                                        "select  bus_no  from fleet_vehicle WHERE driver_id = %s  ",
                                        [driver_id])
                                    bus_num = cursor.fetchall()
                                    cursor.execute(
                                        "select  name  from res_partner WHERE id = %s  ",
                                        [driver_id])
                                    driver_id = cursor.fetchall()
                                    cursor.execute("select display_name_search from student_student WHERE id = %s",
                                                   [student_id])
                                    student_name = cursor.fetchall()
                                    type1 = request.data.get('location_type')
                                    lat = request.data.get('lat')
                                    long = request.data.get('long')

                                    if type1 == 'drop-off':

                                        cursor.execute(
                                            "UPDATE   student_student SET drop_off_lat=%s ,drop_off_lng=%s WHERE id = %s",
                                            [lat, long, student_id])

                                    elif type1 == 'pick-up':

                                        cursor.execute(
                                            "UPDATE   student_student SET pick_up_lat=%s ,pick_up_lng=%s WHERE id = %s",
                                            [lat, long, student_id])

                                    elif type1 == 'both':
                                       cursor.execute(
                                            "UPDATE   student_student SET pick_up_lat=%s ,pick_up_lng=%s,drop_off_lat=%s,drop_off_lng=%s WHERE id = %s",
                                            [lat, long, lat, long, student_id])

                                    message_en = "	The home location of the student "+str(student_name[0][0])+" has been changed by the bus  " + str(bus_num[0][0])
                                    cursor.execute(
                                        "INSERT INTO sh_message_wizard(create_date,from_type, type, message_en,sender_name)VALUES (%s,%s,%s,%s,%s);",
                                        [r, 'App\Model\Driver', 'changed_location_driver', message_en, driver_id[0][0]])

                                    result = {'status': "ok"}
                                    return Response(result)
                        elif name == 'arrive_alarm':
                            round_type = request.data[0].get('round_type')
                            # select  father_id,mother_id,responsible_id_value from student_student WHERE id=1
                            with connections[school_name].cursor() as cursor:
                                cursor.execute("select  father_id,mother_id,responsible_id_value from student_student WHERE id= %s", [request.data[0].get('student_id')])
                                student_info = cursor.fetchall()
                                cursor.execute(
                                    "select  display_name_search from student_student WHERE id= %s",
                                    [request.data[0].get('student_id')])
                                student_name = cursor.fetchall()
                                driver_id = Manager.objects.filter(token=au).values_list('driver_id')
                                for e in driver_id:
                                    driver_id = e[0]
                                cursor.execute(
                                    "select bus_no from fleet_vehicle WHERE driver_id = %s  ",
                                    [driver_id])
                                bus_num = cursor.fetchall()

                                mobile_token = []
                                lang = 'en'
                                for rec in student_info[0]:
                                    cursor.execute("select  settings from school_parent WHERE id = %s", [rec])
                                    setting = cursor.fetchall()
                                    if setting:

                                        if not('None' in str(setting)) :

                                            data = json.loads(setting[0][0])
                                            title = ''
                                            message = ''

                                            if type(data['notifications']) is dict:
                                                if "ar" in data['notifications']['locale']:
                                                    lang = "ar"
                                            else:
                                                li = list(data['notifications'].split(","))
                                                lang = "ar" if "ar" in li[3] else 'en'
                                    mobile_token1 = ManagerParent.objects.filter(Q(parent_id=rec),
                                                                                 Q(db_name=school_name),
                                                                                 Q(is_active=True)).values_list( 'mobile_token').order_by('-pk')
                                    # push_service = FCMNotification(
                                    #     api_key="AAAAzysR6fk:APA91bFX6siqzUm-MQdhOWlno2PCOMfFVFIHmcfzRwmStaQYnUUJfDZBkC2kd2_s-4pk0o5jxrK9RsNiQnm6h52pzxDbfLijhXowIvVL2ReK7Y0FdZAYzmRekWTtOwsyG4au7xlRz1zD")
                                    # # registration_id = "fw7CryLaRjW8TEKOyspKLo:APA91bFQYaCp4MYes5BIQtHFkOQtcPdtVLB0e5BJ-dQKE2WeYBeZ3XSmNpgWJX-veRO_35lOuGzTm6QBv1c2YZM-4WcT1drKBvLdJxEFkhG5l5c-Af_IRtCJzOOKf7c5SmEzzyvoBrQx"
                                    #
                                    # if mobile_token1:
                                    #     registration_id = mobile_token1[0][0]
                                    #     message_title_ar = "اشعار من الحافلة"
                                    #     message_body_ar = " لقد وصلت الحافلة " + str(bus_num[0][
                                    #                                                      0]) + " إلى المنزل " if round_type == "dropoff" else "لقد وصلت الحافلة " + str(
                                    #         bus_num[0][0]) + ".الرجاء إرسال " + student_name[0][0] + "للصعود للحافلة"
                                    #     message_title = "Arrival - Parent" if round_type == "dropoff" else "Bus Arrival"
                                    #     message_body = "The bus " + str(bus_num[0][0]) + "has arrived at your home"
                                    #     result = push_service.notify_single_device(registration_id=registration_id,
                                    #                                                message_title=message_title if lang == "en" else message_title_ar,
                                    #                                                message_body=message_body if lang == "en" else message_body_ar)
                                    for e in mobile_token1:
                                            mobile_token.append(e[0])

                                    push_service = FCMNotification(
                                        api_key="AAAAzysR6fk:APA91bFX6siqzUm-MQdhOWlno2PCOMfFVFIHmcfzRwmStaQYnUUJfDZBkC2kd2_s-4pk0o5jxrK9RsNiQnm6h52pzxDbfLijhXowIvVL2ReK7Y0FdZAYzmRekWTtOwsyG4au7xlRz1zD")
                                    registration_id = "fw7CryLaRjW8TEKOyspKLo:APA91bFQYaCp4MYes5BIQtHFkOQtcPdtVLB0e5BJ-dQKE2WeYBeZ3XSmNpgWJX-veRO_35lOuGzTm6QBv1c2YZM-4WcT1drKBvLdJxEFkhG5l5c-Af_IRtCJzOOKf7c5SmEzzyvoBrQx"

                                if mobile_token:
                                    registration_id = mobile_token[0]
                                    message_title_ar="اشعار من الحافلة"
                                    message_body_ar =" لقد وصلت الحافلة " + str(bus_num[0][0]) +" إلى المنزل " if round_type=="dropoff" else "لقد وصلت الحافلة " + str(bus_num[0][0]) + ".الرجاء إرسال " +student_name[0][0]+"للصعود للحافلة"
                                    message_title = "Arrival - Parent" if round_type=="dropoff" else "Bus Arrival"
                                    message_body = "The bus " + str(bus_num[0][0]) + "has arrived at your home"
                                    result = push_service.notify_single_device(registration_id=registration_id,
                                                                               message_title=message_title if lang =="en" else message_title_ar,
                                                                               message_body=message_body if lang =="en" else message_body_ar)

                                # user_no_move_time_exceeded

                                result ={'status': "ok"}
                                return Response(result)



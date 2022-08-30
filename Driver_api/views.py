from django.conf import settings

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

# Create your views here.


@api_view(['POST'])
def driver_login(request):
    if request.method == 'POST':
        pincode = request.data.get('bus_pin')
        mobile_token = request.data.get('mobile_token')
        school_name = Manager.pincode(pincode)
        # print("ssssssssssssssssssssssssssssssSS",pincode,request.data.get('platform'),mobile_token)
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
            manager = Manager(token=unique_id, db_name=school_name, driver_id=data_id_bus[0][0], mobile_token=mobile_token)
            manager.save()

            # *------------------------------------------------------------------------------------------------*
            # Details for login setting

            cursor.execute("""
            
            select nearby_distance,lat,lng,battery_low,location_refresh_rate,timezone,utc_offset,speed_limit_watch,standstill_watch,notify_if_driver_check_in_out_geo_fence,notify_on_battery_low_of_drivers_app,notify_it_driver_turns_off_gps,user_speed_exceeded,user_no_move_time_exceeded from transport_setting ORDER BY ID DESC LIMIT 1
            
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
                "tracklink":True,
                "bus_id": data_id_bus[0][2],
                "bus_number": data_id_bus[0][1],
                "driver_id": data_id_bus[0][0],
                "nearby_distance": login_details1[0]['nearby_distance'],
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
                        "notify_if_driver_check_in_out_geo_fence": login_details1[0]['notify_if_driver_check_in_out_geo_fence'],
                        "notify_on_battery_low_of_drivers_app": login_details1[0]['notify_on_battery_low_of_drivers_app'],
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
                                "select name,start_time,pick_up_address,drop_off_address,pick_up_lat,pick_up_lng,drop_off_lat,drop_off_lng,route_id,id,is_active from transport_round WHERE vehicle_id = %s and  type = %s",
                                [request.data.get('bus_id'),
                                 'drop_off' if 'drop' in request.data.get('round_type') else 'pick_up'])
                            columns = (x.name for x in cursor.description)
                            list_round = cursor.fetchall()
                            list_round1 = []
                            columnNames = [column[0] for column in cursor.description]
                            for record in list_round:
                                list_round1.append(dict(zip(columnNames, record)))
                            # list_round = cursor.fetchall()
                            # print("dddddddddddddddddddddddddddddddddddddddddddddddd",list_round1)
                            result1 = {}
                            round = []
                            r_id=[]
                            l_round=[]
                            for id in list_round1:
                                r_id.append(id['id'])
                            if r_id:
                                cursor.execute("select id,day_id,round_id from round_schedule WHERE round_id in %s and day_id =%s",
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
                                        end=False
                                        start=False
                                        cancel=False

                                        cursor.execute(
                                            "select  name,vehicle_id,driver_id from transport_round WHERE id = %s  ",
                                            [list_round1[rec]['id']])
                                        round_info = cursor.fetchall()
                                        cursor.execute(
                                            "select  id,round_start,round_end,na from round_history WHERE round_id = %s and driver_id=%s and vehicle_id = %s and round_name=%s ORDER BY ID DESC LIMIT 1 ",
                                            [list_round1[rec]['id'], round_info[0][2], round_info[0][1], list_round1[rec]['id']])
                                        round_history = cursor.fetchall()
                                        if round_history:

                                            now = datetime.date.today()
                                            if round_history[0][2]:
                                                if round_history[0][2].strftime('%Y-%m-%d') == str(now):
                                                    start = False
                                                    cancel = False
                                                    end=True
                                            if (round_history[0][1].strftime('%Y-%m-%d')  == str(now)) and not (round_history[0][2].strftime('%Y-%m-%d') if round_history[0][2] else round_history[0][2] == str(now)) and (round_history[0][3] !='cancel'):
                                                start=True
                                                cancel = False
                                                end = False
                                            if  (round_history[0][1].strftime('%Y-%m-%d')  == str(now)) and round_history[0][3] =='cancel':
                                                end = False
                                                start = False
                                                cancel = True
                                        else:
                                            end = False
                                            start=False
                                            cancel=False
                                        result1[rec] = {
                                            "round_time": str(list_round1[rec]['start_time']),
                                            "name": str(list_round1[rec]['name']),
                                            "date": None,
                                            "pick_up_address": list_round1[rec]['pick_up_address'],
                                            "drop_off_address": list_round1[rec]['drop_off_address'],
                                            "pick_up_lat": list_round1[rec]['pick_up_lat'] if list_round1[rec]['pick_up_lat'] else 0,
                                            "pick_up_lng": list_round1[rec]['pick_up_lng'] if list_round1[rec]['pick_up_lng'] else 0,
                                            "drop_off_lat": list_round1[rec]['drop_off_lat'] if list_round1[rec]['drop_off_lat'] else 0,
                                            "drop_off_lng": list_round1[rec]['drop_off_lng'] if list_round1[rec]['drop_off_lng'] else 0,
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
                                            "moved_students": [],
                                            "students_list": [day_list]

                                        }
                            cursor.execute(
                                """ select 	allow_driver_change_students_location,allow_driver_to_use_beacon from transport_setting ORDER BY ID DESC LIMIT 1""")
                            login_details = cursor.fetchall()

                            for rec in range(len(result1)):
                                round.append(result1[rec])
                                result = {
                                    "school_settings": {
                                        "change_student_location": login_details[0][1],
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
                            # print(day_name,round_id)
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
                                "select student_id from transport_participant WHERE round_schedule_id = %s ORDER BY sequence ASC",
                                [rounds_details[0][0]])
                            columns4 = (x.name for x in cursor.description)
                            rounds_count_student = cursor.fetchall()
                            ch_in = 0
                            ch_out = 0
                            if round_info1[0][1] == 'pick_up':
                                ch_out = len(rounds_count_student)
                            else:
                                ch_in = len(rounds_count_student)


                            st_id = []

                            for k in rounds_count_student:
                                st_id.append(k[0])
                            if st_id:
                                cursor.execute("select * from student_student WHERE id in %s ",
                                               [tuple(st_id)])
                                columns4 = (x.name for x in cursor.description)
                                student_student = cursor.fetchall()
                                # s = [dict(zip(columns4, row)) for row in student_student]
                                student_student1 = []
                                columnNames = [column[0] for column in cursor.description]

                                for record in student_student:
                                    student_student1.append(dict(zip(columnNames, record)))
                                student_info = {}
                                for std in range(len(student_student)):

                                    if student_student[std]:
                                        in_round = False
                                        out_round = False
                                        abs = False
                                        no_show = False
                                        lat=0
                                        long=0
                                        cursor.execute(
                                            "select  name,vehicle_id,driver_id from transport_round WHERE id = %s  ",
                                            [round_id])
                                        round_info = cursor.fetchall()
                                        cursor.execute(
                                            "select  id,round_start,round_end,na from round_history WHERE round_id = %s and driver_id=%s and vehicle_id = %s and round_name=%s ORDER BY ID DESC LIMIT 1 ",
                                            [round_id, round_info[0][2], round_info[0][1],
                                             round_id])
                                        round_history = cursor.fetchall()
                                        if round_history:
                                            now = datetime.date.today()
                                            if round_history[0][1].strftime('%Y-%m-%d') == str(now):
                                                cursor.execute(
                                                    "select  activity_type,lat,long from student_history WHERE round_id = %s and student_id=%s and history_id = %s  ORDER BY ID DESC LIMIT 1 ",
                                                    [round_id, student_student1[std]['id'], round_history[0][0]])
                                                student_history = cursor.fetchall()
                                                if student_history:
                                                    lat=student_history[0][1]
                                                    long=student_history[0][2]

                                                    if student_history[0][0]=='in':

                                                        in_round=True
                                                        out_round =False
                                                        abs=False
                                                        no_show=False
                                                        cursor.execute(
                                                            "UPDATE public.transport_participant SET transport_state = %s WHERE student_id =%s AND round_schedule_id= %s",
                                                            ['in', student_student1[std]['id'],
                                                             rounds_details[0][0]])
                                                        if round_info1[0][1] == 'pick_up':

                                                            ch_in = ch_in + 1
                                                            ch_out = ch_out - 1
                                                        else:

                                                            ch_in = ch_in - 1
                                                            ch_out = ch_out + 1

                                                    elif student_history[0][0]=='out':
                                                        in_round = False
                                                        out_round = True
                                                        abs = False
                                                        no_show = False
                                                        cursor.execute(
                                                            "UPDATE public.transport_participant SET transport_state = %s WHERE student_id =%s AND round_schedule_id= %s",
                                                            ['out', student_student1[std]['id'],
                                                             rounds_details[0][0]])
                                                        if round_info1[0][1] == 'pick_up':
                                                            ch_in = ch_in + 1
                                                            ch_out = ch_out - 1
                                                        else:

                                                            ch_in = ch_in - 1
                                                            ch_out = ch_out + 1
                                                    elif student_history[0][0]=='no-show':
                                                        in_round = False
                                                        out_round = False
                                                        abs = False
                                                        no_show = True
                                                        cursor.execute(
                                                            "UPDATE public.transport_participant SET transport_state = %s WHERE student_id =%s AND round_schedule_id= %s",
                                                            ['no_show', student_student1[std]['id'],
                                                             rounds_details[0][0]])
                                                    elif student_history[0][0]=='absent':
                                                        in_round = False
                                                        out_round = False
                                                        abs = True
                                                        no_show = False
                                                        cursor.execute(
                                                            "UPDATE public.transport_participant SET transport_state = %s WHERE student_id =%s AND round_schedule_id= %s",
                                                            ['absent', student_student1[std]['id'], rounds_details[0][0]])
                                                    elif student_history[0][0] == 'absent_all':
                                                        in_round = False
                                                        out_round = False
                                                        abs = True
                                                        no_show = False


                                                        cursor.execute(
                                                            "UPDATE public.transport_participant SET transport_state = %s WHERE student_id =%s AND round_schedule_id= %s",
                                                            ['absent_all', student_student1[std]['id'],
                                                             rounds_details[0][0]])
                                                else:
                                                    if round_info1[0][1] == 'pick_up':

                                                        cursor.execute(
                                                            "UPDATE public.transport_participant SET transport_state = %s WHERE student_id =%s AND round_schedule_id= %s",
                                                            ['out', student_student1[std]['id'],
                                                             rounds_details[0][0]])
                                                        # ch_out = len(rounds_count_student)
                                                    else:

                                                        cursor.execute(
                                                            "UPDATE public.transport_participant SET transport_state = %s WHERE student_id =%s AND round_schedule_id= %s",
                                                            ['in', student_student1[std]['id'],
                                                             rounds_details[0][0]])
                                                        # ch_in = len(rounds_count_student)

                                        cursor.execute("select * from school_parent WHERE id = %s",
                                                       [student_student1[std]['father_id']])
                                        columns_f = (x.name for x in cursor.description)
                                        father = cursor.fetchall()
                                        father_inf = [dict(zip(columns_f, row)) for row in father]
                                        cursor.execute("select * from school_parent WHERE id = %s",
                                                       [student_student1[std]['mother_id']])
                                        columns_m = (x.name for x in cursor.description)
                                        mother = cursor.fetchall()
                                        mother_inf = [dict(zip(columns_m, row)) for row in mother]
                                        student_info[std] = {
                                            "id": student_student1[std]['id'],
                                            "year_id": student_student1[std]['year_id'],
                                            "emergency_call": student_student1[std]['emergency_call'],
                                            "display_name_search": student_student1[std]['display_name_search'],
                                            "user_id": student_student1[std]['user_id'],
                                            "color": student_student1[std]['color'],
                                            "email": student_student1[std]['email'],
                                            "mobile": student_student1[std]['mobile'],
                                            "name": student_student1[std]['name'],
                                            "contact_phone1": student_student1[std]['contact_phone1'],
                                            "contact_mobile1": student_student1[std]['contact_mobile1'],
                                            "nationality_id": student_student1[std]['nationality_id'],
                                            "admission_date": student_student1[std]['admission_date'],
                                            "second_name": student_student1[std]['second_name'],
                                            "third_name": student_student1[std]['third_name'],
                                            "last_name": student_student1[std]['last_name'],
                                            "mother_tongue": student_student1[std]['mother_tongue'],
                                            "blood_group": student_student1[std]['blood_group'],
                                            "date_of_birth": student_student1[std]['date_of_birth'],
                                            "building_number": student_student1[std]['building_number'],
                                            "building_name": student_student1[std]['building_name'],
                                            "street": student_student1[std]['street'],
                                            "flat_number": student_student1[std]['flat_number'],
                                            "area_id": student_student1[std]['area_id'],
                                            "state_id": student_student1[std]['state_id'],
                                            "address_note": student_student1[std]['address_note'],
                                            "terminate_reason": student_student1[std]['terminate_reason'],
                                            "terminate_date": student_student1[std]['terminate_date'],
                                            "alumni_date": student_student1[std]['alumni_date'],
                                            "national_id": student_student1[std]['national_id'],
                                            "passport_number": student_student1[std]['passport_number'],
                                            "religion_id": student_student1[std]['religion_id'],
                                            "country_id": student_student1[std]['country_id'],
                                            "id_number": student_student1[std]['id_number'],
                                            "is_demo": student_student1[std]['is_demo'],
                                            "birth_certificate_no": student_student1[std]['birth_certificate_no'],
                                            "issued_at": student_student1[std]['issued_at'],
                                            "issue_date": student_student1[std]['issue_date'],
                                            "previous_year_avg": student_student1[std]['previous_year_avg'],
                                            "learning_disabilities": student_student1[std]['learning_disabilities'],
                                            "need_attention": student_student1[std]['need_attention'],
                                            "attention_follow_up_notes": student_student1[std]['attention_follow_up_notes'],
                                            "special_needs": student_student1[std]['special_needs'],
                                            "health_condition_notes": student_student1[std]['health_condition_notes'],
                                            "allergies": student_student1[std]['allergies'],
                                            "allergies_desc": student_student1[std]['allergies_desc'],
                                            "bus_number": student_student1[std]['bus_number'],
                                            "state": student_student1[std]['state'],
                                            "father_id": student_student1[std]['father_id'],
                                            "mother_id": student_student1[std]['mother_id'],
                                            "family_relation_id":student_student1[std]['family_relation_id'],
                                            "message_main_attachment_id": student_student1[std]['message_main_attachment_id'],
                                            "create_uid": student_student1[std]['create_uid'],
                                            "create_date": student_student1[std]['create_date'],
                                            "write_uid": student_student1[std]['write_uid'],
                                            "write_date": student_student1[std]['write_date'],
                                            "is_banned": student_student1[std]['is_banned'],
                                            "currency_id": student_student1[std]['currency_id'],
                                            "name_ar": student_student1[std]['name_ar'],
                                            "second_name_ar": student_student1[std]['second_name_ar'],
                                            "third_name_ar": student_student1[std]['third_name_ar'],
                                            "last_name_ar": student_student1[std]['last_name_ar'],
                                            "display_name_ar": student_student1[std]['display_name_ar'],
                                            "moe_grace_period": student_student1[std]['moe_grace_period'],
                                            "deadline_date": student_student1[std]['deadline_date'],
                                            "neighborhood_id":student_student1[std]['neighborhood_id'],
                                            "assembly_id": student_student1[std]['assembly_id'],
                                            "ministry_state_id": student_student1[std]['ministry_state_id'],
                                            "student_emis_no": student_student1[std]['student_emis_no'],
                                            "family_members": student_student1[std]['family_members'],
                                            "borthers": student_student1[std]['borthers'],
                                            "sisters": student_student1[std]['sisters'],
                                            "soas": student_student1[std]['soas'],
                                            "marital_state": student_student1[std]['marital_state'],
                                            "education": student_student1[std]['education'],
                                            "external_financial_aid":student_student1[std]['external_financial_aid'],
                                            "aid_type": student_student1[std]['aid_type'],
                                            "international_refugee_card_status": student_student1[std]['international_refugee_card_status'],
                                            "district_id": student_student1[std]['district_id'],
                                            "province_id": student_student1[std]['province_id'],
                                            "partner_id": student_student1[std]['partner_id'],
                                            "book_requests": student_student1[std]['book_requests'],
                                            "country_of_birth": student_student1[std]['country_of_birth'],
                                            "city_of_birth": student_student1[std]['city_of_birth'],
                                            "file_name": student_student1[std]['file_name'],
                                            "pickup_by_parent": student_student1[std]['pickup_by_parent'],
                                            "dropoff_by_parent": student_student1[std]['dropoff_by_parent'],
                                            "area_ids": student_student1[std]['area_ids'],
                                            "round_type": student_student1[std]['round_type'],
                                            "contact_person": student_student1[std]['contact_person'],
                                            "family_relation": student_student1[std]['family_relation'],
                                            "contact_person_number": student_student1[std]['contact_person_number'],
                                            "round_address_type": student_student1[std]['round_address_type'],
                                            "pick_up_type": student_student1[std]['pick_up_type'],
                                            "drop_off_type": student_student1[std]['drop_off_type'],
                                            "second_pickup_address": student_student1[std]['second_pickup_address'],
                                            "second_dropoff_address": student_student1[std]['second_dropoff_address'],
                                            "dropoff_as_pickup": student_student1[std]['dropoff_as_pickup'],
                                            "same_as_address": student_student1[std]['same_as_address'],
                                            "pickup_building_number": student_student1[std]['pickup_building_number'],
                                            "pickup_building_name": student_student1[std]['pickup_building_name'],
                                            "pickup_street": student_student1[std]['pickup_street'],
                                            "pickup_flat_number": student_student1[std]['pickup_flat_number'],
                                            "pickup_area_id": student_student1[std]['pickup_area_id'],
                                            "pickup_state_id": student_student1[std]['pickup_state_id'],
                                            "pickup_address_note": student_student1[std]['pickup_address_note'],
                                            "sec_pickup_building_number": student_student1[std]['sec_pickup_building_number'],
                                            "sec_pickup_building_name": student_student1[std]['sec_pickup_building_name'],
                                            "sec_pickup_street": student_student1[std]['sec_pickup_street'],
                                            "sec_pickup_flat_number": student_student1[std]['sec_pickup_flat_number'],
                                            "sec_pickup_area_id": student_student1[std]['sec_pickup_area_id'],
                                            "sec_pickup_state_id": student_student1[std]['sec_pickup_state_id'],
                                            "sec_pickup_address_note": student_student1[std]['sec_pickup_address_note'],
                                            "dropoff_building_number": student_student1[std]['dropoff_building_number'],
                                            "dropoff_building_name": student_student1[std]['dropoff_building_name'],
                                            "dropoff_street": student_student1[std]['dropoff_street'],
                                            "dropoff_flat_number": student_student1[std]['dropoff_flat_number'],
                                            "dropoff_area_id": student_student1[std]['dropoff_area_id'],
                                            "dropoff_state_id": student_student1[std]['dropoff_state_id'],
                                            "dropoff_address_note": student_student1[std]['dropoff_address_note'],
                                            "sec_dropoff_building_number": student_student1[std]['sec_dropoff_building_number'],
                                            "sec_dropoff_building_name": student_student1[std]['sec_dropoff_building_name'],
                                            "sec_dropoff_street": student_student1[std]['sec_dropoff_street'],
                                            "sec_dropoff_flat_number": student_student1[std]['sec_dropoff_flat_number'],
                                            "sec_dropoff_area_id": student_student1[std]['sec_dropoff_area_id'],
                                            "sec_dropoff_state_id": student_student1[std]['sec_dropoff_state_id'],
                                            "sec_dropoff_address_note": student_student1[std]['sec_dropoff_address_note'],
                                            "is_suspended": student_student1[std]['is_suspended'],
                                            "sequence": student_student1[std]['sequence'],
                                            "password": student_student1[std]['password'],
                                            "image_url":'https://trackware-schools.s3.eu-central-1.amazonaws.com/' + student_student1[std]['image_url'] if student_student1[std]['image_url'] else student_student[std][131],
                                            "round_id": student_student1[std]['round_id'],
                                            "responsible_id_value": student_student1[std]['responsible_id_value'],
                                            "grade":student_student1[std]['academic_grade_name1'],
                                            # "first_mandatory": student_student[std][134],
                                            # "second_mandatory": student_student[std][135],
                                            # "third_mandatory": student_student[std][136],
                                            # "last_mandatory": student_student[std][137],
                                            "section_id_value": student_student1[std]['section_id_value'],
                                            # "grade":student_student[std][147],
                                            # "laravel_through_key": s[std]['laravel_through_key'],
                                            "parents_info": [
                                                {
                                                    "father": {
                                                        "mobile_token": father_inf[0]['mobile_token'] if father_inf else "",
                                                        # "mobile_pn_registration_id": father_inf[0]['mobile_pn_registration_id']if father_inf else "",
                                                        # "invite_count": father_inf[0]['invite_count']if father_inf else "",
                                                        "settings": father_inf[0]['settings'] if father_inf else "",
                                                        "number": father_inf[0]['mobile'] if father_inf else "",
                                                        "id": father_inf[0]['id'] if father_inf else -1

                                                    },
                                                    "mother": {
                                                        "mobile_token": mother_inf[0]['mobile_token'] if mother_inf else "",
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
                                            "avatar": student_student1[std]['image_url'] if student_student1[std]['image_url'] else "https://s3.eu-central-1.amazonaws.com/trackware.schools/public_images/default_student.png",
                                            "check_in": in_round,
                                            "check_out": out_round,
                                            "absent": abs,
                                            "lat": lat,
                                            "lng": long,
                                            "no_show": no_show,
                                        }
                                student=[]
                                for std_inf in range(len(student_info)):
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
                                    "select  id from transport_round WHERE id = %s",
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


@api_view(['POST'])
def set_round_status(request):
    if request.method == 'POST':
        if request.headers:
            if request.headers.get('Authorization'):
                if 'Bearer' in request.headers.get('Authorization'):
                    au = request.headers.get('Authorization').replace('Bearer', '').strip()
                    db_name = Manager.objects.filter(token=au).values_list('db_name')
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
                                assistant_id= request.data.get('assistant_id')
                                cursor.execute(
                                    "select  name,vehicle_id,driver_id ,type from transport_round WHERE id = %s  ",
                                    [round_id])
                                round_info = cursor.fetchall()
                                if status =='start':
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
                                                #
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
                                                ch_in=0
                                                ch_out=0
                                                if round_info[0][3]=='pick_up':
                                                    ch_in=len(rounds_count_student)
                                                else:
                                                    ch_out = len(rounds_count_student)

                                                cursor.execute(
                                                    "UPDATE public.transport_round SET total_checkedout_students= %s , total_checkedin_students= %s WHERE id=%s",
                                                    [ch_out,ch_in, round_id])
                                                stds = []
                                                for rec in rounds_count_student:
                                                    stds.append(rec[0])

                                                cursor.execute(
                                                    "UPDATE public.transport_participant SET transport_state = %s WHERE student_id in %s AND round_schedule_id= %s",
                                                    ["", tuple(stds), rounds_details[0][0]])


                                                cursor.execute(
                                                    "INSERT INTO  round_history (round_name,round_id,distance,vehicle_id,driver_id,round_start,attendant_id) VALUES (%s,%s,%s,%s,%s,%s,%s); ",
                                                    [round_id, round_id, distance, round_info[0][1], round_info[0][2],
                                                     datetime.datetime.now(), assistant_id])
                                        else:
                                            cursor.execute(
                                                "INSERT INTO  round_history (round_name,round_id,distance,vehicle_id,driver_id,round_start,attendant_id) VALUES (%s,%s,%s,%s,%s,%s,%s); ",
                                                [round_id, round_id, distance, round_info[0][1], round_info[0][2], datetime.datetime.now(),assistant_id])
                                elif status =='end' or status == 'force_end':


                                    cursor.execute(
                                        "select  round_start,id from round_history WHERE round_id = %s and driver_id=%s and vehicle_id = %s and round_name=%s ORDER BY ID DESC LIMIT 1 ",
                                        [round_id,round_info[0][2],round_info[0][1],round_id])
                                    round_history = cursor.fetchall()
                                    if round_history:
                                        now = datetime.date.today()
                                        if round_history[0][0].strftime('%Y-%m-%d')==str(now):
                                            cursor.execute(
                                                "UPDATE public.round_history SET round_end= %s WHERE id=%s",
                                                [datetime.datetime.now(),round_history[0][1]])
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
                                    "UPDATE public.transport_round SET is_active= not(is_active), pick_up_lat=%s ,pick_up_lng=%s ,drop_off_lat=%s ,drop_off_lng=%s WHERE id=%s",
                                    [lat, long, lat, long, round_id])
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
                    if db_name:
                        for e in db_name:
                            school_name = e[0]
                            school_name = Manager.pincode(school_name)
                            with connections[school_name].cursor() as cursor:
                                students =request.data.get('students')
                                round_id = students[0]['round_id']
                                status = students[0]['status']
                                day_count = students[0]['day_count']
                                lat = students[0]['lat']
                                long = students[0]['long']
                                student_id = students[0]['student_id']
                                waiting_minutes = students[0]['waiting_minutes']
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
                                            "select  datetime from round_student_history WHERE round_id = %s and student_id=%s and history_id = %s  ORDER BY ID DESC LIMIT 1 ",
                                            [round_id, student_id, round_history[0][0]])
                                        student_history = cursor.fetchall()
                                        if student_history:
                                            cursor.execute(
                                                "INSERT INTO  student_history (round_id,student_id,bus_check_in,datetime,history_id,lat,long,activity_type) VALUES (%s,%s,%s,%s,%s,%s,%s,%s); ",
                                                [round_id, student_id, datetime.datetime.now(),
                                                 datetime.datetime.now(), round_history[0][0], lat, long, status])
                                            if status=='in':

                                                cursor.execute(
                                                    "UPDATE public.round_student_history SET bus_check_in = %s WHERE id =%s ",
                                                    [datetime.datetime.now(), student_history[0][0]])
                                                if round_info[0][3] == 'pick_up':
                                                    ch_in = round_info[0][5]+1
                                                    ch_out = round_info[0][4] - 1
                                                else:
                                                    ch_in = round_info[0][5] -1
                                                    ch_out = round_info[0][4] + 1

                                                cursor.execute(
                                                    "UPDATE public.transport_round SET total_checkedout_students= %s , total_checkedin_students= %s WHERE id=%s",
                                                    [ch_out, ch_in, round_id])

                                            elif status=='out':

                                                cursor.execute(
                                                    "UPDATE public.round_student_history SET time_out = %s WHERE id =%s ",
                                                    [datetime.datetime.now(), student_id])
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
                                            cursor.execute(
                                                "INSERT INTO  round_student_history (round_id,student_id,driver_waiting,bus_check_in,datetime,history_id) VALUES (%s,%s,%s,%s,%s,%s); ",
                                                [round_id, student_id, waiting_minutes, datetime.datetime.now(),
                                                 datetime.datetime.now(), round_history[0][0]])
                                            cursor.execute(
                                                "INSERT INTO  student_history (round_id,student_id,bus_check_in,datetime,history_id,lat,long,activity_type) VALUES (%s,%s,%s,%s,%s,%s,%s,%s); ",
                                                [round_id, student_id, datetime.datetime.now(),
                                                 datetime.datetime.now(), round_history[0][0],lat,long,status])

                                cursor.execute(
                                    "select  id  from school_day where name = %s",
                                    [calendar.day_name[curr_date.weekday()]])
                                day_id = cursor.fetchall()
                                cursor.execute(
                                    "select  id from round_schedule WHERE round_id = %s AND day_id =%s ",
                                    [round_id, day_id[0][0]])
                                round_schedule = cursor.fetchall()
                                cursor.execute(
                                    "UPDATE public.transport_participant SET transport_state = %s WHERE student_id =%s AND round_schedule_id= %s",
                                    [status,student_id,round_schedule[0][0]])
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
                    ordered_students_ids=request.data.get('ordered_students_ids')
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
                                for rec in range(len(ordered_students_ids)-1):
                                    student_ids=[]
                                    student_ids.append(ordered_students_ids[rec])
                                    student_ids.append(ordered_students_ids[rec+1])
                                    cursor.execute("select display_name_search from student_student WHERE id in %s",
                                                   [tuple(student_ids)])
                                    student_transferred = cursor.fetchall()

                                    message_en='The driver '+driver_id[0][0]+' has changed the planed route of the round '+round_info[0][0]+'.The driver' +round_info[0][2]+' the student '+student_transferred[0][0]+' before the student'+student_transferred[1][0]+' .'
                                    date_string = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                    r = datetime.datetime.strptime(date_string, '%Y-%m-%d %H:%M:%S')
                                    cursor.execute(
                                        "INSERT INTO sh_message_wizard(create_date,from_type, type, message_en,sender_name)VALUES (%s,%s,%s,%s,%s);",
                                        [r, 'App\Model\Driver', 'route_changed', message_en, driver_id[0][0]])

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
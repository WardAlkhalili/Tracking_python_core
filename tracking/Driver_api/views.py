from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import *
from django.db import connections
from django.http.response import Http404,JsonResponse
from django.http import HttpResponse
from django.core.serializers import serialize
from collections import ChainMap
from rest_framework import status
from itertools import chain
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
# Create your views here.


@api_view(['POST'])
def driver_login(request):

    if request.method == 'POST':
        pincode = request.data.get('pincode')
        school_name = Manager.pincode(pincode)
    

        
        with connections[school_name].cursor() as cursor:
            cursor.execute("select  driver_id,bus_no,id  from fleet_vehicle WHERE bus_pin = %s",[pincode])
            columns = (x.name for x in cursor.description)
            data_id_bus = cursor.fetchall()


            cursor.execute("select name from res_partner WHERE id = %s",[data_id_bus[0][0]])    
            columns1 = (x.name for x in cursor.description)        
            driver_name = cursor.fetchall()


            cursor.execute("select id,name from transport_round WHERE driver_id = %s",[data_id_bus[0][0]])    
            columns2 = (x.name for x in cursor.description)        
            rounds_name = cursor.fetchall()


            # Authentication
            user = User.objects.all().first()
            token_auth, created = Token.objects.get_or_create(user=user)
            manager = Manager(token=token_auth,db_name=school_name,driver_id=data_id_bus[0][0])
            manager.save()

            # *------------------------------------------------------------------------------------------------*
            # Details for login setting
            
            cursor.execute("""
            
            select nearby_distance,lat,lng,battery_low,location_refresh_rate,timezone,utc_offset,speed_limit_watch,standstill_watch,notify_if_driver_check_in_out_geo_fence,notify_on_battery_low_of_drivers_app,notify_it_driver_turns_off_gps,user_speed_exceeded,user_no_move_time_exceeded from transport_setting ORDER BY ID DESC LIMIT 1
            
            """)    
            columns = (x.name for x in cursor.description)        
            login_details = cursor.fetchall()

            cursor.execute('select name,phone  from  res_company')
            columns_login = (x.name for x in cursor.description)
            company_login_info = cursor.fetchall()




            # *------------------------------------------------------------------------------------------------*
            cursor.execute("select id,round_id,day_id from round_schedule WHERE round_id = %s",[rounds_name[0][0]])    
            columns3 = (x.name for x in cursor.description)        
            rounds_details = cursor.fetchall()

            
            cursor.execute("select count(student_id) from transport_participant WHERE round_schedule_id = %s",[rounds_name[0][0]])    
            columns4 = (x.name for x in cursor.description)        
            rounds_count_student = cursor.fetchall()
            

            day_list=[]
            for x,y,z in rounds_details:  
                cursor.execute("select  name  from school_day where id = %s",[z])    
                columns5 = (x.name for x in cursor.description)
                day_name = cursor.fetchall()
                day_list.append(list(day_name))
           
            # *------------------------------------------------------------------------------------------------*
            # 1-List of active round
        
            cursor.execute("select  id,name  from transport_round WHERE is_active = %s",[True])
            columns = (x.name for x in cursor.description)
            active_round_list = cursor.fetchall()
            active_round_list=str(active_round_list)[1:-1]

            
            # 2-A student transferred to another round
            cursor.execute("select  student_id,source_round_id  from transport_participant WHERE source_round_id IS NOT %s",[None])
            columns = (x.name for x in cursor.description)
            student_transferred = cursor.fetchall()
            student_transferred_list = str(student_transferred)[1:-1]


            student_name_transferred = []
            for x,y in student_transferred:
                cursor.execute("select id,display_name_search from student_student WHERE id = %s",[x])
                columns = (x.name for x in cursor.description)
                student_transferred = cursor.fetchall()
                student_name_transferred.append(list(student_transferred))
            
            student_name_transferred_list = str(student_name_transferred)[1:-1]

            result = {
                    'status':'ok',
                    'school_phone': company_login_info[0][1],
                    'school_name': company_login_info[0][0],
                    'school_db': school_name,
                    'school_id': None,
                    'nearby_distance ' : login_details[0][0],
                    'school_lat' : login_details[0][1],
                    'school_lng': login_details[0][2],
                    'location_refresh_rate':login_details[0][4],
                    'timezone':login_details[0][5],
                    'utc_offset':login_details[0][6],
                    'bus_id':data_id_bus[0][2],
                    'bus_number': [1][0],
                    'driver_id': data_id_bus[0][0],
                    
                    'notifications_settings':
                    {
                    'speed_limit_watch':login_details[0][7],
                    'standstill_watch': login_details[0][8],
                    'notify_if_driver_check_in_out_geo_fence':login_details[0][9],
                    'notify_on_battery_low_of_drivers_app': login_details[0][10],
                    'notify_it_driver_turns_off_gps':login_details[0][11]},

                    'notifications_thresholds':{
                        'battery_low':login_details[0][3],
                        'user_speed_exceeded':login_details[0][12],
                        'user_no_move_time_exceeded':login_details[0][13]
                    },

                    "notifications_text":[
                        {
                        "type": "drop-off",
                        "actions": {
                            "near_by_ar": " @student_name على وصول الى المنزل",
                            "no-show_ar": "الطالب @student_name لم يصعد للحافلة في الجولة @rounds_name ",
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

                            "geofenses": [],

                            'token': token_auth.key,


            }

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
"pincode":"iksW6O4MR"
}    

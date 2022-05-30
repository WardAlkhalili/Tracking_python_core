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

@api_view(['GET', 'POST'])
def round_list(request):
    if request.method == 'GET':
        result = {"status": "error"
                  }

        return Response(result)
    if request.method == 'POST':
        if request.headers:
            if request.headers.get('Authorization'):
                if 'Bearer' in request.headers.get('Authorization'):
                    au=request.headers.get('Authorization').replace('Bearer','').strip()
                    db_name=Manager.objects.filter(token=au).values_list('db_name')
                    if db_name:
                        for e in db_name:
                            school_name = e[0]
                        with connections[school_name].cursor() as cursor:
                            cursor.execute(
                                "select name,start_time,pick_up_address,drop_off_address,pick_up_lat,pick_up_lng,drop_off_lat,drop_off_lng,route_id,id from transport_round WHERE vehicle_id = %s and  type = %s",
                                [request.data.get('bus_id'), request.data.get('round_type')])
                            columns = (x.name for x in cursor.description)
                            list_round = cursor.fetchall()
                            result1 = {}
                            round = []
                            for rec in range(len(list_round)):
                                cursor.execute("select id,day_id from round_schedule WHERE round_id = %s", [list_round[rec][9]])
                                columns3 = (x.name for x in cursor.description)
                                rounds_details = cursor.fetchall()
                                day_list = {}
                                for z in rounds_details:
                                    cursor.execute("select  name  from school_day where id = %s", [z[1]])
                                    columns5 = (x.name for x in cursor.description)
                                    day_name = cursor.fetchall()

                                    cursor.execute("select student_id from transport_participant WHERE round_schedule_id = %s",
                                                   [z[0]])
                                    columns4 = (x.name for x in cursor.description)
                                    rounds_count_student = cursor.fetchall()
                                    st_id = []
                                    for k in rounds_count_student:
                                        st_id.append(k[0])
                                    cursor.execute("select display_name_search from student_student WHERE id in %s",
                                                   [tuple(st_id)])
                                    columns4 = (x.name for x in cursor.description)
                                    student_student = cursor.fetchall()
                                    student_name = []
                                    for name in student_student:
                                        student_name.append(name[0])

                                    day_list[day_name[0][0]] = student_name

                                result1[rec] = {

                                    "start_time": list_round[rec][1],
                                    'name ': list_round[rec][0],
                                    "date": None,
                                    "pick_up_address": list_round[rec][2],
                                    "drop_off_address": list_round[rec][3],
                                    "pick_up_lat": list_round[rec][4] if list_round[rec][4] else 0,
                                    "pick_up_lng": list_round[rec][5] if list_round[rec][5] else 0,
                                    "drop_off_lat": list_round[rec][6] if list_round[rec][6] else 0,
                                    "drop_off_lng": list_round[rec][7] if list_round[rec][7] else 0,
                                    "route_id": list_round[rec][8],
                                    "round_canceled": False,
                                    "round_ended": False,
                                    "round_started": False,
                                    "geofenses": {
                                        "id": 1,
                                        "name": 1,
                                        "shape_type": "polygon",
                                        "shape_attrs": {
                                            "vertices": []
                                        }},
                                    "round_id": list_round[rec][9],
                                    "moved_students": [],
                                    "students_list": day_list

                                }
                            for rec in range(len(result1)):
                                round.append(result1[rec])
                            cursor.execute("""
            
                                                       select 	allow_driver_change_students_location,allow_driver_to_use_beacon from transport_setting ORDER BY ID DESC LIMIT 1
            
                                                       """)
                            columns2 = (x.name for x in cursor.description)
                            login_details = cursor.fetchall()
                            result = {"school_settings": {
                                'change_student_location ': login_details[0][0],
                                'allow_driver_to_use_beacon': login_details[0][1],

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
def student_list(request,round_id):
    if request.method == 'GET':
        if request.headers:
            if request.headers.get('Authorization'):
                if 'Bearer' in request.headers.get('Authorization'):
                    au=request.headers.get('Authorization').replace('Bearer','').strip()
                    db_name=Manager.objects.filter(token=au).values_list('db_name')
                    if db_name:
                        for e in db_name:
                            school_name = e[0]
                        # school_name = Manager.pincode('iksQQQ')
                        with connections[school_name].cursor() as cursor:
                            import datetime
                            now = datetime.datetime.now()
                            cursor.execute("select  id  from school_day where name = %s", [now.strftime("%A")])
                            columns5 = (x.name for x in cursor.description)
                            day_name = cursor.fetchall()
                            cursor.execute("select id,day_id from round_schedule WHERE round_id = %s and day_id = %s", [round_id,day_name[0][0]])
                            columns3 = (x.name for x in cursor.description)
                            rounds_details = cursor.fetchall()
                            day_list = {}
                            for z in rounds_details:
                                cursor.execute("select student_id from transport_participant WHERE round_schedule_id = %s",
                                               [z[0]])
                                columns4 = (x.name for x in cursor.description)
                                rounds_count_student = cursor.fetchall()

                            st_id=[]
                            for k in rounds_count_student:
                                st_id.append(k[0])
                            cursor.execute("select * from student_student WHERE id in %s",
                                           [tuple(st_id)])
                            columns4 = (x.name for x in cursor.description)
                            student_student = cursor.fetchall()
                            s=[ dict(zip(columns4, row))for row in student_student]
                            student_info = {}
                            for std in range(len(s)):

                                if s[std]:
                                    cursor.execute("select * from school_parent WHERE id = %s",
                                                   [s[std]['father_id']])
                                    columns_f = (x.name for x in cursor.description)
                                    father = cursor.fetchall()
                                    father_inf = [dict(zip(columns_f, row)) for row in father]
                                    cursor.execute("select * from school_parent WHERE id = %s",
                                                   [s[std]['mother_id']])
                                    columns_m = (x.name for x in cursor.description)
                                    mother = cursor.fetchall()
                                    mother_inf = [dict(zip(columns_m, row)) for row in mother]

                                    student_info[std]={
                                        "id": s[std]['id'],
                                        "year_id": s[std]['year_id'],
                                        "emergency_call": s[std]['emergency_call'],
                                        "display_name_search": s[std]['display_name_search'],
                                        "user_id": s[std]['user_id'],
                                        "color": s[std]['color'],
                                        "email": s[std]['email'],
                                        "mobile": s[std]['mobile'],
                                        "name":s[std]['name'],
                                        "contact_phone1": s[std]['contact_phone1'],
                                        "contact_mobile1": s[std]['contact_mobile1'],
                                        "nationality_id": s[std]['nationality_id'],
                                        "admission_date": s[std]['admission_date'],
                                        "second_name": s[std]['second_name'],
                                        "third_name": s[std]['third_name'],
                                        "last_name": s[std]['last_name'],
                                        "mother_tongue": s[std]['mother_tongue'],
                                        "blood_group": s[std]['blood_group'],
                                        "date_of_birth": s[std]['date_of_birth'],
                                        "building_number": s[std]['building_number'],
                                        "building_name": s[std]['building_name'],
                                        "street": s[std]['street'],
                                        "flat_number": s[std]['flat_number'],
                                        "area_id": s[std]['area_id'],
                                        "state_id": s[std]['state_id'],
                                        "address_note": s[std]['address_note'],
                                        "terminate_reason": s[std]['terminate_reason'],
                                        "terminate_date": s[std]['terminate_date'],
                                        "alumni_date": s[std]['alumni_date'],
                                        "national_id": s[std]['national_id'],
                                        "passport_number": s[std]['passport_number'],
                                        "religion_id": s[std]['religion_id'],
                                        "country_id": s[std]['country_id'],
                                        "id_number":s[std]['id_number'],
                                        "is_demo": s[std]['is_demo'],
                                        "birth_certificate_no": s[std]['birth_certificate_no'],
                                        "issued_at": s[std]['issued_at'],
                                        "issue_date": s[std]['issue_date'],
                                        "previous_year_avg": s[std]['previous_year_avg'],
                                        "learning_disabilities": s[std]['learning_disabilities'],
                                        "need_attention": s[std]['need_attention'],
                                        "attention_follow_up_notes": s[std]['attention_follow_up_notes'],
                                        "special_needs": s[std]['special_needs'],
                                        "health_condition_notes": s[std]['health_condition_notes'],
                                        "allergies": s[std]['allergies'],
                                        "allergies_desc": s[std]['allergies_desc'],
                                        "bus_number": s[std]['bus_number'],
                                        "state": s[std]['state'],
                                        "father_id": s[std]['father_id'],
                                        "mother_id": s[std]['mother_id'],
                                        "family_relation_id": s[std]['family_relation_id'],
                                        "message_main_attachment_id": s[std]['message_main_attachment_id'],
                                        "create_uid": s[std]['create_uid'],
                                        "create_date": s[std]['create_date'],
                                        "write_uid": s[std]['write_uid'],
                                        "write_date": s[std]['write_date'],
                                        "is_banned": s[std]['is_banned'],
                                        "currency_id": s[std]['currency_id'],
                                        "name_ar": s[std]['name_ar'],
                                        "second_name_ar": s[std]['second_name_ar'],
                                        "third_name_ar": s[std]['third_name_ar'],
                                        "last_name_ar": s[std]['last_name_ar'],
                                        "display_name_ar": s[std]['display_name_ar'],
                                        "moe_grace_period": s[std]['moe_grace_period'],
                                        "deadline_date": s[std]['deadline_date'],
                                        "neighborhood_id": s[std]['neighborhood_id'],
                                        "assembly_id": s[std]['assembly_id'],
                                        "ministry_state_id": s[std]['ministry_state_id'],
                                        "student_emis_no": s[std]['student_emis_no'],
                                        "family_members": s[std]['family_members'],
                                        "borthers": s[std]['borthers'],
                                        "sisters": s[std]['sisters'],
                                        "soas": s[std]['soas'],
                                        "marital_state": s[std]['marital_state'],
                                        "education": s[std]['education'],
                                        "external_financial_aid": s[std]['external_financial_aid'],
                                        "aid_type": s[std]['aid_type'],
                                        "international_refugee_card_status": s[std]['international_refugee_card_status'],
                                        "district_id": s[std]['district_id'],
                                        "province_id": s[std]['province_id'],
                                        "partner_id": s[std]['partner_id'],
                                        "book_requests": s[std]['book_requests'],
                                        "country_of_birth": s[std]['country_of_birth'],
                                        "city_of_birth": s[std]['city_of_birth'],
                                        "file_name": s[std]['file_name'],
                                        "pickup_by_parent": s[std]['pickup_by_parent'],
                                        "dropoff_by_parent": s[std]['dropoff_by_parent'],
                                        "area_ids": s[std]['area_ids'],
                                        "round_type": s[std]['round_type'],
                                        "contact_person": s[std]['contact_person'],
                                        "family_relation": s[std]['family_relation'],
                                        "contact_person_number": s[std]['contact_person_number'],
                                        "round_address_type":  s[std]['round_address_type'],
                                        "pick_up_type": s[std]['pick_up_type'],
                                        "drop_off_type":s[std]['drop_off_type'],
                                        "second_pickup_address": s[std]['second_pickup_address'],
                                        "second_dropoff_address": s[std]['second_dropoff_address'],
                                        "dropoff_as_pickup": s[std]['dropoff_as_pickup'],
                                        "same_as_address": s[std]['same_as_address'],
                                        "pickup_building_number": s[std]['pickup_building_number'],
                                        "pickup_building_name": s[std]['pickup_building_name'],
                                        "pickup_street": s[std]['pickup_street'],
                                        "pickup_flat_number": s[std]['pickup_flat_number'],
                                        "pickup_area_id": s[std]['pickup_area_id'],
                                        "pickup_state_id": s[std]['pickup_state_id'],
                                        "pickup_address_note": s[std]['pickup_address_note'],
                                        "sec_pickup_building_number": s[std]['sec_pickup_building_number'],
                                        "sec_pickup_building_name": s[std]['sec_pickup_building_name'],
                                        "sec_pickup_street": s[std]['sec_pickup_street'],
                                        "sec_pickup_flat_number": s[std]['sec_pickup_flat_number'],
                                        "sec_pickup_area_id": s[std]['sec_pickup_area_id'],
                                        "sec_pickup_state_id": s[std]['sec_pickup_state_id'],
                                        "sec_pickup_address_note": s[std]['sec_pickup_address_note'],
                                        "dropoff_building_number": s[std]['dropoff_building_number'],
                                        "dropoff_building_name": s[std]['dropoff_building_name'],
                                        "dropoff_street": s[std]['dropoff_street'],
                                        "dropoff_flat_number": s[std]['dropoff_flat_number'],
                                        "dropoff_area_id": s[std]['dropoff_area_id'],
                                        "dropoff_state_id": s[std]['dropoff_state_id'],
                                        "dropoff_address_note": s[std]['dropoff_address_note'],
                                        "sec_dropoff_building_number": s[std]['sec_dropoff_building_number'],
                                        "sec_dropoff_building_name": s[std]['sec_dropoff_building_name'],
                                        "sec_dropoff_street": s[std]['sec_dropoff_street'],
                                        "sec_dropoff_flat_number": s[std]['sec_dropoff_flat_number'],
                                        "sec_dropoff_area_id": s[std]['sec_dropoff_area_id'],
                                        "sec_dropoff_state_id": s[std]['sec_dropoff_state_id'],
                                        "sec_dropoff_address_note": s[std]['sec_dropoff_address_note'],
                                        "is_suspended": s[std]['is_suspended'],
                                        "sequence": s[std]['sequence'],
                                        "password": s[std]['password'],
                                        "image_url": s[std]['image_url'],
                                        "round_id": s[std]['round_id'],
                                        "responsible_id_value": s[std]['responsible_id_value'],
                                        "first_mandatory": s[std]['first_mandatory'],
                                        "second_mandatory": s[std]['second_mandatory'],
                                        "third_mandatory": s[std]['third_mandatory'],
                                        "last_mandatory": s[std]['last_mandatory'],
                                        "section_id_value": s[std]['section_id_value'],
                                        # "laravel_through_key": s[std]['laravel_through_key'],
                                        "parents_info": [
                                            {
                                                "father": {
                                                    "mobile_token": father_inf[0]['mobile_token']if father_inf else "",
                                                    # "mobile_pn_registration_id": father_inf[0]['mobile_pn_registration_id']if father_inf else "",
                                                    # "invite_count": father_inf[0]['invite_count']if father_inf else "",
                                                    "settings": father_inf[0]['settings']if father_inf else "",
                                                    "number": father_inf[0]['mobile']if father_inf else "",
                                                    "id": father_inf[0]['id']if father_inf else -1

                                                },
                                                "mother": {
                                                    "mobile_token": mother_inf[0]['mobile_token']if mother_inf else "",
                                                    # "mobile_pn_registration_id": mother_inf[0]['mobile_pn_registration_id']if mother_inf else"",
                                                    # "invite_count": mother_inf[0]['invite_count']if mother_inf else"",
                                                    "settings":mother_inf[0]['settings']if mother_inf else "",
                                                # {
                                                    #     "notifications": {
                                                    #         "locale": "ar",
                                                    #         "nearby": false,
                                                    #         "check_in": false,
                                                    #         "check_out": false
                                                    #     }
                                                    # },
                                                    "number":mother_inf[0]['mobile'] if mother_inf else "",
                                                    "id":mother_inf[0]['id']if mother_inf else -1
                                                }
                                            }
                                        ],
                                    }

                                result = {"students_list": student_info
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
                                        [tuple(transport_rounds),day_count])
                                    round_schedule = cursor.fetchall()
                                    round_schedules = []
                                    for rec in round_schedule:
                                        round_schedules.append(rec[0])
                                    if round_schedules:
                                        cursor.execute(
                                            "select  message_ar,create_date,type from sh_message_wizard WHERE round_id in %s AND sender_name = %s AND from_type='App\Model\Driver' ",
                                            [tuple(round_schedules),driver_name[0][0]])
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
                                cursor.execute(
                                    "UPDATE public.transport_round SET is_active= not(is_active), pick_up_lat=%s ,pick_up_lng=%s ,drop_off_lat=%s ,drop_off_lng=%s WHERE id=%s",
                                    [lat,long,lat,long,round_id])
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

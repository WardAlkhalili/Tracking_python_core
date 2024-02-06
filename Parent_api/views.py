from builtins import str, type

from django.db.models import Q

from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import *
from django.db import connections

from pyfcm import FCMNotification
import pandas as pd
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
import json
import calendar
from datetime import date, timedelta, datetime
import requests
import pytz
import datetime

import urllib.request
import math
import jwt


@api_view(['POST'])
def student_login_uni(request):
    if request.method == 'POST':
        password = request.data.get('password')
        user_name = request.data.get('user_name')
        school_name = request.data.get('school_name')
        mobile_token = request.data.get('mobile_token')
        platform = request.data.get('platform')
        with connections[school_name].cursor() as cursor:
            cursor.execute(
                "select id,name,email,mobile,company_id,lang_app,notif,image_url from res_partner WHERE university_id_number = %s",
                [password])
            student_id = cursor.fetchall()
            result = {

                "status": "user not found",
            }
            if student_id:
                notify = student_id[0][6] if student_id[0][6] else True
                lang_app = student_id[0][5] if student_id[0][5] else 'en'
                result = {

                    "token": mobile_token,
                    "db_name": school_name,
                    "company_id": student_id[0][4] if student_id[0][4] else '',
                    "mobile": student_id[0][3],
                    "uid": student_id[0][0],
                    "lang_app": lang_app,
                    "name": student_id[0][1],
                    "notif": 1 if notify else 0,
                    "image": "https://trackware-schools.s3.eu-central-1.amazonaws.com/" + student_id[0][7],
                }
                token = jwt.encode(
                    payload=result,
                    key='my_secret'
                )
                decoded_data = jwt.decode(jwt=token,
                                          key='my_secret',
                                          algorithms=["HS256"])
                print(decoded_data)
                manager_parent = ManagerStudentUni(token=token, db_name=school_name, user_id=student_id[0][0],
                                                   student_id=student_id[0][0],
                                                   school_id=student_id[0][4], mobile_token=mobile_token)
                manager_parent.save()
                cursor.execute(
                    "UPDATE public.res_partner SET mobile_token=%s,platform=%s,secret_token=%s  WHERE id=%s;",
                    [mobile_token, platform, token, student_id[0][0]])
                result = {
                    "status": "ok",
                    "company_id": student_id[0][4] if student_id[0][4] else '',
                    "uid": student_id[0][0],
                    "token": mobile_token,
                    "db_name": school_name,
                    "lang_app": lang_app,
                    "name": student_id[0][1],
                    "mobile": student_id[0][3],
                    "notif": 1 if notify else 0,
                    "distance":500,
                    "image": "https://trackware-schools.s3.eu-central-1.amazonaws.com/" + student_id[0][7],
                    "Authorization": "Bearer " + token

                }

        return Response(result)




@api_view(['POST'])
def student_profile_uni(request):
    if request.method == 'POST':
        result = {

            "status": "user not found",
        }
        if request.headers:
            if request.headers.get('Authorization'):
                if 'Bearer' in request.headers.get('Authorization'):
                    au = request.headers.get('Authorization').replace('Bearer', '').strip()
                    password = request.data.get('pass')
                    notify = request.data.get('notify')

                    lang = request.data.get('lang')

                    decoded_data = jwt.decode(jwt=au,
                                              key='my_secret',
                                              algorithms=["HS256"])
                    school_name = decoded_data['db_name']
                    student_id = decoded_data['uid']
                    with connections[school_name].cursor() as cursor:
                        if student_id:
                            cursor.execute(
                                "UPDATE public.res_partner SET lang_app=%s,notif=%s  WHERE id=%s;",
                                [lang, notify, student_id])
                            result = {
                                "status": "ok",

                            }

        return Response(result)


@api_view(['POST'])
def Routs_uni(request):
    if request.method == 'POST':
        # result = {
        #
        #     "status": "user not found",
        # }
        # if request.headers:
        # if request.headers.get('Authorization'):
        #     if 'Bearer' in request.headers.get('Authorization'):
        #         au = request.headers.get('Authorization').replace('Bearer', '').strip()
        #
        #         decoded_data = jwt.decode(jwt=au,
        #                                   key='my_secret',
        #                                   algorithms=["HS256"])
        #         school_name = decoded_data['db_name']
        # student_id = decoded_data['uid']
        # transport.route
        lo = [

            [
                {'name': 'ddddd',
                 "id": 1,
                 "time": "7:30",
                 "lat": 32.0039233,
                 "long": 35.834021,
                 "round": [{"name": "111122", "time": "111122", }]

                 },
                {'name': '11111',
                 "id": 2,
                 "time": "7:30",
                 "lat": 32.0080538,
                 "long": 35.8395464,
                 # 32.0080538,35.8395464
                 "round": [{"name": "1222222223", "time": "111122", }]

                 },
                {'name': '222',
                 "id": 3,
                 "time": "7:30",
                 "lat": 32.0077638,
                 "long": 35.8399085,
                 # 32.0077638,35.8399085
                 "round": [{"name": "985555555", "time": "111122", }]

                 },
                {'name': '333',
                 "id": 4,
                 "time": "7:30",
                 "lat": 32.0077496,
                 "long": 35.8397858,
                 # 32.0077496,35.8397858
                 "round": [{"name": "weee", "time": "111122", }]

                 },
                {'name': '444',
                 "id": 5,
                 "time": "7:30",
                 "lat": 32.008176,
                 "long": 35.8397722,
                 # 32.008176,35.8397722
                 "round": [{"name": "weee", "time": "111122", }]
                 },
                {'name': '5555',
                 "id": 6,

                 "time": "7:30",
                 "lat": 32.0051623,
                 "long": 35.8468374,
                 # 32.0051623,35.8468374
                 "round": [{"name": "weee", "time": "111122", }]
                 }
            ],

            [
                {'name': 'ddddd',
                 "id": 1,
                 "time": "7:30",
                 "lat": 32.0316656,
                 "long": 35.7723242,
                 # 32.0316656,35.7723242
                 "round": [{"name": "111122", "time": "111122", }]

                 },
                {'name': '11111',
                 "id": 2,
                 "time": "7:30",
                 "lat": 32.0493359,
                 "long": 35.7536113,
                 # 32.0493359,35.7536113
                 "round": [{"name": "1222222223", "time": "111122", }]

                 },
                {'name': '222',
                 "id": 3,
                 "time": "7:30",
                 "lat": 32.0556425,
                 "long": 35.7505148,
                 # 32.0556425,35.7505148
                 "round": [{"name": "985555555", "time": "111122", }]

                 },
                {'name': '333',
                 "id": 4,
                 "time": "7:30",
                 "lat": 32.0615472,
                 "long": 35.7391802,
                 # 32.0615472,35.7391802
                 "round": [{"name": "weee", "time": "111122", }]

                 },
                {'name': '444',
                 "id": 5,
                 "time": "7:30",
                 "lat": 32.0618116,
                 "long": 35.7300177,
                 # 32.0618116,35.7300177
                 "round": [{"name": "weee", "time": "111122", }]
                 },
                {'name': '5555',
                 "id": 6,

                 "time": "7:30",
                 "lat": 32.0634174,
                 "long": 35.7214676,
                 # 32.0634174,35.7214676
                 "round": [{"name": "weee", "time": "111122", }]
                 }
            ],

            [{'name': 'ddddd',
              "id": 1,
              "time": "7:30",
              "lat": 32.0039233,
              "long": 35.834021,
              "round": [{"name": "111122", "time": "111122", }]

              },
             {'name': '11111',
              "id": 2,
              "time": "7:30",
              "lat": 32.0080538,
              "long": 35.8395464,

              "round": [{"name": "1222222223", "time": "111122", }]

              },
             {'name': '222',
              "id": 3,
              "time": "7:30",
              "lat": 32.0077638,
              "long": 35.8399085,
              # 32.0077638,35.8399085
              "round": [{"name": "985555555", "time": "111122", }]

              },
             {'name': '333',
              "id": 4,
              "time": "7:30",
              "lat": 32.0077496,
              "long": 35.8397858,
              # 32.0077496,35.8397858
              "round": [{"name": "weee", "time": "111122", }]

              },
             {'name': '444',
              "id": 5,
              "time": "7:30",
              "lat": 32.008176,
              "long": 35.8397722,
              # 32.008176,35.8397722
              "round": [{"name": "weee", "time": "111122", }]
              },
             {'name': '5555',
              "id": 6,

              "time": "7:30",
              "lat": 32.0051623,
              "long": 35.8468374,
              # 32.0051623,35.8468374
              "round": [{"name": "weee", "time": "111122", }]
              }
             ],

            [{'name': 'ddddd',
              "id": 1,
              "time": "7:30",
              "lat": 32.0039233,
              "long": 35.834021,
              "round": [{"name": "111122", "time": "111122", }]

              },
             {'name': '11111',
              "id": 2,
              "time": "7:30",
              "lat": 32.0080538,
              "long": 35.8395464,
              # 32.0080538,35.8395464
              "round": [{"name": "1222222223", "time": "111122", }]

              },
             {'name': '222',
              "id": 3,
              "time": "7:30",
              "lat": 32.0077638,
              "long": 35.8399085,
              # 32.0077638,35.8399085
              "round": [{"name": "985555555", "time": "111122", }]

              },
             {'name': '333',
              "id": 4,
              "time": "7:30",
              "lat": 32.0077496,
              "long": 35.8397858,
              # 32.0077496,35.8397858
              "round": [{"name": "weee", "time": "111122", }]

              },
             {'name': '444',
              "id": 5,
              "time": "7:30",
              "lat": 32.008176,
              "long": 35.8397722,
              # 32.008176,35.8397722
              "round": [{"name": "weee", "time": "111122", }]
              },
             {'name': '5555',
              "id": 6,

              "time": "7:30",
              "lat": 32.0051623,
              "long": 35.8468374,
              # 32.0051623,35.8468374
              "round": [{"name": "weee", "time": "111122", }]
              }
             ]

        ]
        with connections['tst'].cursor() as cursor:
            from_stations = []
            from_university = []
            cursor.execute(
                "select id,name from transport_route",
                [])
            all_route = cursor.fetchall()
            for rec in range(len(all_route)):
                from_university.append({
                    "name": all_route[rec][1],
                    "id": all_route[rec][0],
                    "station_rout": lo[rec],
                })

                # cursor.execute(
                #     "select name from round_station WHERE id = %s",
                #     [st[0]])
                # station = cursor.fetchall()
                # cursor.execute(
                #     "select id,name,start_time,type from transport_round WHERE route_id = %s",
                #     [rec[0]])
                # all_round = cursor.fetchall()
                # for res in all_round:
                #     cursor.execute(
                #         "select station_id from round_schedule WHERE round_id = %s",
                #         [res[0]])
                #     all_st = cursor.fetchall()

            station = []
            station.append({"result": lo})
            result = {
                "from_stations": from_university,
                # "station": station,
            }

        return Response(result)





@api_view(['POST'])
def parent_login(request):
    if request.method == 'POST':
        password = request.data.get('password')
        user_name = request.data.get('user_name')
        school_name = request.data.get('school_name')
        mobile_token = request.data.get('mobile_token')
        # http://192.168.1.82/
        url = 'https://tst.tracking.trackware.com/web/session/authenticate'
        # url = 'http://192.168.1.82:9098/web/session/authenticate'
        try:

            body = json.dumps(
                {"jsonrpc": "2.0", "params": {"db": school_name, "login": user_name, "password": password}})

            headers = {
                'Content-Type': 'application/json',
            }

            response1 = requests.request("POST", url, headers=headers, data=body)

            response = response1.json()
            # print(response)
            if "error" in response:
                result = {
                    "status": "erorrq"}
                return Response(result)
            session = response1.cookies
            uid = response['result']['uid']
            company_id = response['result']['company_id']

        except Exception  as error:
            # print("--------------------------------------")
            # print(Exception)
            result = {
                "status": "erorr2"
                          ""}
            return Response(result)
        with connections[school_name].cursor() as cursor:
            cursor.execute("select id from school_parent WHERE user_id = %s", [response['result']['uid']])
            parent_id = cursor.fetchall()
            user = User.objects.all().first()
            user = User.objects.all().first()

            token_auth, created = Token.objects.get_or_create(user=user)
            from django.utils.crypto import get_random_string
            unique_id = get_random_string(length=32)

            ManagerParent.objects.filter(parent_id=parent_id[0][0], db_name=school_name, user_id=uid).update(
                is_active=False)

            cursor.execute(
                "UPDATE public.school_parent SET mobile_token=%s WHERE id=%s;",
                [mobile_token, parent_id[0][0]])
            # print("sdasadsa",  parent_id[0][0],"           ",mobile_token)
            manager_parent = ManagerParent(token=unique_id, db_name=school_name, user_id=uid,
                                           parent_id=parent_id[0][0],
                                           school_id=company_id, mobile_token=mobile_token)
            manager_parent.save()
            result = {
                "status": "ok",
                "kids": [],
                "notifications_text": [
                    {
                        "type": "drop-off",
                        "actions": [
                            {
                                "no-show": "@student_name did not show today in @round_name",
                                "check_in": "@student_name just checked into the bus @bus_num",
                                "check_out": "@student_name just reached home."
                            }
                        ]
                    },
                    {
                        "type": "pick-up",
                        "actions": [
                            {
                                "absent": "@student_name is absent today",
                                "check_in": "@student_name just checked into the bus @bus_num",
                                "check_out": "@student_name just reached the school",
                                "near_by": "You are next in route. Please have @student_name ready"
                            }
                        ]
                    }
                ],
                "uid": uid,
                "session_id": session.get_dict()['session_id'],
                "web_base_url": response['result']['web_base_url'],
                "Authorization": "Bearer " + unique_id}

        return Response(result)


@api_view(['POST', 'GET'])
def feed_back(request):
    if request.method == 'POST':
        if request.headers:
            if request.headers.get('Authorization'):
                if 'Bearer' in request.headers.get('Authorization'):
                    au = request.headers.get('Authorization').replace('Bearer', '').strip()
                    db_name = ManagerParent.objects.filter(token=au).values_list('db_name')
                    parent_id = ManagerParent.objects.filter(token=au).values_list('parent_id')
                    for e in parent_id:
                        parent_id = e[0]
                    if db_name:
                        for e in db_name:
                            school_name = e[0]
                        school_name = ManagerParent.pincode(school_name)
                        student_id = request.data.get('student_id')
                        feed_back = request.data.get('feed_back')
                        impression = request.data.get('impression')

                        # school_name = ManagerParent.pincode('iks')
                        impression1 = 3
                        if impression == "Good":

                            impression1 = 1
                        elif impression in "Very Good":
                            impression1 = 2
                        elif impression in "Excellent":
                            impression1 = 3
                        with connections[school_name].cursor() as cursor:
                            cursor.execute(
                                "INSERT INTO feed_back(model_id, model_type, feed_back, impression, student_id)VALUES (%s, %s,%s,%s,%s);",
                                [25, 'App\Model\Parents', feed_back, impression1, student_id])
                            result = {
                                'status': 'ok', }
                            return Response(result)
                    else:
                        result = {'result': 'error'}
                        return Response(result)
                else:
                    result = {'result': 'error'}
                    return Response(result)
            else:
                result = {'result': 'error'}
                return Response(result)
        else:
            result = {'result': 'error'}
            return Response(result)
    elif request.method == 'GET':
        result = {'status': 'error'}
        return Response(result)


@api_view(['POST', 'GET'])
def settings(request):
    if request.method == 'POST':
        if request.headers:
            if request.headers.get('Authorization'):
                if 'Bearer' in request.headers.get('Authorization'):
                    au = request.headers.get('Authorization').replace('Bearer', '').strip()
                    db_name = ManagerParent.objects.filter(token=au).values_list('db_name')
                    parent_id = ManagerParent.objects.filter(token=au).values_list('parent_id')

                    for e in parent_id:
                        parent_id = e[0]
                    if db_name:
                        for e in db_name:
                            school_name = e[0]
                        school_name = ManagerParent.pincode(school_name)
                        notifications = request.data

                        # school_name = ManagerParent.pincode('iks')
                        with connections[school_name].cursor() as cursor:

                            y = json.dumps(notifications['notifications'])

                            settings = "{\"notifications\":" + y + "}"

                            cursor.execute(
                                "UPDATE public.school_parent SET settings=%s WHERE id=%s;",
                                [settings, parent_id])

                            result = {
                                'status': 'ok', }

                            return Response(result)
                    else:
                        result = {'result': 'error1'}
                        return Response(result)
                else:
                    result = {'result': 'error2'}
                    return Response(result)
            else:
                result = {'result': 'error3'}
                return Response(result)
        else:
            result = {'result': 'error4'}
            return Response(result)
    elif request.method == 'GET':
        if request.headers:
            if request.headers.get('Authorization'):
                if 'Bearer' in request.headers.get('Authorization'):
                    au = request.headers.get('Authorization').replace('Bearer', '').strip()
                    db_name = ManagerParent.objects.filter(token=au).values_list('db_name')
                    parent_id = ManagerParent.objects.filter(token=au).values_list('parent_id')
                    for e in parent_id:
                        parent_id = e[0]
                    if db_name:
                        for e in db_name:
                            school_name = e[0]
                        school_name = ManagerParent.pincode(school_name)
                        # school_name = ManagerParent.pincode('iks')
                        with connections[school_name].cursor() as cursor:
                            cursor.execute("select  settings from school_parent WHERE id = %s", [parent_id])
                            data_id_bus = cursor.fetchall()

                            if data_id_bus[0][0]:

                                data = json.loads(data_id_bus[0][0])

                                if type(data['notifications']) is str:
                                    li = list(data['notifications'].split(","))
                                    result = {
                                        "notifications": {
                                            "locale": "ar" if "ar" in li[3] else 'en',
                                            "nearby": True if "true" in li[0] else False,
                                            "check_in": True if "true" in li[1] else False,
                                            "check_out": True if "true" in li[2] else False
                                        }
                                    }
                                elif type(data['notifications']) is dict:
                                    result = {
                                        "notifications": {
                                            "locale": data['notifications']['locale'],
                                            "nearby": data['notifications']['nearby'],
                                            "check_in": data['notifications']['check_in'],
                                            "check_out": data['notifications']['check_out']
                                        }
                                    }
                                else:
                                    result = {"notifications": {}}

                                return Response(result)
                            result = {'status': 'Empty'}
                            return Response(result)
                    else:
                        result = {'result': 'error'}
                        return Response(result)
                else:
                    result = {'result': 'error'}

                    return Response(result)
            else:
                result = {'result': 'error'}
                return Response(result)
        else:
            result = {'result': 'error'}
            return Response(result)


@api_view(['POST', 'GET'])
def student_served(request):
    if request.method == 'POST':
        if request.headers:
            if request.headers.get('Authorization'):
                if 'Bearer' in request.headers.get('Authorization'):
                    au = request.headers.get('Authorization').replace('Bearer', '').strip()
                    db_name = ManagerParent.objects.filter(token=au).values_list('db_name')
                    parent_id = ManagerParent.objects.filter(token=au).values_list('parent_id')
                    for e in parent_id:
                        parent_id = e[0]
                    if db_name:
                        for e in db_name:
                            school_name = e[0]
                        school_name = ManagerParent.pincode(school_name)
                        round_id = request.data.get('round_id')
                        student_id = request.data.get('student_id')
                        datetime_c = datetime.datetime.now()
                        # school_name = ManagerParent.pincode('iks')
                        with connections[school_name].cursor() as cursor:
                            cursor.execute(
                                "select  activity_type from student_history WHERE round_id = %s AND student_id = %s AND datetime = %s ",
                                [round_id, student_id, datetime_c])
                            student_served = cursor.fetchall()
                            if student_served:
                                if student_served[0][0] == "out-school" or student_served[0][0] == "out":
                                    result = {'result': True}
                                    return Response(result)
                            result = {'result': False}
                            return Response(result)
                    else:
                        result = {'result': 'error'}
                        return Response(result)
                else:
                    result = {'result': 'error'}
                    return Response(result)
            else:
                result = {'result': 'error'}
                return Response(result)
        else:
            result = {'result': 'error'}
            return Response(result)
    elif request.method == 'GET':
        result = {'status': 'error'}
        return Response(result)


@api_view(['POST', 'GET'])
def student_pick_up(request):
    if request.method == 'POST':
        if request.headers:
            if request.headers.get('Authorization'):
                if 'Bearer' in request.headers.get('Authorization'):
                    au = request.headers.get('Authorization').replace('Bearer', '').strip()
                    db_name = ManagerParent.objects.filter(token=au).values_list('db_name')
                    parent_id = ManagerParent.objects.filter(token=au).values_list('parent_id')
                    for e in parent_id:
                        parent_id = e[0]
                    if db_name:
                        for e in db_name:
                            school_name = e[0]

                        school_name = ManagerParent.pincode(school_name)

                        status = request.data.get('status')
                        student_id = request.data.get('student_id')
                        with connections[school_name].cursor() as cursor:
                            cursor.execute("select  display_name_search from student_student WHERE id = %s",
                                           [student_id])
                            student_name = cursor.fetchall()
                            cursor.execute(
                                "select  id,date,state from pickup_request WHERE name = %s AND parent_id = %s ORDER BY ID DESC LIMIT 1",
                                [student_name[0][0], parent_id])
                            date_t = cursor.fetchall()

                            if date_t:
                                if not (date_t[0][1].strftime('%Y-%m-%d') == datetime.datetime.now().strftime(
                                        '%Y-%m-%d')):
                                    date_string = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                    r = datetime.datetime.strptime(date_string, '%Y-%m-%d %H:%M:%S')

                                    cursor.execute(
                                        "INSERT INTO  pickup_request (date,name,pick_up_by,source,state,parent_id,create_date,write_date) VALUES (%s,%s,%s,%s,%s,%s,%s,%s); ",
                                        [r, student_name[0][0], 'family_member', 'app', 'draft', parent_id, r, r])
                                    cursor.execute(
                                        "select  id from pickup_request WHERE name = %s AND parent_id = %s ORDER BY ID DESC LIMIT 1",
                                        [student_name[0][0], parent_id])
                                    pickup_id = cursor.fetchall()
                                    cursor.execute(
                                        "INSERT INTO  pickup_request_student_student_rel (pickup_request_id,student_student_id) VALUES (%s,%s); ",
                                        [pickup_id[0][0], student_id])
                                    result = {'result': True}

                                    return Response(result)
                                else:
                                    if date_t[0][2] == 'waiting':
                                        cursor.execute(
                                            "UPDATE public.pickup_request SET state=%s WHERE id=%s;",
                                            ['done', date_t[0][0]])
                                        result = {'result': True}
                                        return Response(result)
                                    elif date_t[0][2] == 'draft':
                                        result = {'status': 'error'}
                                        return Response(result)
                                    elif date_t[0][2] == 'done':
                                        result = {'status': 'error'}
                                        return Response(result)
                            else:
                                date_string = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                r = datetime.datetime.strptime(date_string, '%Y-%m-%d %H:%M:%S')

                                cursor.execute(
                                    "INSERT INTO  pickup_request (date,name,pick_up_by,source,state,parent_id,create_date,write_date) VALUES (%s,%s,%s,%s,%s,%s,%s,%s); ",
                                    [r, student_name[0][0], 'family_member', 'app', 'draft', parent_id, r, r])
                                cursor.execute(
                                    "select  id from pickup_request WHERE name = %s AND parent_id = %s ORDER BY ID DESC LIMIT 1",
                                    [student_name[0][0], parent_id])
                                pickup_id = cursor.fetchall()
                                cursor.execute(
                                    "INSERT INTO  pickup_request_student_student_rel (pickup_request_id,student_student_id) VALUES (%s,%s); ",
                                    [pickup_id[0][0], student_id])
                                result = {'result': True}
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

    elif request.method == 'GET':
        if request.headers:
            if request.headers.get('Authorization'):
                if 'Bearer' in request.headers.get('Authorization'):
                    au = request.headers.get('Authorization').replace('Bearer', '').strip()
                    db_name = ManagerParent.objects.filter(token=au).values_list('db_name')
                    parent_id = ManagerParent.objects.filter(token=au).values_list('parent_id')
                    for e in parent_id:
                        parent_id = e[0]
                    if db_name:
                        for e in db_name:
                            school_name = e[0]

                        school_name = ManagerParent.pincode(school_name)
                        d = datetime.datetime.now().strftime('%Y-%m-%d 00:00:00')
                        result = {}
                        with connections[school_name].cursor() as cursor:
                            cursor.execute(
                                "select  name,state from pickup_request WHERE parent_id = %s AND date <= %s AND date >= %s",
                                [parent_id, datetime.datetime.now(),
                                 datetime.datetime.strptime(d, '%Y-%m-%d %H:%M:%S')])
                            columns = (x.name for x in cursor.description)
                            date_t = cursor.fetchall()
                            studen_state = [dict(zip(columns, row)) for row in date_t]
                            for rec in range(len(date_t)):
                                result[studen_state[rec]['name']] = {'status': studen_state[rec]['state']}
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


@api_view(['POST', 'GET'])
def kids_list(request):
    if request.method == 'POST':
        if request.headers:
            if request.headers.get('Authorization'):
                if 'Bearer' in request.headers.get('Authorization'):

                    l = []
                    au = request.headers.get('Authorization').replace('Bearer', '').strip()

                    l.append(au.split(","))

                    db_name = ManagerParent.objects.filter(token=au.split(",")[0]).values_list('db_name')
                    parent_id = ManagerParent.objects.filter(token=au.split(",")[0]).values_list('parent_id')
                    school_id = ManagerParent.objects.filter(token=au.split(",")[0]).values_list('school_id')
                    mobile_token = ManagerParent.objects.filter(token=au.split(",")[0]).values_list('mobile_token')
                    db_name_test = []
                    for e in mobile_token:
                        mobile_token = e[0]
                    database_yousef_test = ManagerParent.objects.filter(mobile_token=mobile_token).values_list(
                        'db_name')
                    for d in database_yousef_test:
                        db_name_test.append(d[0])
                    for e in parent_id:
                        parent_id = e[0]
                    for e in school_id:
                        school_id = e[0]
                    if db_name_test:
                        studen_list = []

                        seen = []
                        all_db_name_test = []
                        for d in db_name_test:
                            t = d
                            if d not in seen:
                                seen.append(t)
                                all_db_name_test.append(d)
                        for e in all_db_name_test:

                            school_name = e

                            school_name = ManagerParent.pincode(school_name)
                            parent_id = ManagerParent.objects.filter(Q(mobile_token=mobile_token),
                                                                     Q(db_name=school_name)).values_list('parent_id')
                            for e in parent_id:
                                parent_id = e[0]
                            with connections[school_name].cursor() as cursor:

                                cursor.execute(
                                    "select activate_app_map from school_parent WHERE id = %s",
                                    [parent_id])
                                parent_show_map = cursor.fetchall()

                                cursor.execute(
                                    "select  id,display_name_search,user_id,pick_up_type,drop_off_type,image_url,father_id,mother_id,state,academic_grade_name1,pick_up_type,name,name_ar,gender,password,national_id from student_student WHERE (father_id = %s OR mother_id = %s OR responsible_id_value = %s)  And state = 'done'",
                                    [parent_id, parent_id, parent_id])
                                student = cursor.fetchall()

                                # cursor.execute(
                                #     "select  id,display_name_search from student_student WHERE (father_id = %s OR mother_id = %s OR responsible_id_value = %s)  And state = 'done'",
                                #     [parent_id, parent_id, parent_id])
                                # student121 = cursor.fetchall()
                                # print(student121)
                                student1 = []
                                columnNames = [column[0] for column in cursor.description]
                                for record in student:
                                    student1.append(dict(zip(columnNames, record)))
                                cursor.execute(
                                    "select  lat,lng,pickup_request_distance,change_location,show_map,enable_parents_to_confirm_student_pickup,pickup_request_distance from transport_setting  ORDER BY ID DESC LIMIT 1")
                                setting = cursor.fetchall()
                                show_map = True
                                cursor.execute(
                                    "select name from res_lang WHERE id =(select first_lang  from res_company  WHERE id = %s ORDER BY ID DESC LIMIT 1) ",
                                    [school_id])

                                lang = cursor.fetchall()
                                cursor.execute(
                                    "select link  from res_company  ORDER BY ID DESC LIMIT 1",
                                    [])

                                school_logo = cursor.fetchall()

                                if (parent_show_map[0][0] == True):
                                    show_map = True
                                else:
                                    show_map = False
                                cursor.execute(
                                    "select  name,phone from res_company WHERE id = %s ",
                                    [school_id])
                                school = cursor.fetchall()
                                for rec in range(len(student)):
                                    is_active_round = False
                                    student_round_id = 0
                                    curr_date = date.today()
                                    cursor.execute(
                                        "select id from round_schedule WHERE  day_id = (select  id  from school_day where name = %s)",
                                        [calendar.day_name[curr_date.weekday()]])
                                    rounds_details = cursor.fetchall()
                                    for rou in range(len(rounds_details)):
                                        cursor.execute(
                                            "select round_schedule_id,transport_state from transport_participant WHERE round_schedule_id = %s and student_id = %s",
                                            [rounds_details[rou][0], student1[rec]['id']])

                                        rounds_count_student = cursor.fetchall()
                                        if rounds_count_student:
                                            cursor.execute(
                                                "select round_id from round_schedule WHERE  id = %s",
                                                [rounds_count_student[0][0]])
                                            rounds = cursor.fetchall()
                                            cursor.execute(
                                                "select is_active from transport_round WHERE  id = %s",
                                                [rounds[0][0]])
                                            is_active = cursor.fetchall()

                                            if is_active[0][0]:

                                                student_round_id = rounds[0][0]
                                                is_active_round = is_active[0][0]
                                                break
                                            else:

                                                student_round_id = rounds[0][0]
                                                is_active_round = is_active[0][0]

                                    x = {
                                        "Exams": {
                                            # "url": "https://" + school_name + ".staging.trackware.com/my/Badges/",tst.tracking.trackware.com
                                            # "arabic_url": "https://" + school_name + ".staging.trackware.com/ar_SY/my/Badges/",
                                            "url": "https://tst.tracking.trackware.com/my/Exams/",
                                            "arabic_url": "tst.tracking.trackware.com/ar_SY/my/Exams/",
                                            "name": "Exams",
                                            "name_ar": "امتحانات",
                                            "icon": "https://trackware-schools.s3.eu-central-1.amazonaws.com/Assignments.png",
                                            "icon_svg": "https://trackware-schools.s3.eu-central-1.amazonaws.com/flutter_app/Exams.svg"
                                        },
                                        "Badges": {
                                            # "url": "https://" + school_name + ".staging.trackware.com/my/Badges/",tst.tracking.trackware.com
                                            # "arabic_url": "https://" + school_name + ".staging.trackware.com/ar_SY/my/Badges/",
                                            "url": "https://tst.tracking.trackware.com/my/Badges/",
                                            "arabic_url": "tst.tracking.trackware.com/ar_SY/my/Badges/",
                                            "name": "Badges",
                                            "name_ar": "الشارات",
                                            "icon": "https://trackware-schools.s3.eu-central-1.amazonaws.com/Badge.png",
                                            "icon_svg": "https://trackware-schools.s3.eu-central-1.amazonaws.com/flutter_app/Badge.svg"
                                        },
                                        "Weeklyplans":
                                            {
                                                # "url": "https://" + school_name + ".staging.trackware.com/my/Weekly-plans/",
                                                # "arabic_url": "https://" + school_name + ".staging.trackware.com/ar_SY/my/Weekly-plans/",
                                                "url": "https://tst.tracking.trackware.com/my/Weekly-plans/",
                                                "arabic_url": "https://tst.tracking.trackware.com/ar_SY/my/Weekly-plans/",
                                                "name": "Weekly plans",
                                                "name_ar": "الخطط الأسبوعية",
                                                "icon": "https://trackware-schools.s3.eu-central-1.amazonaws.com/Weekly+Plans.png",
                                                "icon_svg": "https://trackware-schools.s3.eu-central-1.amazonaws.com/flutter_app/Weekly+Plans.svg"
                                            },
                                        "Assignments": {
                                            "url": "https://tst.tracking.trackware.com/my/Assignments/",
                                            "arabic_url": "https://tst.tracking.trackware.com/ar_SY/my/Assignments/",
                                            # "url": "https://" + school_name + ".staging.trackware.com/my/Assignments/",
                                            # "arabic_url": "https://" + school_name + ".staging.trackware.com/ar_SY/my/Assignments/",
                                            "name": "Assignments",
                                            "name_ar": "الواجبات الالكترونية",
                                            "icon": "https://trackware-schools.s3.eu-central-1.amazonaws.com/Assignments.png",
                                            "icon_svg": "https://trackware-schools.s3.eu-central-1.amazonaws.com/flutter_app/Assignments.svg"
                                        },
                                        # "Exam": {
                                        #     "url": "my/exam/",
                                        #     "arabic_url": "ar_SY/my/exam",
                                        #     "arabic_name": "امتحانات",
                                        #     "icon": "https://trackware-schools.s3.eu-central-1.amazonaws.com/Assignments.png"
                                        # },
                                        "Events":
                                            {"name": "Events",
                                             "name_ar": "الفعاليات و الانشطة",
                                             # "url": "https://" + school_name + ".staging.trackware.com/my/Events/",
                                             # "arabic_url": "https://" + school_name + ".staging.trackware.com/ar_SY/my/Events/",
                                             "url": "https://tst.tracking.trackware.com/my/Events/",
                                             "arabic_url": "https://tst.tracking.trackware.com/ar_SY/my/Events/",
                                             "arabic_name": "الفعاليات و الانشطة",
                                             "icon": "https://trackware-schools.s3.eu-central-1.amazonaws.com/Events.png",
                                             "icon_svg": "https://trackware-schools.s3.eu-central-1.amazonaws.com/flutter_app/Events.svg"
                                             },
                                        "Homeworks":
                                            {"name": "Homework",
                                             # "url": "https://" + school_name + ".staging.trackware.com/my/Homeworks/",
                                             # "arabic_url": "https://" + school_name + ".staging.trackware.com/ar_SY/my/Homeworks/",
                                             "url": "https://tst.tracking.trackware.com/my/Homeworks/",
                                             "arabic_url": "https://tst.tracking.trackware.com/ar_SY/my/Homeworks/",
                                             "name_ar": "الواجبات المنزلية",
                                             "icon": "https://trackware-schools.s3.eu-central-1.amazonaws.com/worksheets.png",
                                             "icon_svg": "https://trackware-schools.s3.eu-central-1.amazonaws.com/flutter_app/Worksheets.svg"
                                             },
                                        "Calendar":
                                            {"name": "Calendar",
                                             "url": "https://tst.tracking.trackware.com/my/Calendar/",
                                             "arabic_url": "https://tst.tracking.trackware.com/ar_SY/my/Calendar/",
                                             # "url": "https://" + school_name + ".staging.trackware.com/my/Calendar/",
                                             # "arabic_url": "https://" + school_name + ".staging.trackware.com/ar_SY/my/Calendar/",
                                             "name_ar": "التقويم",
                                             "icon": "https://trackware-schools.s3.eu-central-1.amazonaws.com/School+Calendar.png",
                                             "icon_svg": "https://trackware-schools.s3.eu-central-1.amazonaws.com/flutter_app/calendar.svg"
                                             },

                                        "Clinic":
                                            {"name": "Clinic",
                                             "name_ar": "العيادة",
                                             # "url": "https://" + school_name + ".staging.trackware.com/my/Clinic/",
                                             # "arabic_url": "https://" + school_name + ".staging.trackware.com/ar_SY/my/Clinic/",
                                             "url": "https://tst.tracking.trackware.com/my/Clinic/",
                                             "arabic_url": "https://tst.tracking.trackware.com/ar_SY/my/Clinic/",
                                             "arabic_name": "العيادة",
                                             "icon": "https://trackware-schools.s3.eu-central-1.amazonaws.com/Clinic.png",
                                             "icon_svg": "https://trackware-schools.s3.eu-central-1.amazonaws.com/flutter_app/Clinic.svg"
                                             },

                                        "Library":
                                            {"name": "Library",
                                             "name_ar": "المكتبه",
                                             # "url": "https://" + school_name + ".staging.trackware.com/my/Clinic/",
                                             # "arabic_url": "https://" + school_name + ".staging.trackware.com/ar_SY/my/Clinic/",
                                             "url": "https://tst.tracking.trackware.com/my/Library/",
                                             "arabic_url": "https://tst.tracking.trackware.com/ar_SY/my/Library/",
                                             "arabic_name": "العيادة",
                                             "icon": "https://trackware-schools.s3.eu-central-1.amazonaws.com/Clinic.png",
                                             "icon_svg": "https://trackware-schools.s3.eu-central-1.amazonaws.com/book-app.svg"
                                             },
                                        "Timetable":
                                            {"name": "Timetable",
                                             "name_ar": "الجدول الدراسي",
                                             # "url": "https://" + school_name + ".staging.trackware.com/my/Clinic/",
                                             # "arabic_url": "https://" + school_name + ".staging.trackware.com/ar_SY/my/Clinic/",
                                             "url": "https://tst.tracking.trackware.com/my/Timetable/",
                                             "arabic_url": "https://tst.tracking.trackware.com/ar_SY/my/Timetable/",
                                             "arabic_name": "الجدول الدراسي",
                                             "icon": "https://trackware-schools.s3.eu-central-1.amazonaws.com/icons8-curriculum-48.png",
                                             "icon_svg": "https://trackware-schools.s3.eu-central-1.amazonaws.com/icons8-curriculum-48.svg"
                                             }

                                    }
                                    url_m = {}
                                    model_list = (
                                    "Badges", "Clinic", "Calendar", "Homework", "Events", "Online Assignments",
                                    "Weekly Plans", 'Online Exams', 'Library', 'Timetable')
                                    cursor.execute("select name from ir_ui_menu where name in %s", [model_list])
                                    list = cursor.fetchall()
                                    res = []
                                    [res.append(x[0]) for x in list if x[0] not in res]
                                    model = []
                                    show_absence = False
                                    for rec1 in res:

                                        if 'Weekly Plans' == rec1:
                                            x['Weeklyplans']['arabic_url'] = x['Weeklyplans']['arabic_url'] + str(
                                                student1[rec]['user_id'])
                                            x['Weeklyplans']['url'] = x['Weeklyplans']['url'] + str(
                                                student1[rec]['user_id'])
                                            model.append(x['Weeklyplans'])

                                        if 'Events' == rec1:
                                            x['Events']['arabic_url'] = x['Events']['arabic_url'] + str(
                                                student1[rec]['user_id'])
                                            x['Events']['url'] = x['Events']['url'] + str(student1[rec]['user_id'])
                                            model.append(x['Events'])
                                        if 'Online Exams' == rec1:
                                            x['Exams']['arabic_url'] = x['Exams']['arabic_url'] + str(
                                                student1[rec]['user_id'])
                                            x['Exams']['url'] = x['Exams']['url'] + str(student1[rec]['user_id'])
                                            model.append(x['Exams'])

                                        if 'Online Assignments' == rec1:
                                            x['Assignments']['arabic_url'] = x['Assignments']['arabic_url'] + str(
                                                student1[rec]['user_id'])
                                            x['Assignments']['url'] = x['Assignments']['url'] + str(
                                                student1[rec]['user_id'])
                                            model.append(x['Assignments'])

                                        if 'Homework' == rec1:
                                            x['Homeworks']['arabic_url'] = x['Homeworks']['arabic_url'] + str(
                                                student1[rec]['user_id'])
                                            x['Homeworks']['url'] = x['Homeworks']['url'] + str(
                                                student1[rec]['user_id'])
                                            model.append(x['Homeworks'])

                                        if 'Badges' == rec1:
                                            x['Badges']['arabic_url'] = x['Badges']['arabic_url'] + str(
                                                student1[rec]['user_id'])
                                            x['Badges']['url'] = x['Badges']['url'] + str(student1[rec]['user_id'])
                                            model.append(x['Badges'])

                                        if 'Calendar' == rec1:
                                            x['Calendar']['url'] = x['Calendar']['url'] + str(student1[rec]['user_id'])
                                            x['Calendar']['arabic_url'] = x['Calendar']['arabic_url'] + str(
                                                student1[rec]['user_id'])
                                            model.append(x['Calendar'])

                                        if 'Clinic' == rec1:
                                            x['Clinic']['arabic_url'] = x['Clinic']['arabic_url'] + str(
                                                student1[rec]['user_id'])
                                            x['Clinic']['url'] = x['Clinic']['url'] + str(student1[rec]['user_id'])
                                            model.append(x['Clinic'])
                                        if 'Library' == rec1:
                                            x['Library']['arabic_url'] = x['Library']['arabic_url'] + str(
                                                student1[rec]['user_id'])
                                            x['Library']['url'] = x['Library']['url'] + str(student1[rec]['user_id'])
                                            model.append(x['Library'])
                                        if 'Timetable' == rec1:
                                            x['Timetable']['arabic_url'] = x['Timetable']['arabic_url'] + str(
                                                student1[rec]['user_id'])
                                            x['Timetable']['url'] = x['Timetable']['url'] + str(
                                                student1[rec]['user_id'])
                                            model.append(x['Timetable'])
                                    cursor.execute(
                                        "select name from ir_ui_menu where name ='Live Tracking'  LIMIT 1")
                                    tracking = cursor.fetchall()
                                    if len(tracking) > 0:
                                        model.append({
                                            # "url": "https://" + school_name + ".staging.trackware.com/my/Absence/" + str(
                                            #     student1[rec]['user_id']),
                                            # "arabic_url": "https://" + school_name + ".staging.trackware.com/ar_SY/my/Absence/" + str(
                                            #     student1[rec]['user_id']),
                                            "url": "https://tst.tracking.trackware.com/my/Absence/" + str(
                                                student1[rec]['user_id']),
                                            "arabic_url": "https://tst.tracking.trackware.com/ar_SY/my/Absence/" + str(
                                                student1[rec]['user_id']),
                                            "name": "Absence",
                                            "name_ar": "الغياب",
                                            "icon": "https://trackware-schools.s3.eu-central-1.amazonaws.com/Absence.png",
                                            "icon_svg": "https://trackware-schools.s3.eu-central-1.amazonaws.com/flutter_app/Absence.svg"
                                        }
                                        )
                                        show_absence = True
                                    try:
                                        cursor.execute(
                                            "select is_portal_exist from school_parent  LIMIT 1")
                                        is_portal_exist = cursor.fetchall()


                                    except:
                                        model = {
                                            "Absence":
                                                {
                                                    # "url": "https://" + school_name + ".staging.trackware.com/my/Absence/" + str(
                                                    #     student1[rec]['user_id']),
                                                    # "arabic_url": "https://" + school_name + ".staging.trackware.com/ar_SY/my/Absence/" + str(
                                                    #     student1[rec]['user_id']),
                                                    "url": "https://tst.tracking.trackware.com/my/Absence/" + str(
                                                        student1[rec]['user_id']),
                                                    "arabic_url": "https://tst.tracking.trackware.com/ar_SY/my/Absence/" + str(
                                                        student1[rec]['user_id']),
                                                    "name": "Absence",
                                                    "name_ar": "الغياب",
                                                    "icon": "https://trackware-schools.s3.eu-central-1.amazonaws.com/Absence.png",
                                                    "icon_svg": "https://trackware-schools.s3.eu-central-1.amazonaws.com/flutter_app/Absence.svg"
                                                }

                                        }
                                        show_absence = True
                                    if 'by_parents' in student[rec][3]:
                                        pick = True
                                    else:
                                        pick = False
                                    if 'by_parents' in student[rec][4]:
                                        drop = True
                                    else:
                                        drop = False
                                    student_st = ''
                                    assistant_id = 0
                                    assistant_name = ''
                                    assistant_mobile_number = ''
                                    driver_mobile_token = ''
                                    driver_mobile_number = ''
                                    driver_name = ''
                                    bus_id = 0
                                    round_type = ''
                                    round_name = ''
                                    # print(is_active_round)
                                    if bool(is_active_round):
                                        # print(rounds_count_student[0][1])
                                        start = datetime.datetime(datetime.datetime.now().year,
                                                                  datetime.datetime.now().month,
                                                                  datetime.datetime.now().day)
                                        cursor.execute(
                                            "select  activity_type,lat,long from student_history WHERE round_id = %s and student_id=%s and datetime = %s  ORDER BY ID DESC LIMIT 1 ",
                                            [rounds[0][0], student1[rec]['id'], start])
                                        student_history = cursor.fetchall()
                                        # print(student_history,"doasdklasodsadlssks")
                                        if student_history:
                                            student_st = student_history[0][0] if student_history else ""
                                        else:
                                            student_st = 'in' if rounds_count_student[0][1] == "Onboard" else \
                                            rounds_count_student[0][1] if rounds_count_student else ""

                                        cursor.execute(
                                            "select name,type,attendant_id,vehicle_id,driver_id from transport_round WHERE id = %s",
                                            [int(student_round_id)])
                                        round_info = cursor.fetchall()
                                        round_type = round_info[0][1]
                                        round_name = round_info[0][0]
                                        assistant_id = int(round_info[0][2])
                                        cursor.execute(
                                            "select name,mobile_phone from hr_employee WHERE id = %s",
                                            [assistant_id])
                                        assistant = cursor.fetchall()
                                        assistant_mobile_number = assistant[0][1]
                                        assistant_name = assistant[0][0]

                                        cursor.execute(
                                            "select name,mobile from res_partner WHERE id = %s",
                                            [round_info[0][4]])
                                        driver_info = cursor.fetchall()
                                        driver_name = driver_info[0][0]
                                        driver_mobile_number = driver_info[0][1]
                                        cursor.execute(
                                            "select bus_no from fleet_vehicle WHERE id = %s",
                                            [round_info[0][3]])
                                        fleet_info = cursor.fetchall()
                                        bus_id = int(fleet_info[0][0])

                                    student_grade = None
                                    # ----------------------
                                    cursor.execute(
                                        "SELECT academic_grade_id FROM public.student_distribution_line WHERE id = (SELECT student_distribution_line_id FROM student_distribution_line_student_student_rel WHERE student_student_id=%s ORDER BY student_distribution_line_id DESC LIMIT 1)",
                                        [student1[rec]['id']])
                                    student_distribution_line = cursor.fetchall()
                                    if student_distribution_line:
                                        cursor.execute(
                                            "SELECT name FROM public.academic_grade WHERE id = %s",
                                            [student_distribution_line[0][0]])
                                        academic_grade = cursor.fetchall()
                                        student_grade = academic_grade[0][0] if academic_grade else ''

                                    if student_grade == None:
                                        cursor.execute(
                                            "select name from academic_grade where id=(select academic_grade_id from school_class where id="
                                            "(select class_id from res_partner where id=(select partner_id from res_users where id="
                                            "(select user_id from student_student where id=%s))))",
                                            [student1[rec]['id']])
                                        academic_grade_q = cursor.fetchall()
                                        student_grade = academic_grade_q[0][0] if academic_grade_q else ''

                                        # ---------------------
                                    fname = student1[rec]['display_name_search']
                                    defaultImage = ''
                                    if student1[rec]['gender'] == 'male':
                                        defaultImage = 'https://trackware-schools.s3.eu-central-1.amazonaws.com/male.png'
                                    else:
                                        defaultImage = 'https://trackware-schools.s3.eu-central-1.amazonaws.com/fma.png'

                                    if any('English' in x[0] for x in lang):

                                        fname = student1[rec]['name']

                                    else:

                                        fname = student1[rec]['name_ar']
                                    # password,national_id
                                    user_name = student1[rec]['national_id']
                                    password = student1[rec]['national_id']
                                    if student1[rec]['password']:
                                        password = student1[rec]['password']
                                    url = 'https://tst.tracking.trackware.com/web/session/authenticate'
                                    # url = 'http://192.168.1.82:9098/web/session/authenticate'
                                    try:

                                        body = json.dumps(
                                            {"jsonrpc": "2.0",
                                             "params": {"db": school_name, "login": user_name, "password": password}})

                                        headers = {
                                            'Content-Type': 'application/json',
                                        }

                                        response1 = requests.request("POST", url, headers=headers, data=body)

                                        response = response1.json()
                                        if "error" in response:
                                            result = {
                                                "status": "erorrq"}
                                            # return Response(result)
                                        session = response1.cookies
                                        uid = response['result']['uid']
                                        company_id = response['result']['company_id']

                                    except:
                                        result = {
                                            "status": "erorr2"
                                                      ""}
                                        # return Response(result)
                                    # session = response1.cookies

                                    studen_list.append({
                                        "schoolImage": school_logo[0][0] if school_logo[0][
                                            0] else 'https://s3.eu-central-1.amazonaws.com/trackware.schools/public_images/default_student.png',
                                        "name": student1[rec]['display_name_search'],
                                        "fname": fname,
                                        "id": student1[rec]['id'],
                                        "user_id": student1[rec]['user_id'],
                                        "avatar": 'https://trackware-schools.s3.eu-central-1.amazonaws.com/' + str(
                                            student1[rec]['image_url']) if student1[rec][
                                            'image_url'] else defaultImage,
                                        "school_id": int(school_id),
                                        "student_grade": student_grade,
                                        "drop_off_by_parent": drop,
                                        "pickup_by_parent": pick,
                                        "father_id": student1[rec]['father_id'],
                                        "mother_id": student1[rec]['mother_id'],
                                        "other_1": 0,
                                        "other_2": 0,
                                        "school_name": school[0][0],
                                        "school_mobile_number": school[0][1],
                                        "school_lat": str(setting[0][0]),
                                        "school_lng": str(setting[0][1]),
                                        "driver_mobile_number": driver_mobile_number,
                                        "driver_mobile_token": "",
                                        "driver_name": driver_name,
                                        "assistant_name": assistant_name,
                                        "assistant_mobile_number": assistant_mobile_number,
                                        "bus_id": bus_id,
                                        "round_type": round_type,
                                        "is_active": bool(is_active_round),
                                        "round_name": round_name,
                                        "round_id": int(student_round_id),
                                        "assistant_id": assistant_id,

                                        "route_order": 0,
                                        "chat_teachers": False,
                                        "target_lng": "0.0",
                                        "target_lat": "0.0",
                                        "license_state": "not_active",
                                        "trial_days_left": 0,
                                        "license_days_left": 0,
                                        "semester_start_date": "",
                                        "semester_end_date": "",
                                        "show_add_bus_card": False,
                                        "allow_upload_students_images": False,
                                        "show_map": show_map,
                                        "change_location": bool(setting[0][3]),
                                        "pickup_request_distance": int(setting[0][2]),
                                        "db": school_name,
                                        "session_id": session.get_dict()['session_id'],
                                        "show_absence": show_absence,
                                        "student_status": {
                                            "activity_type": str(student_st),
                                            "round_id": int(student_round_id),
                                            "datetime": ""
                                        },
                                        "features": model,
                                    })

                        result = {'message': '', 'students': studen_list, "parent_id": int(parent_id)}
                        # print(result)
                        return Response(result)

                    result = {'status': 'error'}
                    return Response(result)
        result = {'status': 'error'}
        return Response(result)
    elif request.method == 'GET':
        result = {'status': 'error'}
        return Response(result)


def date_time(deadline):
    # cursor.execute(
    #     """select timezone from transport_setting ORDER BY ID DESC LIMIT 1""")
    # transport_setting = cursor.fetchall()
    # date_tz = transport_setting[0][0]
    date_tz = 'Asia/Kuwait'

    if deadline:
        deadline = deadline.astimezone(pytz.timezone(date_tz))
    else:

        deadline = datetime.datetime.now().astimezone(pytz.timezone(date_tz))

    year = str(deadline.year)
    month = '0' + str(deadline.month) if int(deadline.month) < 10 else str(
        deadline.month)
    day = str(deadline.day) if len(str(deadline.day)) > 1 else "0" + str(
        deadline.day)
    hour = str(deadline.hour) if len(str(deadline.hour)) > 1 else "0" + str(
        deadline.hour)
    minute = str(deadline.minute) if len(
        str(deadline.minute)) > 1 else "0" + str(deadline.minute)
    second = str(deadline.second) if len(
        str(deadline.second)) > 1 else "0" + str(deadline.second)
    return year + "-" + month + "-" + day + " " + hour + ":" + minute + ":" + "00"


@api_view(['POST'])
def read_survey(request):
    if request.method == 'POST':
        if request.headers:
            if request.headers.get('Authorization'):
                if 'Bearer' in request.headers.get('Authorization'):
                    au = request.headers.get('Authorization').replace('Bearer', '').strip()
                    db_name = ManagerParent.objects.filter(token=au).values_list('db_name')
                    parent_id = ManagerParent.objects.filter(token=au).values_list('parent_id')

                    for e in parent_id:
                        parent_id = e[0]
                    if db_name:
                        for e in db_name:
                            school_name = e[0]
                        school_name = ManagerParent.pincode(school_name)
                        message_id = request.data.get('message_id')

                        with connections[school_name].cursor() as cursor:

                            cursor.execute(
                                " select read_message from survey_user_input where id=%s ",
                                [message_id])
                            read_message = cursor.fetchall()
                            if read_message[0][0]:
                                cursor.execute(
                                    "UPDATE public.survey_user_input SET read_message=not(read_message) WHERE id=%s;",
                                    [message_id])
                            else:
                                cursor.execute(
                                    "UPDATE public.survey_user_input SET read_message=true WHERE id=%s;",
                                    [message_id])

                            result = {
                                'status': 'ok', }

                            return Response(result)
                    else:
                        result = {'result': 'error1'}
                        return Response(result)
                else:
                    result = {'result': 'error2'}
                    return Response(result)
            else:
                result = {'result': 'error3'}
                return Response(result)
        else:
            result = {'result': 'error4'}
            return Response(result)


@api_view(['POST'])
def hide_survey(request):
    if request.method == 'POST':
        if request.headers:
            if request.headers.get('Authorization'):
                if 'Bearer' in request.headers.get('Authorization'):
                    au = request.headers.get('Authorization').replace('Bearer', '').strip()
                    db_name = ManagerParent.objects.filter(token=au).values_list('db_name')
                    parent_id = ManagerParent.objects.filter(token=au).values_list('parent_id')

                    for e in parent_id:
                        parent_id = e[0]
                    if db_name:
                        for e in db_name:
                            school_name = e[0]
                        school_name = ManagerParent.pincode(school_name)
                        message_id = request.data.get('message_id')

                        with connections[school_name].cursor() as cursor:
                            cursor.execute(
                                "UPDATE public.survey_user_input SET show_message=not(show_message) WHERE id=%s;",
                                [message_id])
                            result = {'status': 'ok', }
                            return Response(result)
                    else:
                        result = {'result': 'error1'}
                        return Response(result)
                else:
                    result = {'result': 'error2'}
                    return Response(result)
            else:
                result = {'result': 'error3'}
                return Response(result)
        else:
            result = {'result': 'error4'}
            return Response(result)


@api_view(['POST'])
def read_message(request):
    if request.method == 'POST':
        if request.headers:
            if request.headers.get('Authorization'):
                if 'Bearer' in request.headers.get('Authorization'):
                    au = request.headers.get('Authorization').replace('Bearer', '').strip()
                    db_name = ManagerParent.objects.filter(token=au).values_list('db_name')
                    parent_id = ManagerParent.objects.filter(token=au).values_list('parent_id')

                    for e in parent_id:
                        parent_id = e[0]
                    if db_name:
                        for e in db_name:
                            school_name = e[0]
                        school_name = ManagerParent.pincode(school_name)
                        message_id = request.data.get('message_id')

                        with connections[school_name].cursor() as cursor:

                            cursor.execute(
                                " select read_message from school_message_student_student where id=%s ",
                                [message_id])
                            read_message = cursor.fetchall()
                            # print(read_message[0][0])
                            if read_message[0][0]:
                                # print("ddddddddddddddddddddddddd")
                                cursor.execute(
                                    "UPDATE public.message_student SET read_message=not(read_message) WHERE id=%s;",
                                    [message_id])
                            else:
                                # print("ddddddddddddddddddddddddqqd")
                                cursor.execute(
                                    "UPDATE public.school_message_student_student SET read_message=true WHERE id=%s;",
                                    [message_id])
                                cursor.execute(
                                    "UPDATE public.message_student SET read_message=true WHERE id=%s;",
                                    [message_id])

                            result = {'status': 'ok', }

                            return Response(result)
                    else:
                        result = {'result': 'error1'}
                        return Response(result)
                else:
                    result = {'result': 'error2'}
                    return Response(result)
            else:
                result = {'result': 'error3'}
                return Response(result)
        else:
            result = {'result': 'error4'}
            return Response(result)


@api_view(['POST'])
def hide_message(request):
    if request.method == 'POST':
        if request.headers:
            if request.headers.get('Authorization'):
                if 'Bearer' in request.headers.get('Authorization'):
                    au = request.headers.get('Authorization').replace('Bearer', '').strip()
                    db_name = ManagerParent.objects.filter(token=au).values_list('db_name')
                    parent_id = ManagerParent.objects.filter(token=au).values_list('parent_id')

                    for e in parent_id:
                        parent_id = e[0]
                    if db_name:
                        for e in db_name:
                            school_name = e[0]
                        school_name = ManagerParent.pincode(school_name)
                        message_id = request.data.get('message_id')

                        with connections[school_name].cursor() as cursor:

                            cursor.execute(
                                "select show_message from message_student WHERE id =%s",
                                [message_id])
                            message_student = cursor.fetchall()
                            if message_student[0][0]:
                                cursor.execute(
                                    "UPDATE public.message_student SET show_message=not(show_message) WHERE id=%s;",
                                    [message_id])
                            else:
                                cursor.execute(
                                    "UPDATE public.message_student SET show_message=false WHERE id=%s;",
                                    [message_id])
                            result = {'status': 'ok', }
                            return Response(result)
                    else:
                        result = {'result': 'error1'}
                        return Response(result)
                else:
                    result = {'result': 'error2'}
                    return Response(result)
            else:
                result = {'result': 'error3'}
                return Response(result)
        else:
            result = {'result': 'error4'}
            return Response(result)


def get_info_message_new(deadline, notifications_text, avatar, create_date, notifications_title, student_name, student_id,id=0,stutes_notif=None,show_notif=None,action_id='0',notifications_title_ar='',notifications_text_ar='',student_image='https://s3.eu-central-1.amazonaws.com/trackware.schools/public_images/default_student.png',image_link='',plan_name='',attachments=[]):
    show=show_notif
    # print(attachments," ooooooooooooooooooooo")
    # if student_image:
    #     print(student_image)
    if not notifications_title:
        notifications_title=''

    stutes=stutes_notif
    # print(stutes)
    if stutes=='Read' or stutes:
        stutes="Mark As UnRead"
    elif  stutes=='UnRead' or not stutes :
        stutes = "Mark As Read"
    else:
        stutes = "Mark As Read"

    if show==None:
        show="show"

    notificationsType = ''
    icon_tracking=''
    if 'Weekly Plan' in notifications_title  or 'Assignment' in notifications_title or  'Homework' in notifications_title or  'Exam' in notifications_title or 'educational' in notifications_title:
        notificationsType = 'educational'
        if ( 'Weekly Plan' in notifications_title or 'educational' in notifications_title):
            icon_tracking = 'https://trackware-schools.s3.eu-central-1.amazonaws.com/flutter_app/Weekly+Plans.svg'
        elif ( 'Assignment' in notifications_title):
            icon_tracking = 'https://trackware-schools.s3.eu-central-1.amazonaws.com/flutter_app/Assignments.svg'
        elif ( 'Exam' in notifications_title):
            icon_tracking = 'https://trackware-schools.s3.eu-central-1.amazonaws.com/flutter_app/Exams.svg'
        elif ('Homework' in notifications_title):
            icon_tracking = 'https://trackware-schools.s3.eu-central-1.amazonaws.com/flutter_app/Worksheets.svg'

    elif 'Pick Up By Parent' in notifications_title or ('Absence' in notifications_title and  notifications_title  != "Absence notification" ) or  'clinic' in notifications_title or 'library' in notifications_title :

        notificationsType = 'Absence'
        if ( 'clinic' in notifications_title):
            icon_tracking = 'https://trackware-schools.s3.eu-central-1.amazonaws.com/flutter_app/Clinic.svg'
        elif ( 'library' in notifications_title):
            icon_tracking = 'https://trackware-schools.s3.eu-central-1.amazonaws.com/book-app.svg'
        else:
            icon_tracking = 'https://trackware-schools.s3.eu-central-1.amazonaws.com/flutter_app/Absence.svg'
    elif notifications_title == 'Pick-up round' or notifications_title == 'School Departure' or notifications_title == 'Checkout Notification' or notifications_title == 'No Show Notification' or "has arrived at your home" in notifications_text or "has just reached the school" in notifications_text or "has just been checked into the bus" in notifications_text or notifications_title == "Absence notification" or 'Message from bus no' in notifications_title:

        notificationsType = 'tracking'
        if (notifications_title == 'Pick-up round' or notifications_title == 'School Departure'):
            icon_tracking = 'https://trackware-schools.s3.eu-central-1.amazonaws.com/flutter_app/icons8-get-on-bus.svg'
        elif (notifications_title == 'Checkout Notification'):
            icon_tracking = 'https://trackware-schools.s3.eu-central-1.amazonaws.com/flutter_app/Absence.svg'
        elif (notifications_title == 'No Show Notification'):
            icon_tracking = 'https://trackware-schools.s3.eu-central-1.amazonaws.com/flutter_app/icons8-get-on-bus+(1).svg'
        elif "has arrived at your home" in notifications_text:
            icon_tracking = 'https://trackware-schools.s3.eu-central-1.amazonaws.com/flutter_app/icons8-house+(1).svg'
        elif "has just reached the school." in notifications_text:
            icon_tracking = 'https://trackware-schools.s3.eu-central-1.amazonaws.com/flutter_app/Absence.svg'
        elif "has just been checked into the bus." in notifications_text:
            icon_tracking = 'https://trackware-schools.s3.eu-central-1.amazonaws.com/flutter_app/icons8-get-on-bus.svg'
        elif notifications_title == "Absence notification":
            notifications_title="bsence notification"
            icon_tracking = 'https://trackware-schools.s3.eu-central-1.amazonaws.com/flutter_app/Absence.svg'
        else:
            icon_tracking = 'https://trackware-schools.s3.eu-central-1.amazonaws.com/flutter_app/icons8-shuttle-bus.svg'
    else:
        notificationsType = 'announcement'
        if (notifications_title == 'survey'):
            icon_tracking=show_notif
        elif('Event' in notifications_title)  :
            icon_tracking = 'https://trackware-schools.s3.eu-central-1.amazonaws.com/flutter_app/Events.svg'
        elif ( 'Meeting' in notifications_title):
            icon_tracking = 'https://trackware-schools.s3.eu-central-1.amazonaws.com/flutter_app/calendar.svg'
        else:
            icon_tracking = 'https://trackware-schools.s3.eu-central-1.amazonaws.com/School+messages.svg'


    if student_name:
        return {
            "avatar": avatar,
            "date_time": date_time(deadline),
            "notifications_text": notifications_text,
            "create_date": create_date,
            "notifications_title": notifications_title,
            "student_name": student_name,
            "student_id": str(student_id),
            "notificationsType": notificationsType,
            "icon_tracking":icon_tracking,
            "id": str(id),
            "stutes": stutes,
            "show": show,
            "student_image": student_image,
            "action_id": str(action_id),
            "notifications_text_ar": notifications_text_ar if notifications_text_ar else  notifications_text,
            "notifications_title_ar": notifications_title_ar if notifications_title_ar else notifications_title,
            "imageLink":'https://trackware-schools.s3.eu-central-1.amazonaws.com/' +str(image_link)if image_link else '',
            "plan_name": plan_name if plan_name else '',
            'attachments':attachments


        }
    else:
        return {
            "avatar": avatar,
            "date_time": date_time(deadline),
            "notifications_text": notifications_text,
            "create_date": create_date,
            "notifications_title": notifications_title,
            "student_id": str(student_id),
            "notificationsType": notificationsType,
            "icon_tracking":icon_tracking,
            "id":id,
            "stutes":stutes,
            "show":show,
            "student_image": student_image,
            "action_id": str(action_id),
            "notifications_text_ar": notifications_text_ar if notifications_text_ar else notifications_text,
            "notifications_title_ar": notifications_title_ar if notifications_title_ar else notifications_title,
            "imageLink": 'https://trackware-schools.s3.eu-central-1.amazonaws.com/' +str(image_link)if image_link else '',
            "plan_name": plan_name if plan_name else '',
            "attachments":attachments

        }




# get school message
def get_school_message_new(student_id, school_name, school_message, student_name):
    notifications = []
    with connections[school_name].cursor() as cursor:
        message_ids = []
        seen = set()
        for rec in school_message:
            message_ids.append(rec[0])
        message_ids = list(dict.fromkeys(message_ids))
        if message_ids:

            cursor.execute(
                "select DISTINCT ON (school_message_id) school_message_id,id,read_message,show_message,action_id from school_message_student_student WHERE school_message_id in %s AND student_student_id = %s AND show_message=true",
                [tuple(message_ids), student_id])
            message_student = cursor.fetchall()
            cursor.execute(
                "select  image_url from student_student WHERE id=%s",
                [student_id])
            student_image = cursor.fetchall()
            message_id = []
            for res in message_student:
                action_id = res[4]
                message_id.append(res[0])

                cursor.execute(
                    "select  id,search_type,title,message,create_date,date from school_message WHERE id = %s",
                    [res[0]])
                school_message1 = cursor.fetchall()

                for rec in range(len(school_message1)):

                    deadline = school_message1[rec][4]
                    notifications_text = school_message1[rec][3] if school_message1[rec][3] else ''
                    avatar = "https://s3.eu-central-1.amazonaws.com/notifications-images/mobile-notifications-icons/notification_icon_msg_admin.png"
                    create_date = school_message1[rec][4].replace(second=0) if school_message1[rec][4] else ''
                    notifications_title = school_message1[rec][2] if school_message1[rec][2] else ''
                    d = {'notifications_title': notifications_title, 'notifications_text': notifications_text,
                         'student_id': student_id}
                    t = tuple(d.items())
                    if t not in seen:
                        seen.add(t)
                        if res[4]:

                            if ('Event' in notifications_title):
                                cursor.execute(
                                    " select id,event_id,state,new_added from school_event_registration where  student_id =%s and  event_id =%s  ORDER BY create_date DESC",
                                    [student_id, res[4]])
                                events = cursor.fetchall()

                                if events:
                                    action_id = events[0][0]
                        notifications.append(
                            get_info_message_new(deadline, notifications_text, avatar, create_date, notifications_title,
                                                 student_name, student_id, res[1], "Read" if res[2] else 'UnRead',
                                                 "show" if res[3] else 'not show', action_id, '', '',
                                                 'https://trackware-schools.s3.eu-central-1.amazonaws.com/' + str(
                                                     student_image[0][0]) if student_image[0][
                                                     0] else 'https://s3.eu-central-1.amazonaws.com/trackware.schools/public_images/default_student.png', ))

    return notifications


def get_survey(student_id, school_name):
    notifications = []
    with connections[school_name].cursor() as cursor:
        message_ids = []
        cursor.execute(
            "select user_id,display_name_search from school_parent where id=%s",
            [student_id])
        user_id_q = cursor.fetchall()

        if user_id_q:
            state = 'new'
            start = False
            cursor.execute(
                " select id,survey_id,token,last_displayed_page_id,state,read_message from survey_user_input where partner_id=(select partner_id from res_users where id=%s) AND show_message=true   ORDER BY create_date DESC, state DESC",
                [user_id_q[0][0]])
            assignments = cursor.fetchall()

            for assingment in assignments:
                cursor.execute(
                    " select id,state,deadline,title,access_token,subject_id,allowed_time_to_start,time_limit,mark,exam_names,create_date from survey_survey where id=%s",
                    [assingment[1]])
                survey = cursor.fetchall()
                if survey:
                    avatar = "https://s3.eu-central-1.amazonaws.com/notifications-images/mobile-notifications-icons/notification_icon_msg_admin.png"
                    if survey[0][1] == 'open':
                        if survey[0][2]:
                            deadline = survey[0][2]
                            date_tz = 'Asia/Kuwait'
                            deadline.replace(date_tz)
                            deadline = deadline.replace(date_tz)
                            deadline = datetime.strptime(deadline, "%d/%m/%Y %H:%M:%S")
                            x = datetime.datetime.now().replace(date_tz)
                            if deadline <= datetime.strptime(x, "%d/%m/%Y %H:%M:%S"):
                                start = True
                                state = 'done'
                            else:
                                if assingment[4] == 'done':
                                    state = 'done'
                                    start = False
                                else:
                                    state = assingment[4]
                                    start = True
                        else:
                            deadline = ""
                            state = assingment[4]
                            start = False
                        if not state == "done":
                            school_base = "https://" + school_name + ".tracking.trackware.com/" + "/survey/start/" + \
                                          survey[0][4] + "?answer_token=" + assingment[2]
                            read = "Read" if assingment[5] else 'UnRead'
                            notifications.append(
                                get_info_message_new(survey[0][10], survey[0][3], avatar, survey[0][10], "survey",
                                                     user_id_q[0][1], student_id, assingment[0], read, school_base))

    return notifications


def get_student_history_new(student_id, school_name, student_name):
    notifications = []
    with connections[school_name].cursor() as cursor:
        list_hist_student = []
        cursor.execute(
            " SELECT  notification_id,round_id FROM student_history WHERE (activity_type='absent-all' or activity_type='absent') and student_id=%s",
            [student_id])
        student_history = cursor.fetchall()

        for mas in student_history:
            cursor.execute(
                "select bus_no from fleet_vehicle WHERE id = (select  vehicle_id from transport_round WHERE id = %s)  ",
                [mas[1]])
            bus_num = cursor.fetchall()
            if mas[0] in list_hist_student:
                continue
            else:
                list_hist_student.append(mas[0])

            cursor.execute(
                "select  message_en,create_date,type,id,type_ar,message_ar from sh_message_wizard WHERE id=%s ORDER BY ID DESC LIMIT 50",
                [mas[0]])
            sh_message_wizard1 = cursor.fetchall()

            for sh_message_bus in range(len(sh_message_wizard1)):
                deadline = sh_message_wizard1[sh_message_bus][1]

                notifications_text = sh_message_wizard1[sh_message_bus][0]
                notifications_text_ar = sh_message_wizard1[sh_message_bus][5]
                avatar = "https://s3.eu-central-1.amazonaws.com/notifications-images/mobile-notifications-icons/notification_icon_check_in_drop.png"
                create_date = deadline.replace(second=0) if deadline else ''
                notifications_title = "Message from bus no. " + str(bus_num[0][0]) + "   " + str(student_name)
                notifications_title_ar = str(student_name) + " " + str(
                    bus_num[0][0]) + "   " + "رسالة من الحافلة رقم . "
                notifications.append(
                    get_info_message_new(deadline, notifications_text, avatar, create_date, notifications_title,
                                         student_name, student_id, 0, None, None, '0', notifications_title_ar,
                                         notifications_text_ar))
    return notifications


def get_bus_notifition_student_new(school_name, student_name, notifications_text, notifications_title, deadline,
                                   round_id,
                                   attendance_round, student_id, notifications_title_ar, notifications_text_ar,
                                   fname_ar):
    notifications = []
    avatar = "https://s3.eu-central-1.amazonaws.com/notifications-images/mobile-notifications-icons/notification_icon_check_in_drop.png"
    with connections[school_name].cursor() as cursor:
        create_date = deadline.replace(second=0) if deadline else ''
        cursor.execute(
            "select  vehicle_id from transport_round WHERE id = %s",
            [round_id])

        vehicle_id = cursor.fetchall()
        cursor.execute(
            "select bus_no from fleet_vehicle WHERE id = %s  ",
            [vehicle_id[0][0]])
        bus_num = cursor.fetchall()

        if "just been" in notifications_text:

            if str(student_name) in notifications_text or str(fname_ar) in notifications_text:

                if notifications_title == 'School Departure':
                    notifications_title = 'School Departure'
                else:
                    notifications_title = 'Bus notification'
                notifications.append(
                    get_info_message_new(deadline, notifications_text, avatar, create_date, notifications_title,
                                         student_name, student_id, 0, None, None, '0', notifications_title_ar,
                                         notifications_text_ar))
        elif "did not check into the bus today" in notifications_text:
            if str(student_name) in notifications_text or str(fname_ar) in notifications_text:
                notifications.append(
                    get_info_message_new(deadline, notifications_text, avatar, create_date, "No Show Notification",
                                         student_name, student_id, 0, None, None, '0', notifications_title_ar,
                                         notifications_text_ar))
        elif "has not checked into the bus" in notifications_text:
            if str(student_name) in notifications_text or str(fname_ar) in notifications_text:
                notifications.append(
                    get_info_message_new(deadline, notifications_text, avatar, create_date, "Absence notification",
                                         student_name, student_id, 0, None, None, '0', notifications_title_ar,
                                         notifications_text_ar))
        elif "has arrived at your home and" in notifications_text:

            if str(student_name) in notifications_text or str(fname_ar) in notifications_text:
                notifications.append(
                    get_info_message_new(deadline, notifications_text, avatar, create_date, "Checkout Notification",
                                         student_name, student_id, 0, None, None, '0', notifications_title_ar,
                                         notifications_text_ar))

        elif "just reached" in notifications_text:
            if str(student_name) in notifications_text or str(fname_ar) in notifications_text:
                notifications.append(
                    get_info_message_new(deadline, notifications_text, avatar, create_date, "Bus notification",
                                         student_name, student_id, 0, None, None, '0', notifications_title_ar,
                                         notifications_text_ar))
        elif "The pickup round is started" in notifications_text:
            if str(student_name) in notifications_text or str(fname_ar) in notifications_text:
                notifications.append(
                    get_info_message_new(deadline, notifications_text, avatar, create_date, "Pick-up round",
                                         student_name, student_id, 0, None, None, '0', notifications_title_ar,
                                         notifications_text_ar))
        else:

            cursor.execute(
                "select  is_active,type from transport_round WHERE id = %s  ",
                [round_id])
            is_active = cursor.fetchall()

            time = ''
            if attendance_round:
                if is_active[0][1] == 'pick_up':
                    time = attendance_round[0][2]
                else:
                    time = attendance_round[0][3]
            notifications_title_ar = str(student_name) + " " + str(bus_num) + "   " + "رسالة من الحافلة رقم . "
            if 'emergency_student' + str(student_id) != notifications_title:
                if time:
                    if time > deadline:
                        notifications.append(
                            get_info_message_new(deadline, notifications_text, avatar, create_date,
                                                 "Message from bus no. " + str(
                                                     bus_num[0][0]) + "  " + str(student_name), student_name,
                                                 student_id, 0, None, None, '0', notifications_title_ar,
                                                 notifications_text_ar))


            else:
                notifications.append(
                    get_info_message_new(deadline, notifications_text, avatar, create_date,
                                         "Message from bus no. " + str(
                                             bus_num[0][0]) + "  " + str(student_name), student_name, student_id, 0,
                                         None, None, '0', notifications_title_ar, notifications_text_ar))
    return notifications


@api_view(['POST'])
def kids_hstory_new(request):
    if request.method == 'POST':
        if request.headers:
            if request.headers.get('Authorization'):
                if 'Bearer' in request.headers.get('Authorization'):
                    au = request.headers.get('Authorization').replace('Bearer', '').strip()

                    db_name = ManagerParent.objects.filter(token=au).values_list('db_name')
                    parent_id = ManagerParent.objects.filter(token=au).values_list('parent_id')

                    notifications = []
                    notifications_not_d = []
                    seen = set()

                    for e in parent_id:
                        parent_id = e[0]
                    if db_name:
                        for e in db_name:
                            school_name = e[0]
                        school_name = ManagerParent.pincode(school_name)
                        start_date = request.data.get('start_date')
                        end_date = request.data.get('end_date')
                        student_round = []
                        student_history_id = []
                        with connections[school_name].cursor() as cursor:
                            if start_date and end_date:
                                cursor.execute(
                                    "select  id  from school_message WHERE create_date >= %s AND create_date <= %s",
                                    [start_date, end_date])
                                school_message = cursor.fetchall()
                            elif start_date and not end_date:
                                cursor.execute(
                                    "select  id  from school_message WHERE create_date >= %s ",
                                    [start_date])

                                school_message = cursor.fetchall()
                            elif not start_date and end_date:
                                cursor.execute(
                                    "select  id  from school_message WHERE  create_date <= %s",
                                    [end_date])

                                school_message = cursor.fetchall()
                            elif not start_date and not end_date:
                                cursor.execute("select  id  from school_message ")
                                school_message = cursor.fetchall()
                            cursor.execute(
                                "SELECT column_name FROM information_schema.columns WHERE table_name='survey_user_input' and column_name='read_message'",
                                [])
                            information_schema_survey = cursor.fetchall()
                            if information_schema_survey:
                                notifications += get_survey(parent_id, school_name)

                            # notifications +=get_survey(parent_id,school_name)
                            cursor.execute(
                                "select  id,display_name_search,image_url,name,name_ar,year_id,user_id from student_student WHERE (father_id = %s OR mother_id = %s OR responsible_id_value = %s)  And state = 'done'",
                                [parent_id, parent_id, parent_id])
                            student_info = cursor.fetchall()
                            student_round_id = []

                            cursor.execute(
                                "select name from res_lang WHERE id = (select first_lang  from res_company  ORDER BY ID DESC LIMIT 1) ",
                                [])
                            #
                            lang = cursor.fetchall()
                            fname = ''
                            fname_ar = ''
                            for student in student_info:
                                # print("safkdsfkdkkfsdfkd")

                                cursor.execute(
                                    " select branch_id from res_users where id=%s",
                                    [student[6]])
                                branch_id = cursor.fetchall()
                                # SELECT column_name
                                # FROM information_schema.columns
                                # WHERE table_name='res_partner' and column_name='yousef';

                                cursor.execute(
                                    "SELECT column_name FROM information_schema.columns WHERE table_name='message_student' and column_name='image_link'",
                                    [])
                                information_schema = cursor.fetchall()
                                if information_schema:
                                    cursor.execute(
                                        "select  date,message_en,message_ar,title,title_ar,action_id,id,image_link,read_message,plan_name,school_message_id from message_student WHERE  branch_id = %s And year_id = %s  And student_id = %s AND (show_message  is null or show_message=true) ORDER BY ID DESC",
                                        [branch_id[0][0], student[5], student[0]])
                                    student_mes = cursor.fetchall()
                                    # print("1653 line ",student_mes)
                                else:
                                    cursor.execute(
                                        "select  date,message_en,message_ar,title,title_ar,action_id,id,read_message,school_message_id from message_student WHERE  branch_id = %s And year_id = %s  And student_id = %s AND (show_message  is null or show_message=true) ORDER BY ID DESC",
                                        [branch_id[0][0], student[5], student[0]])
                                    student_mes = cursor.fetchall()
                                # cursor.execute(
                                #         "INSERT INTO message_student(create_date, type, message_en,message_ar,title,title_ar,date,year_id,branch_id,student_id)VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);",
                                #         [r, 'App\Model\drive', d['notifications_text'], d['notifications_text_ar'], d['notifications_title'], d['notifications_title_ar'], d['date_time'],student_name[0][0],branch_id[0][0],d['student_id']])
                                #         year_id = fields.Many2one('academic.year', 'Academic Year', ondelete='cascade')
                                avatar="https://s3.eu-central-1.amazonaws.com/notifications-images/mobile-notifications-icons/notification_icon_check_in_drop.png"
                                for mes in student_mes:
                                    action_id=mes[5]
                                    if mes[3]:
                                        if ('Event' in mes[3]):
                                            cursor.execute(
                                                " select id,event_id,state,new_added from school_event_registration where  student_id =%s and  event_id =%s  ORDER BY create_date DESC",
                                                [student[0], mes[5]])
                                            events = cursor.fetchall()

                                            if events:
                                                action_id = events[0][0]
                                        cursor.execute(
                                            "select id,name,url from ir_attachment where school_message_id=%s",
                                            [mes[10] if information_schema else mes[8]])

                                        ir_attachment = cursor.fetchall()
                                        attachments = []
                                        if ir_attachment:
                                            for att in ir_attachment:
                                                if att[2]:
                                                    attachments.append(
                                                        {'id': att[0], 'name': att[1], 'datas': att[2]})
                                                    # print(attachments)

                                    notifications.append(
                                        get_info_message_new(mes[0],
                                                             mes[1],
                                                             avatar,
                                                             mes[0].replace(
                                                                 second=0) if mes[0] else '',
                                                             mes[3],
                                                             student[1], student[0], mes[6], mes[8] if information_schema else mes[7], None, action_id if mes[5] else '0', mes[4],
                                                             mes[2],'https://s3.eu-central-1.amazonaws.com/trackware.schools/public_images/default_student.png',mes[7]if information_schema else '',plan_name=mes[9]if information_schema else '',attachments=attachments))
                            #
                            #     student_round = []
                            #     if  any('English'  in x[0]  for x in lang):
                            #
                            #         fname = student[3]
                            #
                            #     else:
                            #
                            #         fname = student[4]
                            #     notifications += get_school_message_new(student[0], school_name, school_message, fname)
                            #     notifications += get_student_history_new(student[0], school_name, fname)
                            #     cursor.execute(
                            #         "select  round_schedule_id from transport_participant WHERE student_id = %s",
                            #         [student[0]])
                            #     round_schedule_id = cursor.fetchall()
                            #     #     get bus message
                            #     for rec in round_schedule_id:
                            #
                            #         cursor.execute(
                            #             "select  round_id from round_schedule WHERE id = %s",
                            #             [rec[0]])
                            #         round_schedule = cursor.fetchall()
                            #
                            #         round_schedules = []
                            #         student_round_h = []
                            #         for rec in round_schedule:
                            #
                            #             if rec[0] in student_round:
                            #
                            #                 continue
                            #             else:
                            #                 cursor.execute(
                            #                     "select  type from transport_round WHERE id = %s",
                            #                     [rec[0]])
                            #
                            #                 type = cursor.fetchall()
                            #
                            #                 if type[0][0] == 'pick_up':
                            #                     student_round_h.append(rec[0])
                            #                 student_round.append(rec[0])
                            #                 round_schedules.append(rec[0])
                            #         round_schedules = list(dict.fromkeys(student_round))
                            #
                            #         for rec_s in round_schedules:
                            #             if rec_s in student_round_id:
                            #                 pass
                            #             else:
                            #                 student_round_id.append(rec_s)
                            #
                            #                 cursor.execute(
                            #                     "select  message_ar,create_date,type,round_id,id,type_ar,message_en from sh_message_wizard WHERE round_id = %s and (type= %s or from_type =%s ) ORDER BY ID DESC LIMIT 50",
                            #                     [rec_s, 'emergency',
                            #                      'App\Model\sta' + str(parent_id)])
                            #                 sh_message_wizard = cursor.fetchall()
                            #
                            #
                            #
                            #                 # save bus message
                            #                 for message_wizard in range(len(sh_message_wizard)):
                            #                     avatar = "https://s3.eu-central-1.amazonaws.com/notifications-images/mobile-notifications-icons/notification_icon_check_in_drop.png"
                            #                     for std in student_info:
                            #                         if any('English'  not in x[0]  for x in lang):
                            #                             fname = std[3]
                            #                             fname_ar=std[4]
                            #
                            #                         else:
                            #                             fname = std[4]
                            #                             fname_ar = std[3]
                            #
                            #                         deadline = sh_message_wizard[message_wizard][1]
                            #                         notifications_text = str(
                            #                             sh_message_wizard[message_wizard][6]) if \
                            #                             sh_message_wizard[message_wizard][6] else ''
                            #                         notifications_text_ar = str(
                            #                             sh_message_wizard[message_wizard][0]) if \
                            #                             sh_message_wizard[message_wizard][0] else ''
                            #
                            #                         notifications += get_bus_notifition_student_new(school_name,
                            #                                                                         fname,
                            #                                                                         notifications_text,
                            #                                                                         sh_message_wizard[
                            #                                                                             message_wizard][
                            #                                                                             2],
                            #                                                                         deadline, rec_s,
                            #                                                                         None,
                            #                                                                         std[0],
                            #                                                                         sh_message_wizard[
                            #                                                                             message_wizard][
                            #                                                                             5],
                            #                                                                         notifications_text_ar,fname_ar)
                            #
                            #
                            #             if student_round_h:
                            #
                            #                 cursor.execute(
                            #                     "select  id,round_start from round_history WHERE round_id in %s and round_name in %s ORDER BY ID DESC LIMIT 1 ",
                            #                     [tuple(student_round_h), tuple(student_round_h)])
                            #                 round_history = cursor.fetchall()
                            #
                            #                 if round_history:
                            #                     history_round = []
                            #
                            #                     for round_h in round_history:
                            #                         history_round.append(round_h[0])
                            #                     for std in student_info:
                            #
                            #                         cursor.execute(
                            #                             "select  datetime,id,time_out,bus_check_in from round_student_history WHERE round_id in %s and student_id = %s and history_id in %s  ORDER BY ID DESC LIMIT 1 ",
                            #                             [tuple(student_round_h), std[0], tuple(history_round)])
                            #                         student_history = cursor.fetchall()
                            #
                            #                         if student_history:
                            #
                            #                             for student_history1 in student_history:
                            #                                 if student_history1[3]:
                            #
                            #                                     if student_history1[1] in student_history_id:
                            #                                         continue
                            #                                     else:
                            #                                         student_history_id.append(student_history1[1])
                            #
                            #                                         cursor.execute(
                            #                                             "select time_out,student_id,bus_check_in from round_student_history WHERE id = %s  ",
                            #                                             [student_history1[1]])
                            #                                         time_out = cursor.fetchall()
                            #                                         if time_out:
                            #                                             cursor.execute(
                            #                                                 "select  display_name_search,name,name_ar from student_student WHERE  id = %s",
                            #                                                 [time_out[0][1]])
                            #                                             name = cursor.fetchall()
                            #
                            #                                             if time_out[0][0] and time_out[0][2]:
                            #                                                 if any('English'  in x[0]  for x in lang):
                            #                                                     if name[0][1]:
                            #                                                         fname = name[0][1]
                            #                                                     else:
                            #                                                         fname = name[0][2]
                            #
                            #                                                 else:
                            #                                                     if not name[0][2]:
                            #                                                         fname = name[0][1]
                            #                                                     else:
                            #                                                         fname = name[0][2]
                            #
                            #                                                 deadline = time_out[0][0] if time_out[0][
                            #                                                     0] else time_out[0][2]
                            #
                            #                                                 notifications.append(
                            #                                                     get_info_message_new(deadline,
                            #                                                                      fname + " has just reached the school.  ",
                            #                                                                      avatar,
                            #                                                                      deadline.replace(
                            #                                                                          second=0) if deadline else '',
                            #                                                                      "Bus notification",
                            #                                                                      fname, time_out[0][1],0,None,None,'0',"اشعار من الحافلة"," وصل إلى المدرسة."+ fname))

                            notifications.sort(key=get_year, reverse=True)


                            for d in notifications:
                                # t = tuple(d.items())
                                t = (d['student_id'], d['notifications_text'],d['create_date'],d['date_time'],d['student_name'],d['notifications_title'],d['notificationsType'],d['notificationsType'])
                                # (d['student_id'], d['notifications_text'])
                                if t not in seen:
                                    seen.add(t)
                                    notifications_not_d.append(d)
                                    date_string = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                    r = datetime.datetime.strptime(date_string, '%Y-%m-%d %H:%M:%S')
                                    # print(d['notifications_text_ar'],d['notifications_title'])
                                    #   return {
                                    #             "avatar": avatar,
                                    #             "date_time": date_time(deadline),
                                    #             "notifications_text": notifications_text,
                                    #             "create_date": create_date,
                                    #             "notifications_title": notifications_title,
                                    #             "student_id": str(student_id),
                                    #             "notificationsType": notificationsType,
                                    #             "icon_tracking":icon_tracking,
                                    #             "id":id,
                                    #             "stutes":stutes,
                                    #             "show":show,
                                    #             "student_image": student_image,
                                    #             "action_id": str(action_id),
                                    #             "notifications_text_ar": notifications_text_ar if notifications_text_ar else notifications_text,
                                    #             "notifications_title_ar": notifications_title_ar if notifications_title_ar else notifications_title,
                                    #
                                    #         }
                                    # cursor.execute(
                                    #     "select  year_id,user_id from student_student WHERE id = %s",
                                    #     [d['student_id']])
                                    # student_name = cursor.fetchall()
                                    # cursor.execute(
                                    #     " select branch_id from res_users where id=%s",
                                    #     [student_name[0][1]])
                                    # branch_id = cursor.fetchall()
                                    # cursor.execute(
                                    #     "INSERT INTO message_student(create_date, type, message_en,message_ar,title,title_ar,date,year_id,branch_id,student_id)VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);",
                                    #     [r, 'App\Model\drive', d['notifications_text'], d['notifications_text_ar'], d['notifications_title'], d['notifications_title_ar'], d['date_time'],student_name[0][0],branch_id[0][0],d['student_id']])


                            result = {"notifications": notifications_not_d}
                            # print(result)
                            return Response(result)
                    else:
                        result = {'status': 'error'}
                        return Response(result)
                else:
                    result = {'status': 'error Authorization'}
                    return Response(result)
            else:
                result = {'status': 'Not found Authorization'}
                return Response(result)
        else:
            result = {'status': 'Not found headers'}
            return Response(result)


def get_info_message(deadline, notifications_text, avatar, create_date, notifications_title, student_name, student_id):
    notificationsType = ''
    icon_tracking = ''
    if notifications_title == 'Weekly plan' or notifications_title == 'Assignment' or notifications_title == 'Homework' or notifications_title == 'Exam' or notifications_title == 'educational':
        notificationsType = 'educational'
    elif notifications_title == 'Pick Up By Parent' or notifications_title == 'Absence':
        notificationsType = 'Absence'
    elif notifications_title == 'School Departure' or notifications_title == 'Checkout Notification' or notifications_title == 'No Show Notification' or "has arrived at your home" in notifications_text or "has just reached the school." in notifications_text or "has just been checked into the bus." in notifications_text or notifications_title == "Absence notification" or 'Message from bus no' in notifications_title:

        notificationsType = 'tracking'
        if (notifications_title == 'School Departure'):
            icon_tracking = 'https://trackware-schools.s3.eu-central-1.amazonaws.com/flutter_app/icons8-get-on-bus.svg'
        elif (notifications_title == 'Checkout Notification'):
            icon_tracking = 'https://trackware-schools.s3.eu-central-1.amazonaws.com/flutter_app/Absence.svg'
        elif (notifications_title == 'No Show Notification'):
            icon_tracking = 'https://trackware-schools.s3.eu-central-1.amazonaws.com/flutter_app/icons8-get-on-bus+(1).svg'
        elif "has arrived at your home" in notifications_text:
            icon_tracking = 'https://trackware-schools.s3.eu-central-1.amazonaws.com/flutter_app/icons8-house+(1).svg'
        elif "has just reached the school." in notifications_text:
            icon_tracking = 'https://trackware-schools.s3.eu-central-1.amazonaws.com/flutter_app/Absence.svg'
        elif "has just been checked into the bus." in notifications_text:
            icon_tracking = 'https://trackware-schools.s3.eu-central-1.amazonaws.com/flutter_app/icons8-get-on-bus.svg'
        elif notifications_title == "Absence notification":
            icon_tracking = 'https://trackware-schools.s3.eu-central-1.amazonaws.com/flutter_app/Absence.svg'
        else:
            icon_tracking = 'https://trackware-schools.s3.eu-central-1.amazonaws.com/flutter_app/icons8-shuttle-bus.svg'
    else:

        notificationsType = 'announcement'
    if student_name:
        return {
            "avatar": avatar,
            "date_time": date_time(deadline),
            "notifications_text": notifications_text,
            "create_date": create_date,
            "notifications_title": notifications_title,
            "student_name": student_name,
            "student_id": str(student_id),
            "notificationsType": notificationsType,
            "icon_tracking": icon_tracking

        }
    else:
        return {
            "avatar": avatar,
            "date_time": date_time(deadline),
            "notifications_text": notifications_text,
            "create_date": create_date,
            "notifications_title": notifications_title,
            "student_id": str(student_id),
            "notificationsType": notificationsType,
            "icon_tracking": icon_tracking
        }


# get school message
def get_school_message(student_id, school_name, school_message, student_name):
    notifications = []
    with connections[school_name].cursor() as cursor:
        message_ids = []
        for rec in school_message:
            message_ids.append(rec[0])
        message_ids = list(dict.fromkeys(message_ids))

        if message_ids:
            cursor.execute(
                "select  school_message_id from school_message_student_student WHERE school_message_id in %s AND student_student_id = %s",
                [tuple(message_ids), student_id])
            message_student = cursor.fetchall()
            message_id = []
            for rec in message_student:
                message_id.append(rec[0])

            if message_id:

                cursor.execute(
                    "select  id,search_type,title,message,create_date,date from school_message WHERE id in %s",
                    [tuple(list(dict.fromkeys(message_id)))])
                school_message1 = cursor.fetchall()

                for rec in range(len(school_message1)):
                    deadline = school_message1[rec][4]
                    notifications_text = school_message1[rec][3] if school_message1[rec][3] else ''
                    avatar = "https://s3.eu-central-1.amazonaws.com/notifications-images/mobile-notifications-icons/notification_icon_msg_admin.png"
                    create_date = school_message1[rec][4].replace(second=0) if school_message1[rec][4] else ''
                    notifications_title = school_message1[rec][2] if school_message1[rec][2] else ''

                    notifications.append(
                        get_info_message(deadline, notifications_text, avatar, create_date, notifications_title,
                                         student_name, student_id))

    return notifications


def get_student_history(student_id, school_name, student_name):
    notifications = []
    with connections[school_name].cursor() as cursor:
        list_hist_student = []
        cursor.execute(
            " SELECT  notification_id,round_id FROM student_history WHERE (activity_type='absent-all' or activity_type='absent') and student_id=%s",
            [student_id])
        student_history = cursor.fetchall()

        for mas in student_history:
            cursor.execute(
                "select  vehicle_id from transport_round WHERE id = %s",
                [mas[1]])

            vehicle_id = cursor.fetchall()
            cursor.execute(
                "select bus_no from fleet_vehicle WHERE id = %s  ",
                [vehicle_id[0][0]])
            bus_num = cursor.fetchall()

            if mas[0] in list_hist_student:
                continue
            else:
                list_hist_student.append(mas[0])

            cursor.execute(
                "select  message_en,create_date,type,id from sh_message_wizard WHERE id=%s ORDER BY ID DESC LIMIT 50",
                [mas[0]])
            sh_message_wizard1 = cursor.fetchall()

            for sh_message_bus in range(len(sh_message_wizard1)):
                deadline = sh_message_wizard1[sh_message_bus][1]

                notifications_text = sh_message_wizard1[sh_message_bus][0]
                avatar = "https://s3.eu-central-1.amazonaws.com/notifications-images/mobile-notifications-icons/notification_icon_check_in_drop.png"
                create_date = deadline.replace(second=0) if deadline else ''
                notifications_title = "Message from bus no. " + str(bus_num[0][0]) + "   " + str(student_name)
                notifications_title_ar = str(student_name) + " " + str(
                    bus_num[0][0]) + "   " + "رسالة من الحافلة رقم . "
                notifications.append(
                    get_info_message(deadline, notifications_text, avatar, create_date, notifications_title,
                                     student_name, student_id, 0, None, None, '0', notifications_title_ar,
                                     notifications_text))
    return notifications


def get_bus_notifition_student(school_name, student_name, notifications_text, notifications_title, deadline, round_id,
                               attendance_round, student_id):
    notifications = []

    avatar = "https://s3.eu-central-1.amazonaws.com/notifications-images/mobile-notifications-icons/notification_icon_check_in_drop.png"
    with connections[school_name].cursor() as cursor:
        create_date = deadline.replace(second=0) if deadline else ''
        cursor.execute(
            "select  vehicle_id from transport_round WHERE id = %s",
            [round_id])

        vehicle_id = cursor.fetchall()
        cursor.execute(
            "select bus_no from fleet_vehicle WHERE id = %s  ",
            [vehicle_id[0][0]])
        bus_num = cursor.fetchall()

        if "just been" in notifications_text:

            if str(student_name) in notifications_text:

                if notifications_title == 'School Departure':
                    notifications_title = 'School Departure'
                else:
                    notifications_title = 'Bus notification'
                notifications.append(
                    get_info_message(deadline, notifications_text, avatar, create_date, notifications_title,
                                     student_name, student_id))
        elif "did not check into the bus today" in notifications_text:

            if str(student_name) in notifications_text:
                notifications.append(
                    get_info_message(deadline, notifications_text, avatar, create_date, "No Show Notification",
                                     student_name, student_id))

        elif "has not checked into the bus" in notifications_text:

            if str(student_name) in notifications_text:
                notifications.append(
                    get_info_message(deadline, notifications_text, avatar, create_date, "Absence notification",
                                     student_name, student_id))


        elif "has arrived at your home and" in notifications_text:

            if str(student_name) in notifications_text:
                notifications.append(
                    get_info_message(deadline, notifications_text, avatar, create_date, "Checkout Notification",
                                     student_name, student_id))

        elif "just reached" in notifications_text:
            if str(student_name) in notifications_text:
                notifications.append(
                    get_info_message(deadline, notifications_text, avatar, create_date, "Bus notification",
                                     student_name, student_id))

        else:

            cursor.execute(
                "select  is_active,type from transport_round WHERE id = %s  ",
                [round_id])
            is_active = cursor.fetchall()

            time = ''
            if attendance_round:
                if is_active[0][1] == 'pick_up':
                    time = attendance_round[0][2]
                else:
                    time = attendance_round[0][3]
            notifications_title_ar = str(student_name) + " " + str(bus_num[0][0]) + "   " + "رسالة من الحافلة رقم . "
            if time:
                if time > deadline:
                    notifications.append(
                        get_info_message(deadline, notifications_text, avatar, create_date,
                                         "Message from bus no. " + str(
                                             bus_num[0][0]) + "  " + str(student_name), student_name, student_id, 0,
                                         None, None, '0', notifications_title_ar, notifications_text))


            else:
                notifications.append(
                    get_info_message(deadline, notifications_text, avatar, create_date, "Message from bus no. " + str(
                        bus_num[0][0]) + "  " + str(student_name), student_name, student_id, 0, None, None, '0',
                                     notifications_title_ar, notifications_text))
    return notifications


@api_view(['POST'])
def kids_hstory(request):
    if request.method == 'POST':
        if request.headers:
            if request.headers.get('Authorization'):
                if 'Bearer' in request.headers.get('Authorization'):
                    au = request.headers.get('Authorization').replace('Bearer', '').strip()

                    db_name = ManagerParent.objects.filter(token=au).values_list('db_name')
                    parent_id = ManagerParent.objects.filter(token=au).values_list('parent_id')

                    notifications = []
                    notifications_not_d = []
                    seen = set()
                    for e in parent_id:
                        parent_id = e[0]
                    if db_name:
                        for e in db_name:
                            school_name = e[0]
                        school_name = ManagerParent.pincode(school_name)
                        start_date = request.data.get('start_date')
                        end_date = request.data.get('end_date')
                        student_round = []
                        student_history_id = []
                        with connections[school_name].cursor() as cursor:
                            if start_date and end_date:
                                cursor.execute(
                                    "select  id  from school_message WHERE create_date >= %s AND create_date <= %s",
                                    [start_date, end_date])
                                school_message = cursor.fetchall()
                            elif start_date and not end_date:
                                cursor.execute(
                                    "select  id  from school_message WHERE create_date >= %s ",
                                    [start_date])

                                school_message = cursor.fetchall()
                            elif not start_date and end_date:
                                cursor.execute(
                                    "select  id  from school_message WHERE  create_date <= %s",
                                    [end_date])

                                school_message = cursor.fetchall()
                            elif not start_date and not end_date:
                                cursor.execute("select  id  from school_message ")
                                school_message = cursor.fetchall()
                            cursor.execute(
                                "select  id,display_name_search,image_url,name,name_ar from student_student WHERE (father_id = %s OR mother_id = %s OR responsible_id_value = %s)  And state = 'done'",
                                [parent_id, parent_id, parent_id])
                            student_info = cursor.fetchall()
                            student_round_id = []
                            cursor.execute(
                                "select first_lang  from res_company  ORDER BY ID DESC LIMIT 1")

                            first_lang = cursor.fetchall()
                            cursor.execute(
                                "select name from res_lang WHERE id = %s ",
                                [first_lang[0][0]])

                            lang = cursor.fetchall()
                            fname = ''

                            for student in student_info:

                                student_round = []
                                if "Arabic" not in lang:
                                    fname = student[3]

                                else:
                                    fname = student[4]
                                notifications += get_school_message(student[0], school_name, school_message, fname)
                                notifications += get_student_history(student[0], school_name, fname)
                                cursor.execute(
                                    "select  round_schedule_id from transport_participant WHERE student_id = %s",
                                    [student[0]])
                                round_schedule_id = cursor.fetchall()
                                #     get bus message
                                for rec in round_schedule_id:

                                    cursor.execute(
                                        "select  round_id from round_schedule WHERE id = %s",
                                        [rec[0]])
                                    round_schedule = cursor.fetchall()

                                    round_schedules = []
                                    student_round_h = []
                                    for rec in round_schedule:

                                        if rec[0] in student_round:

                                            continue
                                        else:
                                            cursor.execute(
                                                "select  type from transport_round WHERE id = %s",
                                                [rec[0]])

                                            type = cursor.fetchall()

                                            if type[0][0] == 'pick_up':
                                                student_round_h.append(rec[0])
                                            student_round.append(rec[0])
                                            round_schedules.append(rec[0])
                                    round_schedules = list(dict.fromkeys(student_round))

                                    for rec_s in round_schedules:
                                        if rec_s in student_round_id:
                                            pass
                                        else:
                                            student_round_id.append(rec_s)
                                            cursor.execute(
                                                "select  message_ar,create_date,type,round_id,id from sh_message_wizard WHERE round_id = %s and (type= %s or from_type =%s ) ORDER BY ID DESC LIMIT 50",
                                                [rec_s, 'emergency',
                                                 'App\Model\sta' + str(parent_id)])
                                            sh_message_wizard = cursor.fetchall()
                                            # save bus message
                                            for message_wizard in range(len(sh_message_wizard)):
                                                avatar = "https://s3.eu-central-1.amazonaws.com/notifications-images/mobile-notifications-icons/notification_icon_check_in_drop.png"
                                                for std in student_info:
                                                    if "Arabic" not in lang:
                                                        fname = std[3]

                                                    else:
                                                        fname = std[4]

                                                    cursor.execute(
                                                        "select  id,round_id,bus_check_in,time_out,history_id from round_student_history WHERE student_id = %s And driver_waiting is not  null  AND round_id=%s AND bus_check_in is  null AND  datetime >= %s AND  datetime < %s ",
                                                        [std[0], rec, datetime.datetime(
                                                            sh_message_wizard[message_wizard][1].year,
                                                            sh_message_wizard[message_wizard][1].month,
                                                            sh_message_wizard[message_wizard][1].day),
                                                         datetime.datetime(
                                                             sh_message_wizard[message_wizard][1].year,
                                                             sh_message_wizard[message_wizard][1].month,
                                                             sh_message_wizard[message_wizard][1].day + 1)])
                                                    attendance_round = cursor.fetchall()

                                                    if not attendance_round:
                                                        cursor.execute(
                                                            "select  is_active,type,write_date from transport_round WHERE id = %s  ",
                                                            [rec_s])
                                                        is_active = cursor.fetchall()
                                                        date_time_message = datetime.datetime(
                                                            sh_message_wizard[message_wizard][1].year,
                                                            sh_message_wizard[message_wizard][1].month,
                                                            sh_message_wizard[message_wizard][1].day)

                                                        car_time = datetime.datetime(datetime.datetime.now().year,
                                                                                     datetime.datetime.now().month,
                                                                                     datetime.datetime.now().day)

                                                        if (is_active[0][0] and car_time == date_time_message) or (
                                                                not is_active[0][0] and car_time == date_time_message):

                                                            cursor.execute(
                                                                "select  round_schedule_id from transport_participant WHERE student_id = %s",
                                                                [std[0]])
                                                            round_schedule_id_tst = cursor.fetchall()
                                                            schedule_id = []
                                                            for cha_round_s in round_schedule_id_tst:
                                                                schedule_id.append(cha_round_s[0])
                                                            if schedule_id:
                                                                cursor.execute(
                                                                    "select  round_id from round_schedule WHERE id in %s",
                                                                    [tuple(schedule_id)])
                                                                round_id_tst = cursor.fetchall()
                                                                round_id_student = []
                                                                for r_id in round_id_tst:
                                                                    round_id_student.append(r_id[0])
                                                                if rec_s in round_id_student:
                                                                    cursor.execute(
                                                                        "select  id,round_id,bus_check_in,time_out,history_id from round_student_history WHERE student_id = %s And driver_waiting is not  null  AND round_id=%s AND bus_check_in is not null AND  datetime >= %s AND  datetime < %s ",
                                                                        [std[0], rec, datetime.datetime(
                                                                            sh_message_wizard[message_wizard][1].year,
                                                                            sh_message_wizard[message_wizard][1].month,
                                                                            sh_message_wizard[message_wizard][1].day),
                                                                         datetime.datetime(
                                                                             sh_message_wizard[message_wizard][1].year,
                                                                             sh_message_wizard[message_wizard][1].month,
                                                                             sh_message_wizard[message_wizard][
                                                                                 1].day + 1)])
                                                                    attendance_round_yousef = cursor.fetchall()
                                                                    start = datetime.datetime(
                                                                        sh_message_wizard[message_wizard][1].year,
                                                                        sh_message_wizard[message_wizard][1].month,
                                                                        sh_message_wizard[message_wizard][1].day)
                                                                    end = datetime.datetime(
                                                                        sh_message_wizard[message_wizard][1].year,
                                                                        sh_message_wizard[message_wizard][1].month,
                                                                        sh_message_wizard[message_wizard][1].day + 1)
                                                                    if attendance_round_yousef:
                                                                        cursor.execute(
                                                                            "select  id,round_start,round_end,na from round_history WHERE id=%s",
                                                                            [attendance_round_yousef[0][4]])
                                                                        round_history = cursor.fetchall()
                                                                        cursor.execute(
                                                                            "select  activity_type,lat,long,datetime from student_history WHERE round_id = %s and student_id=%s and history_id = %s ORDER BY ID DESC  ",
                                                                            [rec_s, std[0], round_history[0][0]])
                                                                        student_history = cursor.fetchall()

                                                                        cursor.execute(
                                                                            "select  is_active,type,write_date from transport_round WHERE id = %s  ",
                                                                            [rec_s])
                                                                        is_active = cursor.fetchall()
                                                                        cursor.execute(
                                                                            "select  activity_type,lat,long from student_history WHERE round_id = %s and student_id=%s and datetime >= %s and datetime <= %s   ORDER BY ID DESC LIMIT 1 ",
                                                                            [rec_s, std[0],
                                                                             start, end])
                                                                        student_history1 = cursor.fetchall()

                                                                    cursor.execute(
                                                                        "select  activity_type,lat,long from student_history WHERE round_id = %s and student_id=%s and datetime >= %s and datetime <= %s   ORDER BY ID DESC LIMIT 1 ",
                                                                        [rec_s, std[0],
                                                                         start, end])
                                                                    student_history1 = cursor.fetchall()

                                                                    if student_history1:
                                                                        if student_history1[0][0] == 'absent' or \
                                                                                student_history1[0][0] == 'absent-all':
                                                                            continue

                                                                    deadline = sh_message_wizard[message_wizard][1]
                                                                    notifications_text = str(
                                                                        sh_message_wizard[message_wizard][0]) if \
                                                                        sh_message_wizard[message_wizard][0] else ''
                                                                    notifications += get_bus_notifition_student(
                                                                        school_name, fname,
                                                                        notifications_text,
                                                                        sh_message_wizard[message_wizard][2],
                                                                        deadline, rec_s,
                                                                        attendance_round_yousef, std[0])

                                                        continue
                                                    cursor.execute(
                                                        "select  id,round_start,round_end,na from round_history WHERE id=%s",
                                                        [attendance_round[0][4]])
                                                    round_history = cursor.fetchall()
                                                    cursor.execute(
                                                        "select  activity_type,lat,long,datetime from student_history WHERE round_id = %s and student_id=%s and history_id = %s ORDER BY ID DESC LIMIT 1 ",
                                                        [rec_s, std[0], round_history[0][0]])
                                                    student_history = cursor.fetchall()

                                                    cursor.execute(
                                                        "select  is_active,type,write_date from transport_round WHERE id = %s  ",
                                                        [rec_s])
                                                    is_active = cursor.fetchall()

                                                    if is_active[0][0]:

                                                        if sh_message_wizard[message_wizard][1] < round_history[0][1]:
                                                            deadline = sh_message_wizard[message_wizard][1]
                                                            notifications_text = str(
                                                                sh_message_wizard[message_wizard][0]) if \
                                                                sh_message_wizard[message_wizard][0] else ''

                                                            notifications += get_bus_notifition_student(school_name,
                                                                                                        fname,
                                                                                                        notifications_text,
                                                                                                        sh_message_wizard[
                                                                                                            message_wizard][
                                                                                                            2],
                                                                                                        deadline, rec_s,
                                                                                                        attendance_round,
                                                                                                        std[0])
                                                        if is_active[0][1] == 'pick_up':
                                                            if (student_history[0][0] == 'absent-all' or
                                                                student_history[0][0] == 'in' or
                                                                student_history[0][0] == 'Onboard' or
                                                                student_history[0][0] == 'absent' or
                                                                student_history[0][0] == 'no-show') and (
                                                                    sh_message_wizard[message_wizard][1] >
                                                                    student_history[0][3]):
                                                                continue
                                                            deadline = sh_message_wizard[message_wizard][1]
                                                            notifications_text = str(
                                                                sh_message_wizard[message_wizard][0]) if \
                                                                sh_message_wizard[message_wizard][0] else ''

                                                            notifications += get_bus_notifition_student(school_name,
                                                                                                        fname,
                                                                                                        notifications_text,
                                                                                                        sh_message_wizard[
                                                                                                            message_wizard][
                                                                                                            2],
                                                                                                        deadline, rec_s,
                                                                                                        attendance_round,
                                                                                                        std[0])
                                                        else:

                                                            if (student_history[0][0] == 'absent-all' or
                                                                student_history[0][0] == 'out' or
                                                                student_history[0][0] == 'Offboard' or
                                                                student_history[0][0] == 'absent' or
                                                                student_history[0][0] == 'no-show') and (
                                                                    sh_message_wizard[message_wizard][1] >
                                                                    student_history[0][3]):
                                                                continue

                                                            deadline = sh_message_wizard[message_wizard][1]
                                                            notifications_text = str(
                                                                sh_message_wizard[message_wizard][0]) if \
                                                                sh_message_wizard[message_wizard][0] else ''
                                                            notifications += get_bus_notifition_student(school_name,
                                                                                                        fname,
                                                                                                        notifications_text,
                                                                                                        sh_message_wizard[
                                                                                                            message_wizard][
                                                                                                            2],
                                                                                                        deadline, rec_s,
                                                                                                        attendance_round,
                                                                                                        std[0])
                                                    else:

                                                        if sh_message_wizard[message_wizard][1] < is_active[0][2]:

                                                            deadline = sh_message_wizard[message_wizard][1]
                                                            notifications_text = str(
                                                                sh_message_wizard[message_wizard][0]) if \
                                                                sh_message_wizard[message_wizard][0] else ''

                                                            if (sh_message_wizard[message_wizard][1] <
                                                                    student_history[0][3]):
                                                                notifications += get_bus_notifition_student(school_name,
                                                                                                            fname,
                                                                                                            notifications_text,
                                                                                                            sh_message_wizard[
                                                                                                                message_wizard][
                                                                                                                2],
                                                                                                            deadline,
                                                                                                            rec_s,
                                                                                                            attendance_round,
                                                                                                            std[0])

                                        if student_round_h:

                                            cursor.execute(
                                                "select  id,round_start from round_history WHERE round_id in %s and round_name in %s ORDER BY ID DESC LIMIT 1 ",
                                                [tuple(student_round_h), tuple(student_round_h)])
                                            round_history = cursor.fetchall()

                                            if round_history:
                                                history_round = []

                                                for round_h in round_history:
                                                    history_round.append(round_h[0])
                                                for std in student_info:

                                                    cursor.execute(
                                                        "select  datetime,id,time_out,bus_check_in from round_student_history WHERE round_id in %s and student_id = %s and history_id in %s  ORDER BY ID DESC LIMIT 1 ",
                                                        [tuple(student_round_h), std[0], tuple(history_round)])
                                                    student_history = cursor.fetchall()

                                                    #
                                                    if student_history:

                                                        for student_history1 in student_history:
                                                            if student_history1[3]:

                                                                if student_history1[1] in student_history_id:
                                                                    continue
                                                                else:
                                                                    student_history_id.append(student_history1[1])

                                                                    cursor.execute(
                                                                        "select time_out,student_id,bus_check_in from round_student_history WHERE id = %s  ",
                                                                        [student_history1[1]])
                                                                    time_out = cursor.fetchall()
                                                                    if time_out:
                                                                        cursor.execute(
                                                                            "select  display_name_search,name,name_ar from student_student WHERE  id = %s",
                                                                            [time_out[0][1]])
                                                                        name = cursor.fetchall()

                                                                        if time_out[0][0] and time_out[0][2]:
                                                                            if "Arabic" not in lang:
                                                                                if name[0][1]:
                                                                                    fname = name[0][1]
                                                                                else:
                                                                                    fname = name[0][2]

                                                                            else:
                                                                                if not name[0][2]:
                                                                                    fname = name[0][1]
                                                                                else:
                                                                                    fname = name[0][2]

                                                                            deadline = time_out[0][0] if time_out[0][
                                                                                0] else time_out[0][2]

                                                                            notifications.append(
                                                                                get_info_message(deadline,
                                                                                                 fname + " has just reached the school.  ",
                                                                                                 avatar,
                                                                                                 deadline.replace(
                                                                                                     second=0) if deadline else '',
                                                                                                 "Bus notification",
                                                                                                 fname, time_out[0][1]))

                            notifications.sort(key=get_year, reverse=True)

                            for d in notifications:
                                t = tuple(d.items())
                                if t not in seen:
                                    seen.add(t)
                                    notifications_not_d.append(d)

                            result = {"notifications": notifications_not_d}
                            return Response(result)
                    else:
                        result = {'status': 'error'}
                        return Response(result)
                else:
                    result = {'status': 'error Authorization'}
                    return Response(result)
            else:
                result = {'status': 'Not found Authorization'}
                return Response(result)
        else:
            result = {'status': 'Not found headers'}
            return Response(result)


def get_year(element):
    return element['date_time']


@api_view(['POST'])
def pre_arrive(request):
    if request.method == 'POST':
        if request.headers:
            if request.headers.get('Authorization'):
                if 'Bearer' in request.headers.get('Authorization'):
                    au = request.headers.get('Authorization').replace('Bearer', '').strip()
                    db_name = ManagerParent.objects.filter(token=au).values_list('db_name')
                    parent_id = ManagerParent.objects.filter(token=au).values_list('parent_id')
                    for e in parent_id:
                        parent_id = e[0]
                    if db_name:
                        for e in db_name:
                            school_name = e[0]

                        school_name = ManagerParent.pincode(school_name)

                        status = request.data.get('status')
                        student_id = request.data.get('student_id')

                        with connections[school_name].cursor() as cursor:
                            cursor.execute(
                                "select  display_name_search,year_id,user_id from student_student WHERE id = %s",
                                [student_id])
                            student_name = cursor.fetchall()
                            cursor.execute(
                                " select branch_id from res_users where id=%s",
                                [student_name[0][2]])
                            branch_id = cursor.fetchall()

                            cursor.execute(
                                "select  id,date,state from pickup_request WHERE name = %s AND parent_id = %s ORDER BY ID DESC LIMIT 1",
                                [student_name[0][0], parent_id])
                            date_t = cursor.fetchall()
                            if date_t:
                                if not (date_t[0][1].strftime('%Y-%m-%d') == datetime.datetime.now().strftime(
                                        '%Y-%m-%d')):
                                    date_string = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                    r = datetime.datetime.strptime(date_string, '%Y-%m-%d %H:%M:%S')
                                    cursor.execute(
                                        "INSERT INTO  pickup_request (date,name,pick_up_by,source,state,parent_id,write_date,year_id,branch_id,create_date) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s); ",
                                        [r, student_name[0][0], 'family_member', 'app', 'draft', parent_id, r,
                                         student_name[0][1], branch_id[0][0], r])
                                    cursor.execute(
                                        "select  id from pickup_request WHERE name = %s AND parent_id = %s ORDER BY ID DESC LIMIT 1",
                                        [student_name[0][0], parent_id])
                                    pickup_id = cursor.fetchall()
                                    cursor.execute(
                                        "INSERT INTO  pickup_request_student_student_rel (pickup_request_id,student_student_id) VALUES (%s,%s); ",
                                        [pickup_id[0][0], student_id])
                                    result = {'result': True}
                                    return Response(result)
                                else:
                                    if date_t[0][2] == 'waiting':
                                        cursor.execute(
                                            "UPDATE public.pickup_request SET state=%s WHERE id=%s;",
                                            ['done', date_t[0][0]])
                                        result = {'result': True}
                                        return Response(result)
                                    elif date_t[0][2] == 'draft':
                                        result = {'status': 'error'}
                                        return Response(result)
                                    elif date_t[0][2] == 'done':
                                        result = {'status': 'error'}
                                        return Response(result)
                            else:
                                q = "INSERT INTO  pickup_request (name,pick_up_by, parent_id,date,source,state) VALUES (%s, %s,%s, %s,%s); ", [
                                    student_name[0][0], 'family_member', '1', datetime.datetime.now(), 'app', 'draft']

                                date_string = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                r = datetime.datetime.strptime(date_string, '%Y-%m-%d %H:%M:%S')

                                cursor.execute(
                                    "INSERT INTO  pickup_request (date,name,pick_up_by,source,state,parent_id,write_date,year_id,branch_id,create_date) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s); ",
                                    [r, student_name[0][0], 'family_member', 'app', 'draft', parent_id, r,
                                     student_name[0][1], branch_id[0][0], r])
                                cursor.execute(
                                    "select  id from pickup_request WHERE name = %s AND parent_id = %s ORDER BY ID DESC LIMIT 1",
                                    [student_name[0][0], parent_id])
                                pickup_id = cursor.fetchall()
                                cursor.execute(
                                    "INSERT INTO  pickup_request_student_student_rel (pickup_request_id,student_student_id) VALUES (%s,%s); ",
                                    [pickup_id[0][0], student_id])

                                result = {'result': True}

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
        if request.headers:
            if request.headers.get('Authorization'):
                if 'Bearer' in request.headers.get('Authorization'):
                    au = request.headers.get('Authorization').replace('Bearer', '').strip()
                    db_name = ManagerParent.objects.filter(token=au).values_list('db_name')

                    if db_name:
                        for e in db_name:
                            school_name = e[0]

                        school_name = ManagerParent.pincode(school_name)
                        type = request.data.get('location_type')
                        date = request.data.get('date')
                        student_id = request.data.get('student_id')
                        name = request.data.get('name')
                        lat = request.data.get('lat')
                        long = request.data.get('long')
                        if name == 'childs_attendance':

                            parent_id = ManagerParent.objects.filter(token=au).values_list('parent_id')
                            for e in parent_id:
                                parent_id = e[0]
                            sender_id = parent_id
                            when = request.data.get('when')
                            date_absent = when
                            when = datetime.datetime.strptime(when + ' 00:00:00', '%d/%m/%Y %H:%M:%S')
                            target_rounds = request.data.get('target_rounds')
                            # round_id=request.data.get('status')
                            with connections[school_name].cursor() as cursor:
                                type = "absent-all" if target_rounds == 'both' else "absent"

                                cursor.execute(
                                    "select  display_name_search,year_id,user_id from student_student WHERE id = %s",
                                    [student_id])

                                student_name = cursor.fetchall()
                                cursor.execute("select  display_name_search from school_parent WHERE id = %s",
                                               [sender_id])

                                sender_name = cursor.fetchall()
                                message_en = "	My child  " + student_name[0][0] + " will be absent on " + str(
                                    date_absent) + " .So please do not pass by my home for pickup"
                                date_string = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                r = datetime.datetime.strptime(date_string, '%Y-%m-%d %H:%M:%S')

                                cursor.execute(
                                    " select branch_id from res_users where id=%s",
                                    [student_name[0][2]])
                                branch_id = cursor.fetchall()
                                cursor.execute(
                                    "INSERT INTO message_student(create_date, type, message_en,message_ar,title,title_ar,date,year_id,branch_id,student_id)VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);",
                                    [r, 'App\Model\Parents', message_en, message_en, 'Absence notification',
                                     'Absence notification', r, student_name[0][1], branch_id[0][0], student_id])
                                cursor.execute(
                                    "INSERT INTO sh_message_wizard(create_date,from_type, type, message_en,sender_name)VALUES (%s,%s,%s,%s,%s);",
                                    [r, 'App\Model\Parents', type, message_en, sender_name[0][0]])

                                cursor.execute("SELECT currval(pg_get_serial_sequence('sh_message_wizard','id'))",
                                               [])

                                notification_id = cursor.fetchall()

                                cursor.execute("select  display_name_search from school_parent WHERE id = %s",
                                               [sender_id])

                                sender_name = cursor.fetchall()

                                curr_date = datetime.datetime.today()
                                cursor.execute(
                                    "select  id  from school_day where name = %s",
                                    [calendar.day_name[curr_date.weekday()]])
                                day_id = cursor.fetchall()
                                cursor.execute(
                                    "select  round_schedule_id from transport_participant WHERE student_id = %s",
                                    [student_id])
                                round_schedule_id = cursor.fetchall()
                                r_id = []
                                for rec in round_schedule_id:
                                    r_id.append(rec[0])
                                if r_id:

                                    cursor.execute(
                                        "select id,round_id from round_schedule WHERE id in %s and day_id =%s",
                                        [tuple(r_id), day_id[0][0]])
                                    rounds_details = cursor.fetchall()
                                    cursor.execute(
                                        "select activity_type from student_history WHERE student_id = %s and datetime >= %s  ",
                                        [student_id, when])
                                    student_history = cursor.fetchall()
                                    result = {'result': "attendance"}
                                    student_history1 = []
                                    for res in student_history:
                                        student_history1.append(res[0])

                                    if "in" in student_history1 or "out" in student_history1 or "absent" in student_history1 or 'absent-all' in student_history1:
                                        if "in" in student_history1 or "out" in student_history1:
                                            result = {'result': "checked"}
                                        pass
                                    else:
                                        student_history = []
                                    if not student_history:
                                        if target_rounds == 'both':
                                            for res in rounds_details:
                                                cursor.execute(
                                                    "select driver_id from transport_round WHERE id = %s",
                                                    [res[1]])
                                                round_info = cursor.fetchall()
                                                cursor.execute("select token from res_partner WHERE id = %s",
                                                               [round_info[0][0]])
                                                driver_name = cursor.fetchall()
                                                # print(driver_name[0][0])
                                                if driver_name[0][0]:
                                                    send_driver_notif(driver_name[0][0], student_id, student_name[0][0],
                                                                      res[1], 'both', when)

                                                cursor.execute(
                                                    "INSERT INTO student_history(lat,long, student_id, round_id,datetime,activity_type,notification_id)VALUES (%s,%s,%s,%s,%s,%s,%s);",
                                                    [lat, long, student_id, res[1], when, "absent-all",
                                                     notification_id[0][0]])
                                                cursor.execute(
                                                    "INSERT INTO round_student_history(student_id,round_id,datetime)VALUES (%s,%s,%s);",
                                                    [student_id, res[1], when])

                                                cursor.execute(
                                                    "UPDATE   transport_participant SET transport_state=%s  WHERE student_id = %s and round_schedule_id = %s",
                                                    ['absent-all', student_id, res[0]])
                                        else:
                                            round_id = []
                                            for rec in rounds_details:
                                                round_id.append(rec[1])

                                            cursor.execute(
                                                "select id from transport_round WHERE id in %s and  type=%s",
                                                [tuple(round_id), 'pick_up'])
                                            rounds_details = cursor.fetchall()

                                            for res in rounds_details:
                                                cursor.execute(
                                                    "select driver_id from transport_round WHERE id = %s",
                                                    [res[0]])
                                                round_info = cursor.fetchall()
                                                cursor.execute("select signup_token from res_partner WHERE id = %s",
                                                               [round_info[0][0]])
                                                driver_name = cursor.fetchall()
                                                send_driver_notif(driver_name[0][0], student_id, student_name[0][0],
                                                                  res[0], "morning", when)
                                                cursor.execute(
                                                    "INSERT INTO student_history(lat,long, student_id, round_id,datetime,activity_type,notification_id)VALUES (%s,%s,%s,%s,%s,%s,%s);",
                                                    [lat, long, student_id, res[0], when,
                                                     'absent', notification_id[0][0]])
                                                cursor.execute(
                                                    "INSERT INTO round_student_history( student_id, round_id,datetime)VALUES (%s,%s,%s);",
                                                    [student_id, res[0], when])
                                                cursor.execute(
                                                    "UPDATE   transport_participant SET transport_state=%s  WHERE student_id = %s and round_schedule_id = %s",
                                                    ['absent', student_id, res[0]])
                                        result = {'result': "ok"}
                                return Response(result)
                        elif name == 'changed_location':
                            with connections[school_name].cursor() as cursor:
                                parent_id = ManagerParent.objects.filter(token=au).values_list('parent_id')
                                for e in parent_id:
                                    parent_id = e[0]
                                sender_id = parent_id
                                if type == 'drop-off':

                                    cursor.execute(
                                        "UPDATE   student_student SET drop_off_lat=%s ,drop_off_lng=%s WHERE id = %s",
                                        [lat, long, student_id])
                                    result = {'result': "ok"}

                                    return Response(result)
                                elif type == 'pick-up':

                                    cursor.execute(
                                        "UPDATE   student_student SET pick_up_lat=%s ,pick_up_lng=%s WHERE id = %s",
                                        [lat, long, student_id])
                                    result = {'result': "ok"}
                                    return Response(result)
                                elif type == 'both':
                                    cursor.execute(
                                        "UPDATE  student_student SET pick_up_lat=%s ,pick_up_lng=%s,drop_off_lat=%s,drop_off_lng=%s WHERE id = %s",
                                        [lat, long, lat, long, student_id])
                                    result = {'result': "ok"}
                                    return Response(result)
                        elif name == 'confirmed_pick':

                            with connections[school_name].cursor() as cursor:
                                parent_id = ManagerParent.objects.filter(token=au).values_list('parent_id')
                                for e in parent_id:
                                    parent_id = e[0]
                                cursor.execute("select  display_name_search from student_student WHERE id = %s",
                                               [student_id])
                                student_name = cursor.fetchall()
                                cursor.execute(
                                    "select  id,date,state from pickup_request WHERE name = %s AND parent_id = %s ORDER BY ID DESC LIMIT 1",
                                    [student_name[0][0], parent_id])
                                date_t = cursor.fetchall()
                                if date_t:
                                    cursor.execute(
                                        "UPDATE public.pickup_request SET picked_up_par=%s WHERE id=%s",
                                        ['confirmed', date_t[0][0]])
                                    result = {'result': True}
                                    return Response(result)


def send_driver_notif(mobile_token, student_id, student_name, round_id, type, when):
    # AAAAXj2DTK0:APA91bFSxi4txQ8WffLYLBrxFVd3JMCSP5n9WfZafPnLpxC2i9cXHi2SofNoNSBgFWt2tgqjEstSeVkre-1FklyKn4NIy0AuYSwafkQt-RhXcVCth3RJdt8GUbTw9aZI70XFmYBshjuy
    # push_service = FCMNotification(
    #         api_key="AAAAXj2DTK0:APA91bFSxi4txQ8WffLYLBrxFVd3JMCSP5n9WfZafPnLpxC2i9cXHi2SofNoNSBgFWt2tgqjEstSeVkre-1FklyKn4NIy0AuYSwafkQt-RhXcVCth3RJdt8GUbTw9aZI70XFmYBshjuy")
    push_service = FCMNotification(
        api_key="AAAAzysR6fk:APA91bFX6siqzUm-MQdhOWlno2PCOMfFVFIHmcfzRwmStaQYnUUJfDZBkC2kd2_s-4pk0o5jxrK9RsNiQnm6h52pzxDbfLijhXowIvVL2ReK7Y0FdZAYzmRekWTtOwsyG4au7xlRz1zD")
    registration_id = mobile_token
    message_title = ""
    message_body = "Today, the student  " + student_name + " is absent, So please do not pass by for pickup."
    # message_body = "The student " + student_name + "will be absent on" + str(
    #     when) + ". So please do not pass by my home for pickup."
    # if(type=="morning"):
    #     message_title = "Absent Only Morning"
    # else:
    #     message_title = "Absent All Day "
    message_title = 'Round\'s Absence'
    result = push_service.notify_single_device(registration_id=registration_id, message_title=message_title,
                                               message_body=message_body, message_icon="",
                                               data_message={"json_data": json.dumps(
                                                   {"student_id": student_id, "status": "absent",
                                                    "student_name": student_name, "round_id": round_id,
                                                    "date_time": ""})}
                                               )


@api_view(['GET'])
def get_badge(request, student_id):
    if request.method == 'GET':
        if request.headers:
            if request.headers.get('Authorization'):
                if 'Bearer' in request.headers.get('Authorization'):
                    au = request.headers.get('Authorization').replace('Bearer', '').strip()
                    db_name = ManagerParent.objects.filter(token=au).values_list('db_name')

                    if db_name:
                        for e in db_name:
                            school_name = e[0]
                    with connections[school_name].cursor() as cursor:
                        # academic.year
                        cursor.execute(
                            "select  id  from academic_year WHERE state = %s",
                            ['active'])
                        academic_year = cursor.fetchall()
                        academic_year_ids = []
                        data = []
                        new_add = False
                        for rec in academic_year:
                            academic_year_ids.append(rec[0])
                        cursor.execute(
                            "select  school_badge_id,teacher_id,subject_id,date,new_badge,id,new_added  from badge_badge WHERE student_id = %s AND year_id in %s  ORDER BY ID DESC",
                            [student_id, tuple(academic_year_ids)])
                        badges = cursor.fetchall()

                        for b in badges:
                            cursor.execute(
                                "select  *  from student_seen WHERE student_id = %s AND model_name = 'badge.badge' And rec_id = %s   ORDER BY ID DESC",
                                [student_id, b[5]])
                            student_seen = cursor.fetchall()

                            new_add = len(student_seen) == 0 or new_add
                            if new_add:
                                cursor.execute(
                                    "INSERT INTO student_seen(model_name,student_id,rec_id)VALUES (%s,%s,%s);",
                                    ['badge.badge', student_id, b[5]])
                            cursor.execute(
                                "select  name,description,image_url  from school_badge WHERE id = %s ",
                                [b[0]])
                            school_badge = cursor.fetchall()

                            cursor.execute(
                                "select  name,image_url,job_id  from hr_employee WHERE id = %s ",
                                [b[1]])
                            teacher_name = cursor.fetchall()
                            cursor.execute(
                                "select  name from hr_job WHERE id = %s ",
                                [teacher_name[0][2]])
                            job_name = cursor.fetchall()

                            subject_name = ''
                            delta = ''
                            if b[2]:
                                cursor.execute(
                                    "select  name  from school_subject WHERE id = %s ",
                                    [b[2]])
                                subject_name = cursor.fetchall()
                                cursor.execute(
                                    "select badge_duration from res_company",
                                    [])
                                badge_duration = cursor.fetchall()

                                d0 = date(b[3].year, b[3].month, b[3].day)
                                d1 = date(datetime.datetime.now().year, datetime.datetime.now().month,
                                          datetime.datetime.now().day)
                                delta = d1 - d0

                            data.append({'name': school_badge[0][0],
                                         'date': b[3].strftime("%d %b %Y"),
                                         'image': 'https://trackware-schools.s3.eu-central-1.amazonaws.com/' + str(
                                             school_badge[0][2]) if school_badge[0][2] else "",
                                         'id': b[5],
                                         'teacher': teacher_name[0][0],
                                         'subject': subject_name[0][0] if subject_name else '',
                                         'description': school_badge[0][1],
                                         'new_badge': b[4],
                                         'disable': delta.days < badge_duration[0][0] if delta else True,
                                         'job_name': job_name[0][0] if job_name else '',
                                         'image_teacher': 'https://trackware-schools.s3.eu-central-1.amazonaws.com/' + str(
                                             teacher_name[0][1]) if teacher_name[0][
                                             1] else "https://s3.eu-central-1.amazonaws.com/trackware.schools/public_images/default_student.png",

                                         })

                    result = {'result': data, 'new_add': new_add}
                    return Response(result)


@api_view(['GET'])
def get_calendar(request, student_id):
    if request.method == 'GET':
        if request.headers:
            if request.headers.get('Authorization'):
                if 'Bearer' in request.headers.get('Authorization'):
                    au = request.headers.get('Authorization').replace('Bearer', '').strip()
                    db_name = ManagerParent.objects.filter(token=au).values_list('db_name')

                    if db_name:
                        for e in db_name:
                            school_name = e[0]
                    with connections[school_name].cursor() as cursor:

                        cursor.execute(
                            "select user_id from student_student where id=%s",
                            [student_id])
                        user_id_q = cursor.fetchall()
                        if user_id_q:
                            cursor.execute(
                                " select partner_id from res_users where id=%s",
                                [user_id_q[0][0]])
                            partner_id_q = cursor.fetchall()
                            cursor.execute(
                                " select calendar_event_id from calendar_event_res_partner_rel where res_partner_id = %s ORDER BY calendar_event_id DESC",
                                [partner_id_q[0][0]])
                            calendar_event_id = cursor.fetchall()

                        data = []
                        for f_data in calendar_event_id:

                            cursor.execute(
                                " select id,name,start_datetime from calendar_event where id = %s ",
                                [f_data[0]])
                            event = cursor.fetchall()

                            if event[0][2] == None:

                                data.append({'id': event[0][0],
                                             'name': event[0][1],
                                             'start_date': event[0][2].strftime(
                                                 "%Y") if event[0][2] else '',
                                             'year': event[0][2].strftime("%Y") if event[0][2] else ''
                                             })
                            else:

                                data.append({'id': event[0][0],
                                             'name': event[0][1],
                                             'start_date': event[0][2].strftime("%d %b %Y"),
                                             'year': event[0][2],
                                             })

                    result = {'result': data}

                    return Response(result)


@api_view(['GET'])
def get_clinic(request, student_id):
    if request.method == 'GET':
        if request.headers:
            if request.headers.get('Authorization'):
                if 'Bearer' in request.headers.get('Authorization'):
                    au = request.headers.get('Authorization').replace('Bearer', '').strip()
                    db_name = ManagerParent.objects.filter(token=au).values_list('db_name')

                    if db_name:
                        for e in db_name:
                            school_name = e[0]

                    with connections[school_name].cursor() as cursor:
                        # academic.year
                        cursor.execute(
                            "select  id  from academic_year WHERE state = %s",
                            ['active'])
                        academic_year = cursor.fetchall()
                        academic_year_ids = []
                        data = []
                        cursor.execute(
                            "select user_id,year_id from student_student where id=%s",
                            [student_id])
                        user_id_q = cursor.fetchall()

                        if user_id_q:
                            for rec in academic_year:
                                academic_year_ids.append(rec[0])
                            if user_id_q:
                                cursor.execute(
                                    " select partner_id from res_users where id=%s",
                                    [user_id_q[0][0]])
                                partner_id_q = cursor.fetchall()
                                cursor.execute(
                                    " select id,name,date,note,temperature,blood_pressure,prescription from school_clinic where patient_id=%s and year_id = %s and state='done' ORDER BY ID DESC",
                                    [partner_id_q[0][0], user_id_q[0][1]])
                                vists = cursor.fetchall()

                            for v in vists:

                                try:
                                    date_s = datetime.datetime.strptime(str(v[2]), '%Y-%m-%d %H:%M:%S')
                                    data.append({'visit_id': v[0],
                                                 'name': v[1],
                                                 'date': date_s.strftime("%d %b %Y"),
                                                 'time': date_s.strftime("%I : %M %p"),
                                                 'note': v[3],
                                                 'temperature': v[4],
                                                 'blood_pressure': v[5],
                                                 'prescription': v[6] if v[6] else ""})
                                except:
                                    date_s = v[2]
                                    data.append({'visit_id': v[0],
                                                 'name': v[1],
                                                 'date': date_s,
                                                 'time': date_s,
                                                 'note': v[3],
                                                 'temperature': v[4],
                                                 'blood_pressure': v[5],
                                                 'prescription': v[6] if v[6] else ""})
                            result = {'result': data}
                        else:
                            result = {'result': data}

                    return Response(result)


@api_view(['GET'])
def get_attendance(request, student_id):
    if request.method == 'GET':
        if request.headers:
            if request.headers.get('Authorization'):
                if 'Bearer' in request.headers.get('Authorization'):
                    au = request.headers.get('Authorization').replace('Bearer', '').strip()
                    db_name = ManagerParent.objects.filter(token=au).values_list('db_name')

                    if db_name:
                        for e in db_name:
                            school_name = e[0]
                    with connections[school_name].cursor() as cursor:
                        absence_request = []
                        daily_attendance = []

                        cursor.execute(
                            "select display_name_search,year_id,user_id from student_student where id=%s",
                            [student_id])
                        user_id_q = cursor.fetchall()
                        cursor.execute(
                            " select branch_id from res_users where id=%s",
                            [user_id_q[0][2]])
                        branch_id = cursor.fetchall()
                        if user_id_q:
                            cursor.execute(
                                " select id,name,start_date,end_date,reason,type,state,arrival_time from student_absence_request where student_id=%s and year_id=%s and branch_id=%s ORDER BY id DESC",
                                [student_id, user_id_q[0][1], branch_id[0][0]])
                            studentleaves = cursor.fetchall()
                            cursor.execute(
                                "SELECT daily_attendance_id,id,note,reason,attendance_status,arrival_time FROM daily_attendance_line WHERE student_id=%s ORDER BY id DESC",
                                [student_id])
                            daily_attendance_line = cursor.fetchall()
                            for s in daily_attendance_line:
                                if not s[0]:
                                    continue
                                cursor.execute(
                                    "SELECT state,date FROM daily_attendance WHERE id = %s",
                                    [s[0]])
                                daily = cursor.fetchall()
                                if daily[0][0] == 'draft':
                                    continue
                                if s[4] == 'present':
                                    continue
                                if s[2] != False:
                                    daily_attendance.append({'leave_id': s[1],
                                                             'name': user_id_q[0][0],
                                                             'start_date': daily[0][1].strftime("%d %b %Y"),
                                                             'end_date': '30 Sep 2021',
                                                             'reason': 'Death of A Relative' if s[3] == 'death' else s[
                                                                 3],
                                                             'type': s[4],
                                                             'arrival_time': str(s[5]) if s[5] else "0"
                                                             })
                                else:
                                    daily_attendance.append({'leave_id': s[1],
                                                             'name': user_id_q[0][0],
                                                             'start_date': None,
                                                             'end_date': '30 Sep 2021',
                                                             'reason': 'Death of A Relative' if s[3] == 'death' else s[
                                                                 3],
                                                             'type': s[4],
                                                             'arrival_time': str(s[5]) if s[5] else "0"
                                                             })
                            for st in studentleaves:
                                arrival_time = calculate_time(st[7])

                                absence_request.append({'leave_id': st[0],
                                                        'name': st[1],
                                                        'start_date': st[2].strftime("%d %b %Y"),
                                                        'end_date': st[3].strftime("%d %b %Y"),
                                                        'reason': 'Death of A Relative' if st[4] == 'death' else (
                                                            st[4].capitalize() if st[4] else ""),
                                                        'type': st[5].capitalize() if st[5] else "",
                                                        'status': st[6].capitalize() if st[6] else "",
                                                        'arrival_time': arrival_time})
                    result = {'absence_request': absence_request,
                              'daily_attendance': daily_attendance}

                    return Response(result)


@api_view(['POST'])
def post_attendance(request):
    if request.method == 'POST':
        if request.headers:
            if request.headers.get('Authorization'):
                if 'Bearer' in request.headers.get('Authorization'):
                    au = request.headers.get('Authorization').replace('Bearer', '').strip()
                    db_name = ManagerParent.objects.filter(token=au).values_list('db_name')

                    if db_name:
                        for e in db_name:
                            school_name = e[0]

                        school_name = ManagerParent.pincode(school_name)
                        Session = request.data.get('session')
                        student_id = request.data.get('student_id')
                        start_date = request.data.get('start_date')
                        end_date = request.data.get('end_date')
                        type = request.data.get('type')
                        notes = request.data.get('notes')
                        departure_time = request.data.get('departure_time')
                        reason = request.data.get('Reason')
                        arrival_time = request.data.get('arrival_time')
                        base_url = request.data.get('base_url')
                        with connections[school_name].cursor() as cursor:

                            attached_files = request.data.get("file")
                            body = json.dumps({"jsonrpc": "2.0",
                                               "params": {"student_id": int(student_id), "attachments": attached_files,
                                                          "arrival_time": arrival_time,
                                                          "departure_time": departure_time, "type": type,
                                                          "start_date": start_date, "end_date": end_date,
                                                          "reason": reason, "notes": notes

                                                          }})
                            headers = {
                                'X-Openerp-Session-Id': Session,
                                'Content-Type': 'application/json',
                            }
                            url = base_url + "check_user_type1"
                            response1 = requests.request("POST", url,
                                                         headers=headers, data=body)

                            result = {'result': 'ok'}
                            return Response(result)
                result = {'result': 'Error Authorization'}
                return Response(result)
            result = {'result': 'Not Authorization'}
            return Response(result)


@api_view(['POST'])
def post_workSheet(request):
    if request.method == 'POST':
        if request.headers:
            if request.headers.get('Authorization'):
                if 'Bearer' in request.headers.get('Authorization'):
                    au = request.headers.get('Authorization').replace('Bearer', '').strip()
                    db_name = ManagerParent.objects.filter(token=au).values_list('db_name')

                    if db_name:
                        for e in db_name:
                            school_name = e[0]

                        school_name = ManagerParent.pincode(school_name)

                        Session = request.data.get('session')
                        student_id = request.data.get('student_id')
                        wk_id = request.data.get('wk_id')
                        base_url = request.data.get('base_url')
                        with connections[school_name].cursor() as cursor:
                            cursor.execute(
                                "select user_id from student_student where id=%s",
                                [student_id])
                            user_id_q = cursor.fetchall()

                            attached_files = request.data.get("file")
                            body = json.dumps({"jsonrpc": "2.0",
                                               "params": {"student_id": int(user_id_q[0][0]),
                                                          "attachments": attached_files,
                                                          "wk_id": wk_id,

                                                          }})
                            headers = {
                                'X-Openerp-Session-Id': Session,
                                'Content-Type': 'application/json',
                            }

                            url = str(base_url) + "upload_worksheet"

                            response1 = requests.request("POST", url,
                                                         headers=headers, data=body)

                            result = {'result': 'ok'}
                            return Response(result)
                result = {'result': 'Error Authorization'}
                return Response(result)
            result = {'result': 'Not Authorization'}
            return Response(result)


@api_view(['POST'])
def post_Event(request):
    if request.method == 'POST':
        if request.headers:
            if request.headers.get('Authorization'):
                if 'Bearer' in request.headers.get('Authorization'):
                    au = request.headers.get('Authorization').replace('Bearer', '').strip()
                    db_name = ManagerParent.objects.filter(token=au).values_list('db_name')

                    if db_name:
                        for e in db_name:
                            school_name = e[0]

                        school_name = ManagerParent.pincode(school_name)
                        Session = request.data.get('session')
                        student_id = request.data.get('student_id')
                        wk_id = request.data.get('wk_id')
                        base_url = request.data.get('base_url')
                        with connections[school_name].cursor() as cursor:
                            cursor.execute(
                                "select user_id from student_student where id=%s",
                                [student_id])
                            user_id_q = cursor.fetchall()

                            attached_files = request.data.get("file")
                            body = json.dumps({"jsonrpc": "2.0",
                                               "params": {"stu_id": int(student_id), "attachments": attached_files,
                                                          "user_id": int(student_id),
                                                          "wk_id": wk_id,

                                                          }})

                            headers = {
                                'X-Openerp-Session-Id': Session,
                                'Content-Type': 'application/json',
                            }

                            url = str(base_url) + "upload_events_flutter"
                            response1 = requests.request("POST", url,
                                                         headers=headers, data=body)

                            result = {'result': 'ok'}
                            return Response(result)
                result = {'result': 'Error Authorization'}
                return Response(result)
            result = {'result': 'Not Authorization'}
            return Response(result)


@api_view(['POST'])
def cancel_event(request):
    if request.method == 'POST':
        if request.headers:
            if request.headers.get('Authorization'):
                if 'Bearer' in request.headers.get('Authorization'):
                    au = request.headers.get('Authorization').replace('Bearer', '').strip()
                    db_name = ManagerParent.objects.filter(token=au).values_list('db_name')
                    if db_name:
                        for e in db_name:
                            school_name = e[0]
                        school_name = ManagerParent.pincode(school_name)
                        wk_id = request.data.get('wk_id')
                        with connections[school_name].cursor() as cursor:
                            cursor.execute(
                                "Update school_event_registration SET state = 'cancel'  WHERE id=%s",
                                [wk_id])
                            result = {'result': 'ok'}
                            return Response(result)
                result = {'result': 'Error Authorization'}
                return Response(result)
            result = {'result': 'Not Authorization'}
            return Response(result)


def calculate_time(time):
    if time <= 12:
        result_time = '{0:02.0f}:{1:02.0f}'.format(*divmod(time * 60, 60))
        result_time = result_time + '  am'
    else:
        time = time - 12
        result_time = '{0:02.0f}:{1:02.0f}'.format(*divmod(time * 60, 60))
        result_time = result_time + '  pm'
    return result_time


@api_view(['GET'])
def get_exam(request, student_id):
    if request.method == 'GET':
        if request.headers:
            if request.headers.get('Authorization'):
                if 'Bearer' in request.headers.get('Authorization'):
                    au = request.headers.get('Authorization').replace('Bearer', '').strip()
                    db_name = ManagerParent.objects.filter(token=au).values_list('db_name')

                    if db_name:
                        for e in db_name:
                            school_name = e[0]

                    with connections[school_name].cursor() as cursor:

                        cursor.execute(
                            "select  id  from academic_year WHERE state = %s",
                            ['active'])
                        academic_year = cursor.fetchall()
                        academic_year_ids = []
                        data = []
                        cursor.execute(
                            "select user_id,year_id from student_student where id=%s",
                            [student_id])
                        user_id_q = cursor.fetchall()

                        if user_id_q:
                            for rec in academic_year:
                                academic_year_ids.append(rec[0])
                            if user_id_q:
                                cursor.execute(
                                    " select partner_id,branch_id from res_users where id=%s",
                                    [user_id_q[0][0]])
                                partner_id_q = cursor.fetchall()
                                # print(partner_id_q,user_id_q)

                                data = []
                                state = 'new'
                                start = False
                                cursor.execute(
                                    " select id,survey_id,token,last_displayed_page_id,state from survey_user_input where partner_id=%s and year_id = %s and branch_id =%s   ORDER BY create_date DESC, state DESC",
                                    [partner_id_q[0][0], user_id_q[0][1], partner_id_q[0][1]])
                                assignments = cursor.fetchall()

                            for assingment in assignments:
                                # print(assingment)
                                cursor.execute(
                                    " select id,state,deadline,title,access_token,subject_id,allowed_time_to_start,time_limit,mark,exam_names from survey_survey where id=%s and certificate=%s",
                                    [assingment[1], True])
                                survey = cursor.fetchall()

                                if survey:
                                    # print("lllllllll", survey)

                                    cursor.execute(
                                        "select  name  from school_subject WHERE id = %s ",
                                        [survey[0][5]])
                                    subject_name = cursor.fetchall()

                                    cursor.execute(
                                        "SELECT * FROM allowed_enter_exam_student_survey_rel WHERE survey_survey_id = %s and student_student_id = %s  ",
                                        [survey[0][0], student_id])
                                    allowed_enter_exam_student_survey_rel = cursor.fetchall()
                                    allowed_to_enter_exam_after_time_limit = True if allowed_enter_exam_student_survey_rel else False

                                    cursor.execute(
                                        " select id  from survey_question where survey_id=%s and question_type != ''",
                                        [assingment[1]])
                                    survey_question = cursor.fetchall()

                                    cursor.execute(
                                        " select exam_name_english ,exam_name_arabic  from exam_name where id=%s",
                                        [survey[0][9]])
                                    exam_name = cursor.fetchall()

                                    cursor.execute(
                                        " select id  from survey_user_input_line where survey_id=%s",
                                        [assingment[1]])
                                    survey_user_input_line = cursor.fetchall()
                                    if survey[0][1] == 'open':
                                        if survey[0][2]:
                                            deadline = survey[0][2]
                                            # cursor.execute(
                                            #     """select timezone from transport_setting ORDER BY ID DESC LIMIT 1""")
                                            # transport_setting = cursor.fetchall()
                                            # date_tz = transport_setting[0][0]
                                            date_tz = 'Asia/Kuwait'
                                            deadline.replace(date_tz)
                                            deadline = deadline.replace(date_tz)
                                            deadline = datetime.strptime(deadline, "%d/%m/%Y %H:%M:%S")
                                            x = datetime.datetime.now().replace(date_tz)
                                            if start_time <= datetime.strptime(x, "%d/%m/%Y %H:%M:%S"):
                                                start = True
                                                state = 'done'
                                            else:
                                                if assingment[4] == 'done':
                                                    state = 'done'
                                                    start = False
                                                else:
                                                    state = assingment[4]
                                                    start = True
                                        else:
                                            start_time = ""
                                            state = assingment[4]
                                            start = False

                                        if start_time == '':
                                            start_time2 = ''
                                            now_time = ''
                                            exam_start_sss = ''
                                            allowed_time_to_start_exams = ''
                                            late_to_exams = ''
                                            exam_start_in = ''
                                            late_time = ''
                                        else:
                                            now = datetime.now()

                                            start_time2 = start_time
                                            dt_string = now.strftime("%Y/%m/%d %H:%M:%S")
                                            date_time_obj = datetime.strptime(dt_string, '%Y/%m/%d %H:%M:%S')
                                            now_time = date_time_obj + timedelta(hours=3)
                                            allowed_time_to_start = survey[6]
                                            allowed_time_to_start_exam = pd.to_datetime(allowed_time_to_start,
                                                                                        format='%M')
                                            exam_start_sss = start_time2 + timedelta(
                                                minutes=allowed_time_to_start_exam.minute)

                                            if type(start_time2) == str:
                                                print("")
                                            else:
                                                if start_time2 <= now_time <= exam_start_sss:
                                                    allowed_time_to_start_exams = True
                                                else:
                                                    allowed_time_to_start_exams = False

                                                if now_time >= exam_start_sss:
                                                    late_to_exams = True
                                                else:
                                                    late_to_exams = False

                                            late_time = now_time - exam_start_sss
                                            seconds = late_time.seconds
                                            seconds = seconds % (24 * 3600)
                                            hour = seconds // 3600
                                            seconds %= 3600
                                            minutes = seconds // 60
                                            seconds %= 60
                                            late_time = "%d:%02d:%02d" % (hour, minutes, seconds)

                                            exam_start_in = start_time2 - now_time
                                            seconds = exam_start_in.seconds
                                            seconds = seconds % (24 * 3600)
                                            hour = seconds // 3600
                                            seconds %= 3600
                                            minutes = seconds // 60
                                            seconds %= 60
                                            exam_start_in = "%d:%02d:%02d" % (hour, minutes, seconds)

                                        data.append({
                                            "id": assingment[0],
                                            "assignment_id": assingment[1],
                                            "name": survey[0][3] if survey[0][3] else '',
                                            "subject": subject_name[0][0] if subject_name[0][0] else '',
                                            "token": survey[0][4] if survey[0][4] else '',
                                            'answer_token': assingment[2] if assingment[2] else '',
                                            'questions_count': len(survey_question),
                                            "state": state,
                                            'last_displayed_page': "None",
                                            'answered_questions': len(survey_user_input_line),
                                            "ass_state": survey[0][1] if survey[0][1] else '',
                                            "start": start,
                                            'start_time': str(start_time) if start_time else 'None',
                                            'allowed_time_to_start_exams': str(
                                                allowed_time_to_start_exams) if allowed_time_to_start_exams else 'None',
                                            'allowed_enter_exam_student_ids': str(
                                                allowed_to_enter_exam_after_time_limit[0][
                                                    0]) if allowed_to_enter_exam_after_time_limit else "None",
                                            "exam_name_english": exam_name[0][0] if exam_name else 'None',
                                            "exam_name_arabic": exam_name[0][1] if exam_name else 'None',
                                            'mark': int(survey[0][8]),
                                            'time_limit': survey[0][7] if survey[0][7] else 0,
                                            'allowed_time_to_start': survey[0][6] if survey[0][6] else 0.0,
                                            'late_to_exams': late_to_exams if late_to_exams else "None",
                                            'late_time': late_time if late_time else "None",
                                            'exam_start_in': exam_start_in if exam_start_in else "None",
                                            'allowed_to_enter_exam_after_time_limit': True if allowed_to_enter_exam_after_time_limit else True
                                        })

                        result = {'result': data}
                        # print(result)

                    return Response(result)


@api_view(['GET'])
def get_student_assignment(request, student_id):
    if request.method == 'GET':
        if request.headers:
            if request.headers.get('Authorization'):
                if 'Bearer' in request.headers.get('Authorization'):
                    au = request.headers.get('Authorization').replace('Bearer', '').strip()
                    db_name = ManagerParent.objects.filter(token=au).values_list('db_name')

                    if db_name:
                        for e in db_name:
                            school_name = e[0]

                    with connections[school_name].cursor() as cursor:

                        cursor.execute(
                            "select  id  from academic_year WHERE state = %s",
                            ['active'])
                        academic_year = cursor.fetchall()
                        academic_year_ids = []
                        data = []
                        cursor.execute(
                            "select user_id,year_id from student_student where id=%s",
                            [student_id])
                        user_id_q = cursor.fetchall()

                        if user_id_q:
                            for rec in academic_year:
                                academic_year_ids.append(rec[0])
                            if user_id_q:
                                cursor.execute(
                                    " select partner_id,branch_id from res_users where id=%s",
                                    [user_id_q[0][0]])
                                partner_id_q = cursor.fetchall()

                                data = []
                                state = 'new'
                                start = False
                                cursor.execute(
                                    " select id,survey_id,token,last_displayed_page_id,state from survey_user_input where partner_id=%s and year_id = %s and branch_id =%s   ORDER BY create_date DESC, state DESC",
                                    [partner_id_q[0][0], user_id_q[0][1], partner_id_q[0][1]])
                                assignments = cursor.fetchall()

                            for assingment in assignments:

                                cursor.execute(
                                    " select id,state,deadline,title,access_token,subject_id from survey_survey where id=%s and is_assignment=%s",
                                    [assingment[1], True])
                                survey = cursor.fetchall()

                                if survey:

                                    cursor.execute(
                                        "select  name  from school_subject WHERE id = %s ",
                                        [survey[0][5]])
                                    subject_name = cursor.fetchall()
                                    cursor.execute(
                                        " select id  from survey_question where survey_id=%s and question_type != ''",
                                        [assingment[1]])
                                    survey_question = cursor.fetchall()
                                    cursor.execute(
                                        " select id  from survey_user_input_line where survey_id=%s",
                                        [assingment[1]])
                                    survey_user_input_line = cursor.fetchall()

                                    if survey[0][1] == 'open':
                                        dead = ''
                                        if survey[0][2]:
                                            deadline = survey[0][2]

                                            # cursor.execute(
                                            #     """select timezone from transport_setting ORDER BY ID DESC LIMIT 1""")
                                            # transport_setting = cursor.fetchall()
                                            # date_tz = transport_setting[0][0]
                                            date_tz = 'Asia/Kuwait'
                                            # deadline.replace(date_tz)
                                            # deadline = deadline.replace(date_tz)
                                            deadline = deadline.astimezone(pytz.timezone(date_tz))

                                            dead = str(deadline.day) + "/" + str(deadline.month) + "/" + str(
                                                deadline.year) + " " + str(deadline.hour) + ":" + str(
                                                deadline.minute) + ":" + str(deadline.second)
                                            deadline = datetime.datetime.strptime(str(dead), "%d/%m/%Y %H:%M:%S")

                                            x = datetime.datetime.now().astimezone(pytz.timezone(date_tz))
                                            cur_data = str(x.day) + "/" + str(x.month) + "/" + str(x.year) + " " + str(
                                                x.hour) + ":" + str(x.minute) + ":" + str(x.second)
                                            if deadline <= datetime.datetime.strptime(str(cur_data),
                                                                                      "%d/%m/%Y %H:%M:%S"):
                                                start = True
                                                state = 'done'
                                            else:
                                                if assingment[4] == 'done':
                                                    state = 'done'
                                                    start = False
                                                else:
                                                    state = assingment[4]
                                                    start = True
                                        else:
                                            deadline = ""
                                            state = assingment[4]
                                            start = False
                                        data.append({
                                            "id": assingment[0],
                                            "assignment_id": assingment[1],
                                            "name": survey[0][3] if survey[0][3] else '',
                                            "subject": subject_name[0][0] if subject_name[0][0] else '',
                                            "token": survey[0][4] if survey[0][4] else '',
                                            'answer_token': assingment[2] if assingment[2] else '',
                                            'questions_count': len(survey_question),
                                            "state": state,
                                            # 'last_displayed_page': assingment[3] if assingment[3] else ' gg' ,
                                            'answered_questions': len(survey_user_input_line),
                                            "ass_state": survey[0][1] if survey[0][1] else '',
                                            "deadline": dead,
                                            "start": start
                                        })

                        result = {'result': data}

                    return Response(result)


@api_view(['GET'])
def get_all_weekly_plans(request, student_id):
    if request.method == 'GET':
        if request.headers:
            if request.headers.get('Authorization'):
                if 'Bearer' in request.headers.get('Authorization'):
                    au = request.headers.get('Authorization').replace('Bearer', '').strip()
                    db_name = ManagerParent.objects.filter(token=au).values_list('db_name')

                    if db_name:
                        for e in db_name:
                            school_name = e[0]

                    with connections[school_name].cursor() as cursor:

                        cursor.execute(
                            "select  id  from academic_year WHERE state = %s",
                            ['active'])
                        academic_year = cursor.fetchall()
                        academic_year_ids = []
                        data = []
                        cursor.execute(
                            "select user_id,year_id from student_student where id=%s",
                            [student_id])
                        user_id_q = cursor.fetchall()
                        if user_id_q:
                            for rec in academic_year:
                                academic_year_ids.append(rec[0])
                            if user_id_q:
                                cursor.execute(
                                    " select partner_id,branch_id from res_users where id=%s",
                                    [user_id_q[0][0]])
                                partner_id_q = cursor.fetchall()

                                cursor.execute(
                                    " select id,name,date_from,date_to from week_plan where state='puplished' and year_id = %s and branch_id =%s   ORDER BY id DESC",
                                    [user_id_q[0][1], partner_id_q[0][1]])
                                week_plan = cursor.fetchall()
                                for p in week_plan:
                                    data.append({'id': p[0],
                                                 'plan_name': p[1],
                                                 'start_date': str(p[2].strftime("%d %b %Y")),
                                                 'end_date': str(p[3].strftime("%d %b %Y"))
                                                 })
                                result = {'result': data}

                                return Response(result)


@api_view(['GET'])
def get_weekly_plan_lines(request, plan_id, student_id, week_name):
    if request.method == 'GET':
        if request.headers:
            if request.headers.get('Authorization'):
                if 'Bearer' in request.headers.get('Authorization'):
                    au = request.headers.get('Authorization').replace('Bearer', '').strip()
                    db_name = ManagerParent.objects.filter(token=au).values_list('db_name')

                    if db_name:
                        for e in db_name:
                            school_name = e[0]

                    with connections[school_name].cursor() as cursor:

                        data = {}
                        days = []
                        cursor.execute(
                            "select user_id,year_id from student_student where id=%s",
                            [student_id])
                        student = cursor.fetchall()
                        if student:

                            cursor.execute(
                                " select partner_id from res_users where id=%s",
                                [student[0][0]])
                            partner_id = cursor.fetchall()
                            if partner_id:

                                cursor.execute(
                                    "select class_id from res_partner where id=%s",
                                    [partner_id[0][0]])
                                class_id = cursor.fetchall()
                                cursor.execute(
                                    "select enable_saturday,enable_sunday,enable_monday,enable_tuesday,enable_wednesday,enable_thursday,enable_friday,subject_id,notes,description_saturday,"
                                    "description_sunday,description_monday,description_tuesday,description_wednesday,description_thursday,description_friday,id from week_plan_lines where week_id=%s and class_id=%s and state ='approved'",
                                    [plan_id, class_id[0][0]])
                                lines = cursor.fetchall()

                                # 16
                                data['plan_name'] = week_name
                                for line in lines:
                                    if line[0] and 'Saturday' not in days:
                                        days.append('Saturday')
                                    if line[1] and 'Sunday' not in days:
                                        days.append('Sunday')
                                    if line[2] and 'Monday' not in days:
                                        days.append('Monday')
                                    if line[3] and 'Tuesday' not in days:
                                        days.append('Tuesday')
                                    if line[4] and 'Wednesday' not in days:
                                        days.append('Wednesday')
                                    if line[5] and 'Thursday' not in days:
                                        days.append('Thursday')
                                    if line[6] and 'Friday' not in days:
                                        days.append('Friday')
                                days = list(set(days))

                                columns = {'days': {}}

                                for day in days:
                                    if day == 'Saturday':
                                        columns['days'][0] = 'Saturday'
                                    if day == 'Sunday':
                                        columns['days'][1] = 'Sunday'
                                    if day == 'Monday':
                                        columns['days'][2] = 'Monday'
                                    if day == 'Tuesday':
                                        columns['days'][3] = 'Tuesday'
                                    if day == 'Wednesday':
                                        columns['days'][4] = 'Wednesday'
                                    if day == 'Thursday':
                                        columns['days'][5] = 'Thursday'
                                    if day == 'Friday':
                                        columns['days'][6] = 'Friday'
                                columns = sorted(columns['days'].items())
                                dayss = []

                                for col in columns:
                                    dayss.append({
                                        "id": col[0],
                                        "day": col[1]
                                    })
                                data['columns'] = dayss

                                subject_lines = []
                                for l in lines:
                                    cursor.execute(
                                        "select  name  from school_subject WHERE id = %s ",
                                        [l[7]])
                                    subject_name = cursor.fetchall()
                                    line = {'subject_id': l[7], 'subject_name': subject_name[0][0],
                                            'notes': l[8] if l[8] else '',
                                            'attachments': []}
                                    if l[0]:
                                        line['Saturday'] = l[9]
                                    else:
                                        line['Saturday'] = ''
                                    if l[1]:
                                        line['Sunday'] = l[10]
                                    else:
                                        line['Sunday'] = ''
                                    if l[2]:
                                        line['Monday'] = l[11]
                                    else:
                                        line['Monday'] = ''
                                    if l[3]:
                                        line['Tuesday'] = l[12]
                                    else:
                                        line['Tuesday'] = ''
                                    if l[4]:
                                        line['Wednesday'] = l[13]
                                    else:
                                        line['Wednesday'] = ''
                                    if l[5]:
                                        line['Thursday'] = l[14]
                                    else:
                                        line['Thursday'] = ''
                                    if l[6]:
                                        line['Friday'] = l[15]
                                    else:
                                        line['Friday'] = ''
                                    subject_lines.append(line)
                                    cursor.execute(
                                        "select id,name,url from ir_attachment where week_plan_line_id=%s",
                                        [l[16]])

                                    ir_attachment = cursor.fetchall()

                                    if ir_attachment:
                                        for att in ir_attachment:

                                            if att[2]:
                                                line['attachments'].append(
                                                    {'id': att[0], 'name': att[1], 'datas': att[2]})
                                data['lines'] = subject_lines
                                notes = ''
                                data['notes'] = notes

                        result = {'result': data}
                        # print(result)
                        return Response(result)


@api_view(['GET'])
def get_data_worksheets(request, student_id):
    if request.method == 'GET':
        if request.headers:
            if request.headers.get('Authorization'):
                if 'Bearer' in request.headers.get('Authorization'):
                    au = request.headers.get('Authorization').replace('Bearer', '').strip()
                    db_name = ManagerParent.objects.filter(token=au).values_list('db_name')

                    if db_name:
                        for e in db_name:
                            school_name = e[0]
                        with connections[school_name].cursor() as cursor:
                            data = []
                            cursor.execute(
                                "select user_id,year_id from student_student where id=%s",
                                [student_id])
                            user_id_q = cursor.fetchall()
                            if user_id_q:
                                cursor.execute(
                                    " select partner_id,branch_id from res_users where id=%s",
                                    [user_id_q[0][0]])
                                partner_id_q = cursor.fetchall()
                                cursor.execute(
                                    "select  worksheet_id  from student_details WHERE student_id = %s  ",
                                    [student_id])
                                class_worksheet_id = cursor.fetchall()
                                worksheet_id = []
                                for rec in class_worksheet_id:
                                    if rec[0]:
                                        worksheet_id.append(rec[0])
                                if worksheet_id:
                                    cursor.execute(
                                        " select id,name,priority,create_date,subject_id,deadline from class_worksheet where state='published' and year_id = %s and branch_id =%s and id in %s  ORDER BY create_date DESC",
                                        [user_id_q[0][1], partner_id_q[0][1], tuple(worksheet_id)])
                                    class_worksheet = cursor.fetchall()

                                    for w in class_worksheet:
                                        if w[4]:
                                            cursor.execute(
                                                "select  name  from school_subject WHERE id = %s ",
                                                [w[4]])
                                            subject_name = cursor.fetchall()
                                            deadline = None
                                            # cursor.execute(
                                            #     """select timezone from transport_setting ORDER BY ID DESC LIMIT 1""")
                                            # transport_setting = cursor.fetchall()
                                            # date_tz = transport_setting[0][0]
                                            date_tz = 'Asia/Kuwait'
                                            new_timezone = pytz.timezone(date_tz)

                                            date = w[3].astimezone(new_timezone)

                                            if w[5]:
                                                deadline = w[5].astimezone(new_timezone)

                                            data.append({'worksheet_id': w[0],
                                                         'name': w[1],
                                                         # str(p[2].strftime("%d %b %Y"))
                                                         'date': str(date.strftime("%d %b %Y")),
                                                         'priority': w[2],
                                                         'deadline': str(deadline.strftime("%d %b %Y") + ' ' + str(
                                                             deadline.hour) + ':' + str(deadline.minute) + ':' + str(
                                                             deadline.second)) if deadline else '',
                                                         'subject': subject_name[0][0],
                                                         'finish': str(deadline < datetime.datetime.now().astimezone(
                                                             new_timezone)) if deadline else ''
                                                         })
                                result = {'result': data}
                                # print(result)

                                return Response(result)
                            result = {'result': data}
                            return Response(result)


@api_view(['GET'])
def get_event_data(request, student_id):
    """
    Needed parameters student_id, current year_id for the student.
    Rerun list of dictionaries for student events data for portal event view.
    """
    if request.method == 'GET':
        if request.headers:
            if request.headers.get('Authorization'):
                if 'Bearer' in request.headers.get('Authorization'):
                    au = request.headers.get('Authorization').replace('Bearer', '').strip()
                    db_name = ManagerParent.objects.filter(token=au).values_list('db_name')

                    if db_name:
                        for e in db_name:
                            school_name = e[0]
                            with connections[school_name].cursor() as cursor:
                                data = []
                                cursor.execute(
                                    "select user_id,year_id from student_student where id=%s",
                                    [student_id])
                                user_id_q = cursor.fetchall()
                                if user_id_q:
                                    # cursor.execute(
                                    #     " select partner_id,branch_id from res_users where id=%s",
                                    #     [user_id_q[0][0]])
                                    # partner_id_q = cursor.fetchall()
                                    #     cursor.execute(
                                    #         "select  worksheet_id  from student_details WHERE student_id = %s  ",
                                    #         [student_id])
                                    #     class_worksheet_id = cursor.fetchall()
                                    #     worksheet_id = []
                                    #     for rec in class_worksheet_id:
                                    #         if rec[0]:
                                    #             worksheet_id.append(rec[0])
                                    #     if worksheet_id:
                                    cursor.execute(
                                        " select id,event_id,state,new_added from school_event_registration where  student_id =%s   ORDER BY create_date DESC",
                                        [student_id])
                                    events = cursor.fetchall()

                                    for ev in events:
                                        cursor.execute(
                                            " select name,state,start_date from school_event where id=%s and  year_id = %s",
                                            [ev[1], user_id_q[0][1]])
                                        school_event = cursor.fetchall()
                                        # school.event
                                        if school_event:
                                            data.append({'event_id': ev[0],
                                                         'name': school_event[0][0],
                                                         'start_date': school_event[0][2].strftime("%d %b %Y"),
                                                         'state': school_event[0][1],
                                                         'participant_state': ev[2],
                                                         'new_added': str(ev[3]) if ev[3] else ''
                                                         })
                                result = {'result': data}

                                return Response(result)
    result = {'result': ''}
    return Response(result)

    # search_filters = self.search(std_dom).portal_filterable_serchable()

    # return {'data': data, 'search_filters': search_filters}


@api_view(['GET'])
def get_worksheet_form_view_data(request, wsheet, std):
    """
    Needed parameters event_id.
    Rerun list of dictionaries for student events data for portal form view.
    """
    if request.method == 'GET':

        if request.headers:
            if request.headers.get('Authorization'):
                if 'Bearer' in request.headers.get('Authorization'):
                    au = request.headers.get('Authorization').replace('Bearer', '').strip()
                    db_name = ManagerParent.objects.filter(token=au).values_list('db_name')

                    if db_name:
                        for e in db_name:
                            school_name = e[0]
                    data = []
                    with connections[school_name].cursor() as cursor:

                        cursor.execute(
                            " select id,name,priority,create_date,subject_id,deadline,link,attached_homework,attach_files,description,teacher_id from class_worksheet where  id = %s  ORDER BY create_date DESC",
                            [wsheet])
                        worksheet = cursor.fetchall()
                        # cursor.execute(
                        #     """select timezone from transport_setting ORDER BY ID DESC LIMIT 1""")
                        # transport_setting = cursor.fetchall()
                        # date_tz = transport_setting[0][0]
                        date_tz = 'Asia/Kuwait'
                        new_timezone = pytz.timezone(date_tz)

                        # deadline= format_datetime(request.env, worksheet.deadline, tz=date_tz, dt_format=False)

                        import datetime

                        if worksheet:
                            if worksheet[0][5]:
                                deadline = worksheet[0][5]
                                date_time_str = deadline
                                date_time_obj = datetime.datetime.strptime(str(date_time_str),
                                                                           '%Y-%m-%d %H:%M:%S').astimezone(new_timezone)
                            cursor.execute(
                                "select  name  from school_subject WHERE id = %s ",
                                [worksheet[0][4]])
                            subject_name = cursor.fetchall()
                            cursor.execute(
                                "select  id,name,image_url,job_id  from hr_employee WHERE id = %s ",
                                [worksheet[0][10]])
                            hr_employee = cursor.fetchall()
                            cursor.execute(
                                "select  name from hr_job WHERE id = %s ",
                                [hr_employee[0][3]])
                            job_name = cursor.fetchall()
                            # hr.job
                            if worksheet[0][6]:

                                # importing the module
                                file = urllib.request.urlopen(worksheet[0][6])
                                size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")

                                i = 0
                                s = 0
                                if file.length:
                                    i = int(math.floor(math.log(file.length, 1024)))
                                    p = math.pow(1024, i)
                                    s = round(file.length / p, 2)
                            cursor.execute(
                                "select id from student_student where id=%s",
                                [std])
                            user_id_q = cursor.fetchall()
                            student_solution = []
                            if user_id_q:
                                cursor.execute(
                                    "select id from student_details where worksheet_id=%s and student_id=%s",
                                    [worksheet[0][0], std])
                                detail = cursor.fetchall()

                                cursor.execute(
                                    "SELECT * FROM public.ir_attachment_student_details_rel where student_details_id=%s ",
                                    [detail[0][0]])
                                ir_attachment_student_details_rel = cursor.fetchall()
                                if ir_attachment_student_details_rel:
                                    for rec in ir_attachment_student_details_rel:
                                        cursor.execute(
                                            "SELECT name,file_size  FROM public.ir_attachment where id=%s ",
                                            [rec[1]])
                                        ir_attachment = cursor.fetchall()
                                        for res in ir_attachment:
                                            student_solution.append({
                                                'name': str(res[0]),
                                                'file_size': str(res[1])
                                            })

                            data.append({'worksheet_id': worksheet[0][0],
                                         'name': worksheet[0][1],
                                         'date': str(worksheet[0][3].strftime("%d %b %Y")) if worksheet[0][3] else '',
                                         'teacher_name': hr_employee[0][1],
                                         'link': worksheet[0][6] if worksheet[0][6] else '',
                                         'teacher_id': hr_employee[0][0],
                                         'teacher_image': 'https://trackware-schools.s3.eu-central-1.amazonaws.com/' + str(
                                             hr_employee[0][2]) if hr_employee[0][
                                             2] else "https://s3.eu-central-1.amazonaws.com/trackware.schools/public_images/default_student.png",
                                         'teacher_position': job_name[0][0] if job_name else 'Teacher',
                                         'subject': subject_name[0][0],
                                         'homework': "%s %s" % (s, size_name[i]) if worksheet[0][7] else '',
                                         'homework_name': worksheet[0][8],
                                         'description': worksheet[0][9],
                                         'deadline': str(date_time_obj.strftime("%d %b %Y")) if worksheet[0][5] else "",
                                         'end': str(datetime.datetime.now() >= worksheet[0][5]) if worksheet[0][
                                             5] else "",
                                         'student_solution': student_solution
                                         })
                        result = {'result': data}
                        # print(result)
                        return Response(result)
                    result = {'result': data}
                    return Response(result)


def remove_html(string):
    import re
    regex = re.compile(r'<[^>]+>')
    return regex.sub('', string)


@api_view(['GET'])
def get_event_form_view_data(request, event, std):
    """
    Needed parameters event_id.
    Rerun list of dictionaries for student events data for portal form view.
    """
    if request.method == 'GET':
        if request.headers:
            if request.headers.get('Authorization'):
                if 'Bearer' in request.headers.get('Authorization'):
                    au = request.headers.get('Authorization').replace('Bearer', '').strip()
                    db_name = ManagerParent.objects.filter(token=au).values_list('db_name')

                    if db_name:
                        for e in db_name:
                            school_name = e[0]
                            with connections[school_name].cursor() as cursor:

                                cursor.execute(
                                    " select id,event_id,state,new_added from school_event_registration where  id =%s   ORDER BY create_date DESC",
                                    [event])
                                events = cursor.fetchall()
                                cursor.execute(
                                    "Update school_event_registration SET new_added = False  WHERE id=%s",
                                    [event])

                                data = []

                                cursor.execute(
                                    " select name,state,start_date,maximum_participants,maximum_participants,cost,attached_event,attach_files_event,link,contact_id,supervisor_id,start_date,end_date,start_reg_date,last_reg_date,company_id from school_event where id=%s",
                                    [events[0][1]])
                                school_event = cursor.fetchall()

                                cursor.execute(
                                    " select currency_id from res_company where id=%s",
                                    [school_event[0][15]])
                                res_company = cursor.fetchall()
                                cursor.execute(
                                    " select name from res_currency where id=%s",
                                    [res_company[0][0]])
                                res_currency = cursor.fetchall()
                                contact_id = ''

                                if school_event[0][9]:
                                    cursor.execute(
                                        "select  id,name,image_url  from hr_employee WHERE id = %s ",
                                        [school_event[0][9]])
                                    contact_id = cursor.fetchall()
                                cursor.execute(
                                    "select  id,name,image_url  from hr_employee WHERE id = %s ",
                                    [school_event[0][10]])
                                supervisor_id = cursor.fetchall()
                                cursor.execute(
                                    " select id from school_event_registration where  event_id =%s and  state='confirm'  ORDER BY create_date DESC",
                                    [event])
                                participants = cursor.fetchall()
                                available_seats = school_event[0][3] - len(participants)
                                cursor.execute(
                                    "select user_id from student_student where id=%s",
                                    [std])
                                user_id_q = cursor.fetchall()
                                student_solution = []
                                if user_id_q:
                                    import math
                                    cursor.execute(
                                        "SELECT name,file_size  FROM public.ir_attachment where res_model='school.event' and res_id =%s and student_idq =%s",
                                        [events[0][1], std])
                                    ir_attachment = cursor.fetchall()
                                    for res in ir_attachment:
                                        size_name = (
                                            "B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
                                        i1 = int(math.floor(math.log(res[1], 1024)))
                                        p1 = math.pow(1024, i1)
                                        s1 = round(res[1] / p1, 2)
                                        student_solution.append({
                                            'name': str(res[0]),
                                            'file_size': str(s1)
                                        })
                                contact_name = ''
                                supervisor_name = ''
                                supervisor_image = 'https://s3.eu-central-1.amazonaws.com/trackware.schools/public_images/default_student.png'
                                contact_image = 'https://s3.eu-central-1.amazonaws.com/trackware.schools/public_images/default_student.png'
                                contact_id_id = 0
                                supervisor_id_id = 0

                                if contact_id:
                                    contact_name = contact_id[0][1] if contact_id[0][1] else ""
                                    contact_image = contact_id[0][2] if contact_id[0][
                                        2] else "https://s3.eu-central-1.amazonaws.com/trackware.schools/public_images/default_student.png"
                                    contact_id_id = contact_id[0][0] if contact_id[0][0] else 0

                                if supervisor_id:
                                    supervisor_name = supervisor_id[0][1] if supervisor_id[0][1] else ""
                                    supervisor_image = supervisor_id[0][2] if supervisor_id[0][
                                        2] else "https://s3.eu-central-1.amazonaws.com/trackware.schools/public_images/default_student.png"
                                    supervisor_id_id = supervisor_id[0][0] if supervisor_id[0][0] else 0

                                data.append({'event_id': events[0][0],
                                             'name': school_event[0][0],
                                             'start_date': str(school_event[0][11].strftime("%d %b %Y")),
                                             'end_date': str(school_event[0][12].strftime("%d %b %Y")),
                                             'registration_start_date': str(school_event[0][13].strftime("%d %b %Y")) if
                                             school_event[0][
                                                 13] else '',
                                             'registration_last_date': str(school_event[0][14].strftime("%d %b %Y")) if
                                             school_event[0][
                                                 14] else '',
                                             'maximum_participants': school_event[0][3],
                                             'available_seats': available_seats,
                                             'cost': str(school_event[0][5]) + ' ' + str(res_currency[0][0]),
                                             'contact_name': contact_name,
                                             'contact_id': contact_id_id,
                                             'contact_image': contact_image,
                                             'supervisor_name': supervisor_name,
                                             'event': str(school_event[0][6]) if school_event[0][6] else '',
                                             'event_name': str(school_event[0][7]) if school_event[0][7] else '',
                                             'link': str(school_event[0][8]) if school_event[0][8] else '',
                                             'supervisor_id': supervisor_id_id,
                                             'supervisor_image': supervisor_image,
                                             'state': events[0][2],
                                             'flag': str(True) if events[0][2] == 'draft' else str(False),
                                             'period': str(school_event[0][12] - school_event[0][11]),
                                             'student_solution': student_solution,

                                             'new_added': str(events[0][3]) if events[0][3] else ''})

                                result = {'result': data}

                                return Response(result)


@api_view(['GET'])
def get_library(request, student_id):
    if request.method == 'GET':
        if request.headers:
            if request.headers.get('Authorization'):
                if 'Bearer' in request.headers.get('Authorization'):
                    au = request.headers.get('Authorization').replace('Bearer', '').strip()
                    db_name = ManagerParent.objects.filter(token=au).values_list('db_name')

                    if db_name:
                        for e in db_name:
                            school_name = e[0]
                    with connections[school_name].cursor() as cursor:
                        book_borrowed = []
                        book_all_r = []
                        book_req = []
                        cursor.execute(
                            " SELECT ID,NAME,borrow_period_days FROM product_template WHERE is_library_book=TRUE",
                            [])
                        all_book = cursor.fetchall()

                        for book1 in all_book:
                            # cursor.execute(
                            #     "SELECT  product_qty  from  report_stock_quantity WHERE product_id=%s  ORDER BY DATE DESC LIMIT 1",
                            #     [book1[0]])
                            # report_stock_quantity = cursor.fetchall()
                            # if report_stock_quantity:
                            # if report_stock_quantity[0][0]>0:

                            book_all_r.append({'id': book1[0],
                                               'name': book1[1],
                                               'borrow_period_days': str(book1[2])

                                               })
                        cursor.execute(
                            "select display_name_search,year_id,user_id from student_student where id=%s",
                            [student_id])
                        user_id_q = cursor.fetchall()
                        cursor.execute(
                            " select branch_id from res_users where id=%s",
                            [user_id_q[0][2]])
                        branch_id = cursor.fetchall()
                        if user_id_q:
                            cursor.execute(
                                "SELECT  id,book_id,state,create_date,date_delivered,date_returned,expected_return_date from book_request  where student_id=%s and branch_id=%s ORDER BY id DESC",
                                [student_id, branch_id[0][0]])
                            book_request = cursor.fetchall()
                            for book in book_request:
                                book_author = ''
                                cursor.execute(
                                    "SELECT name,id FROM product_template WHERE id = %s",
                                    [book[1]])
                                book_name = cursor.fetchall()

                                cursor.execute(
                                    "SELECT book_author_id FROM book_author_prodtempl_rel WHERE product_template_id=%s",
                                    [book_name[0][1]])
                                book_author_prodtempl_rel = cursor.fetchall()
                                for author in book_author_prodtempl_rel:
                                    cursor.execute(
                                        "SELECT name FROM product_author WHERE id=%s",
                                        [author[0]])
                                    product_author = cursor.fetchall()
                                    book_author += product_author[0][0] + ' & '
                                if book_author:
                                    book_author = book_author[:len(book_author) - 2] + book_author[len(book_author):]
                                if book[2] == 'delivered' or book[2] == 'done':

                                    book_borrowed.append({'id': book[1],
                                                          'name': book_name[0][0],
                                                          'date_delivered': book[4].strftime("%d %b %Y"),
                                                          'date_returned': book[6].strftime("%d %b %Y"),
                                                          'date_returned_on': book[5].strftime("%d %b %Y") if book[
                                                              5] else '',
                                                          'status': book[2],
                                                          'book_author': book_author
                                                          })

                                else:
                                    book_req.append({'id': book[1],
                                                     'name': book_name[0][0],
                                                     'requested_date': book[3].strftime("%d %b %Y"),
                                                     'status': book[2]
                                                     })

                    result = {'book_request': book_req,
                              'book_borrowed': book_borrowed,
                              'book': book_all_r}

                    return Response(result)


@api_view(['POST'])
def post_library(request):
    if request.method == 'POST':
        if request.headers:
            if request.headers.get('Authorization'):
                if 'Bearer' in request.headers.get('Authorization'):
                    au = request.headers.get('Authorization').replace('Bearer', '').strip()
                    db_name = ManagerParent.objects.filter(token=au).values_list('db_name')
                    if db_name:
                        for e in db_name:
                            school_name = e[0]
                        school_name = ManagerParent.pincode(school_name)
                        student_id = request.data.get('student_id')
                        book_id = request.data.get('book_id')
                        countDay = request.data.get('countDay')
                        request_soft_copy = request.data.get('copy')
                        with connections[school_name].cursor() as cursor:

                            cursor.execute(
                                "select id from stock_warehouse WHERE is_library =true ORDER BY ID DESC LIMIT 1",
                                [])
                            stock_warehouse = cursor.fetchall()
                            cursor.execute(
                                "select id from book_request  ORDER BY ID DESC LIMIT 1",
                                [])
                            book_request = cursor.fetchall()
                            cursor.execute(
                                "select id from res_partner  WHERE student_id =%s",
                                [student_id])
                            borrower_id = cursor.fetchall()
                            cursor.execute(
                                "select year_id,user_id from student_student where id=%s",
                                [student_id])
                            user_id_q = cursor.fetchall()
                            cursor.execute(
                                " select branch_id from res_users where id=%s",
                                [user_id_q[0][1]])
                            branch_id = cursor.fetchall()
                            # cursor.execute(
                            #     "select year_id,branch_id from student_student  WHERE id =%s",
                            #     [student_id])
                            # branch_id = cursor.fetchall()
                            # res.partner expected_return_date
                            # print(book_request)
                            if book_request:
                                name = 'R00' + str(book_request[0][0] + 1)
                            else:
                                name = 'R00' + str(1)
                            # select id from stock_warehouse WHERE is_library =true ORDER BY ID DESC LIMIT 1
                            cursor.execute(
                                "INSERT INTO book_request(borrower_id,book_id,name,request_soft_copy,library_id,state,create_date,student_id,branch_id,academic_year,requested_borrow_days)VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                                [borrower_id[0][0], book_id, name, request_soft_copy,
                                 stock_warehouse[0][0] if stock_warehouse else 1, 'under_approval',
                                 datetime.datetime.now(), student_id, branch_id[0][0], user_id_q[0][0], countDay])
                            result = {'result': 'ok'}
                            return Response(result)
                result = {'result': 'Error Authorization'}
                return Response(result)
            result = {'result': 'Not Authorization'}
            return Response(result)
        # Marks


@api_view(['GET'])
def get_marks(request, student_id):
    if request.method == 'GET':
        # if request.headers:
        #     if request.headers.get('Authorization'):
        #         if 'Bearer' in request.headers.get('Authorization'):
        #             au = request.headers.get('Authorization').replace('Bearer', '').strip()
        #             db_name = ManagerParent.objects.filter(token=au).values_list('db_name')
        #
        #             if db_name:
        #                 for e in db_name:
        #                     school_name = e[0]
        with connections['tst'].cursor() as cursor:
            book_borrowed = []
            book_all_r = []
            book_req = []
            cursor.execute(
                "SELECT id,name FROM academic_semester WHERE year_id=(SELECT year_id FROM student_student WHERE id=%s)",
                [student_id])
            academic_semester = cursor.fetchall()

            class_id = None
            # ----------------------
            cursor.execute(
                "SELECT academic_grade_id FROM public.student_distribution_line WHERE id = (SELECT student_distribution_line_id FROM student_distribution_line_student_student_rel WHERE student_student_id=%s ORDER BY student_distribution_line_id DESC LIMIT 1)",
                [student_id])
            student_distribution_line = cursor.fetchall()
            if student_distribution_line:
                cursor.execute(
                    "SELECT id FROM public.academic_grade WHERE id = %s",
                    [student_distribution_line[0][0]])
                academic_grade = cursor.fetchall()
                cursor.execute(
                    "select id from school_class WHERE academic_grade_id = %s",
                    [academic_grade[0][0]])
                cl = cursor.fetchall()
                class_id = cl[0][0] if cl else ''
            if class_id == None:
                cursor.execute(
                    "select class_id from res_partner where id=(select partner_id from res_users where id=(select user_id from student_student where id=%s))",
                    [student_id])
                academic_grade_q = cursor.fetchall()
                class_id = academic_grade_q[0][0] if academic_grade_q else ''
            cursor.execute(
                " SELECT name,subject_id FROM mark_mark WHERE state='approved' and  class_id=%s",
                [class_id])
            mark = cursor.fetchall()

        result = {'book_request': book_req,
                  'book_borrowed': book_borrowed,
                  'book': book_all_r}

        return Response(result)


@api_view(['POST'])
def logout(request):
    if request.method == 'POST':
        # print("sdasadsafffyyyyyyy" )
        if request.headers:
            # print("sdasadsafffyyyyyyyaa")
            if request.headers.get('Authorization'):
                # print("sdasadsafffyyyyyyssy",request.headers.get('Authorization'))
                # parent_id
                au = request.headers.get('Authorization').replace('Bearer', '').strip()
                db_name = ManagerParent.objects.filter(token=au).values_list('db_name')

                if db_name:
                    for e in db_name:
                        school_name = e[0]
                parent_id = ManagerParent.objects.filter(token=au).values_list('parent_id')
                # parent_id1 = ManagerParent.objects.filter(token=au).values_list('mobile_token')
                if parent_id:
                    for e in parent_id:
                        parent_id = e[0]

                ManagerParent.objects.filter(parent_id=parent_id[0][0], db_name=school_name,is_active=True).order_by('-pk').update(mobile_token='')
                # ManagerParent.objects.filter(parent_id=parent_id[0][0], db_name=school_name, is_active=True).delete()
                mobile_toke121n = ManagerParent.objects.filter(parent_id=parent_id[0][0], db_name=school_name,is_active=True).values_list('mobile_token')
                print("ssssssssssssss",mobile_toke121n,parent_id[0][0],school_name)
                with connections[school_name].cursor() as cursor:
                    cursor.execute(
                        "UPDATE public.school_parent SET mobile_token=%s WHERE id=%s;",
                        ['', parent_id[0][0]])
                result = {'result': 'ok'}
                return Response(result)
            result = {'result': 'Not Authorization'}
            return Response(result)
        result = {'result': 'Not headers'}
        return Response(result)


@api_view(['GET'])
def get_time_table(request, student_id):
    if request.method == 'GET':
        if request.headers:
            if request.headers.get('Authorization'):
                if 'Bearer' in request.headers.get('Authorization'):
                    au = request.headers.get('Authorization').replace('Bearer', '').strip()
                    db_name = ManagerParent.objects.filter(token=au).values_list('db_name')

                    if db_name:
                        for e in db_name:
                            school_name = e[0]

                    with connections[school_name].cursor() as cursor:

                        data = {}
                        days = []
                        cursor.execute(
                            "select user_id,year_id from student_student where id=%s",
                            [student_id])
                        student = cursor.fetchall()
                        if student:

                            cursor.execute(
                                " select partner_id from res_users where id=%s",
                                [student[0][0]])
                            partner_id = cursor.fetchall()
                            if partner_id:

                                cursor.execute(
                                    "select class_id from res_partner where id=%s",
                                    [partner_id[0][0]])
                                class_id = cursor.fetchall()

                                cursor.execute(
                                    "SELECT id, name FROM school_day WHERE checkbox_day=true;",
                                    [])
                                school_day = cursor.fetchall()
                                subject_lines = []
                                for line in school_day:
                                    day_id = 0
                                    if 'Saturday' in line and 'Saturday' not in days:
                                        days.append('Saturday')
                                        day_id = 5
                                    elif 'Sunday' in line and 'Sunday' not in days:
                                        days.append('Sunday')
                                        day_id = 6
                                    elif 'Monday' in line and 'Monday' not in days:
                                        days.append('Monday')
                                        day_id = 0
                                    elif 'Tuesday' in line and 'Tuesday' not in days:
                                        days.append('Tuesday')
                                        day_id = 1
                                    elif 'Wednesday' in line and 'Wednesday' not in days:
                                        days.append('Wednesday')
                                        day_id = 2
                                    elif 'Thursday' in line and 'Thursday' not in days:
                                        days.append('Thursday')
                                        day_id = 3
                                    elif 'Friday' in line and 'Friday' not in days:
                                        days.append('Friday')
                                        day_id = 4
                                    cursor.execute(
                                        "SELECT lecture_id,subject_id,  from_time, to_time ,sequence FROM public.add_day_subject WHERE class_id=%s and week_day=%s ORDER by sequence ASC; ",
                                        [class_id[0][0], str(day_id)])
                                    add_day_subject = cursor.fetchall()

                                    for subject in add_day_subject:

                                        subject_name = 'break'
                                        if subject[1]:
                                            cursor.execute(
                                                "select  name  from school_subject WHERE id = %s ",
                                                [subject[1]])
                                            s_name = cursor.fetchall()
                                            subject_name = s_name[0][0]

                                        line = {'subject_id': subject[1], 'subject_name': subject_name,
                                                }

                                        from_time = '{0:02.0f}:{1:02.0f}'.format(*divmod(float(subject[2]) * 60, 60))
                                        to_time = '{0:02.0f}:{1:02.0f}'.format(*divmod(float(subject[3]) * 60, 60))

                                        if day_id == 5:
                                            line['Saturday'] = str(from_time) + " - " + str(to_time)
                                        else:
                                            line['Saturday'] = ''
                                        if day_id == 6:
                                            line['Sunday'] = str(from_time) + " - " + str(to_time)
                                        else:
                                            line['Sunday'] = ''
                                        if day_id == 0:
                                            line['Monday'] = str(from_time) + " - " + str(to_time)
                                        else:
                                            line['Monday'] = ''
                                        if day_id == 1:
                                            line['Tuesday'] = str(from_time) + " - " + str(to_time)
                                        else:
                                            line['Tuesday'] = ''
                                        if day_id == 2:
                                            line['Wednesday'] = str(from_time) + " - " + str(to_time)
                                        else:
                                            line['Wednesday'] = ''
                                        if day_id == 3:
                                            line['Thursday'] = str(from_time) + " - " + str(to_time)
                                        else:
                                            line['Thursday'] = ''
                                        if day_id == 4:
                                            line['Friday'] = str(from_time) + " - " + str(to_time)
                                        else:
                                            line['Friday'] = ''

                                        subject_lines.append(line)
                                    # print("-----------------")
                                days = list(set(days))

                                columns = {'days': {}}

                                for day in days:
                                    if day == 'Saturday':
                                        columns['days'][0] = 'Saturday'
                                    if day == 'Sunday':
                                        columns['days'][1] = 'Sunday'
                                    if day == 'Monday':
                                        columns['days'][2] = 'Monday'
                                    if day == 'Tuesday':
                                        columns['days'][3] = 'Tuesday'
                                    if day == 'Wednesday':
                                        columns['days'][4] = 'Wednesday'
                                    if day == 'Thursday':
                                        columns['days'][5] = 'Thursday'
                                    if day == 'Friday':
                                        columns['days'][6] = 'Friday'
                                columns = sorted(columns['days'].items())
                                dayss = []

                                for col in columns:
                                    dayss.append({
                                        "id": col[0],
                                        "day": col[1]
                                    })
                                data['columns'] = dayss

                                data['lines'] = subject_lines
                                # notes = ''
                                # data['notes'] = notes

                        result = {'result': data}
                        # print(result)
                        return Response(result)


@api_view(['GET', 'POST'])
def get_Allergies(request):
    if request.method == 'GET':
        if request.headers:
            if request.headers.get('Authorization'):
                au = request.headers.get('Authorization').replace('Bearer', '').strip()
                db_name = ManagerParent.objects.filter(token=au).values_list('db_name')

                if db_name:
                    for e in db_name:
                        school_name = e[0]
                parent_id = ManagerParent.objects.filter(token=au).values_list('parent_id')

                if parent_id:
                    for e in parent_id:
                        parent_id = e[0]
                ManagerParent.objects.filter(parent_id=parent_id[0][0], db_name=school_name).update(
                    mobile_token='')
                date = []
                with connections[school_name].cursor() as cursor:

                    cursor.execute(
                        "select id,name from product_attribute_value WHERE attribute_id = (select id from product_attribute WHERE name = 'allergies' or name = 'Allergies')",
                        [])
                    product_attribute_value = cursor.fetchall()

                    for allergies in product_attribute_value:
                        if allergies[1]:
                            date.append({"id": allergies[0],
                                         "name": allergies[1],
                                         "icon": "https://trackware-schools.s3.eu-central-1.amazonaws.com/allergic.svg",
                                         "des": ""

                                         })

                result = {'result': date}
                return Response(result)
            result = {'result': 'Not Authorization'}
            return Response(result)
        result = {'result': 'Not headers'}
        return Response(result)
    if request.method == 'POST':
        if request.headers:
            if request.headers.get('Authorization'):
                au = request.headers.get('Authorization').replace('Bearer', '').strip()
                db_name = ManagerParent.objects.filter(token=au).values_list('db_name')

                if db_name:
                    for e in db_name:
                        school_name = e[0]
                parent_id = ManagerParent.objects.filter(token=au).values_list('parent_id')

                if parent_id:
                    for e in parent_id:
                        parent_id = e[0]
                ManagerParent.objects.filter(parent_id=parent_id[0][0], db_name=school_name).update(
                    mobile_token='')

                with connections[school_name].cursor() as cursor:
                    student_id = request.data.get('student_id')
                    list_al = request.data.get('list_al')
                    # allergies.food
                    cursor.execute(
                        "select year_id, user_id,canteen_spending from student_student WHERE id=%s",
                        [student_id])
                    student_info = cursor.fetchall()

                    cursor.execute(
                        "select branch_id,company_id from res_users WHERE id=%s",
                        [student_info[0][1]])
                    student_info_users = cursor.fetchall()

                    cursor.execute(
                        "select attribute_value_id from allergies_food WHERE student_id = %s and year_id=%s and branch_id=%s and company_id=%s",
                        [student_id, student_info[0][0], student_info_users[0][0], student_info_users[0][0]])
                    allergies_food = cursor.fetchall()

                    allergies_food = list(set(allergies_food))
                    cursor.execute(
                        "delete from allergies_food where student_id=%s",
                        [student_id])

                    # for allergies in allergies_food:
                    #
                    #     if allergies not  in list_al:
                    #         cursor.execute(
                    #             "INSERT INTO allergies_food(year_id, student_id, branch_id,company_id,attribute_value_id)VALUES (%s,%s,%s,%s,%s);",
                    #             [student_info[0][0], student_id, student_info_users[0][0], student_info_users[0][0],
                    #              allergies])
                    for allergies in list_al:
                        cursor.execute(
                            "INSERT INTO allergies_food(year_id, student_id, branch_id,company_id,attribute_value_id)VALUES (%s,%s,%s,%s,%s);",
                            [student_info[0][0], student_id, student_info_users[0][0], student_info_users[0][0],
                             allergies])

                result = {'result': 'ok'}
                return Response(result)
            result = {'result': 'Not Authorization'}
            return Response(result)
        result = {'result': 'Not headers'}
        return Response(result)


@api_view(['GET', 'POST'])
def get_Allergies_student(request, student_id):
    if request.method == 'GET':
        if request.headers:
            if request.headers.get('Authorization'):
                au = request.headers.get('Authorization').replace('Bearer', '').strip()
                db_name = ManagerParent.objects.filter(token=au).values_list('db_name')

                if db_name:
                    for e in db_name:
                        school_name = e[0]
                parent_id = ManagerParent.objects.filter(token=au).values_list('parent_id')

                if parent_id:
                    for e in parent_id:
                        parent_id = e[0]
                ManagerParent.objects.filter(parent_id=parent_id[0][0], db_name=school_name).update(
                    mobile_token='')
                date = []
                with connections[school_name].cursor() as cursor:

                    cursor.execute(
                        "select id,name from product_attribute_value WHERE attribute_id = (select id from product_attribute WHERE name = 'allergies' or name = 'Allergies')",
                        [])
                    product_attribute_value = cursor.fetchall()

                    for allergies in product_attribute_value:
                        if allergies[1]:
                            date.append({"id": allergies[0],
                                         "name": allergies[1],
                                         "icon": "https://trackware-schools.s3.eu-central-1.amazonaws.com/allergic.svg",
                                         "des": ""

                                         })

                result = {'result': date}
                return Response(result)
            result = {'result': 'Not Authorization'}
            return Response(result)
        result = {'result': 'Not headers'}
        return Response(result)
    if request.method == 'POST':
        if request.headers:
            if request.headers.get('Authorization'):
                au = request.headers.get('Authorization').replace('Bearer', '').strip()
                db_name = ManagerParent.objects.filter(token=au).values_list('db_name')

                if db_name:
                    for e in db_name:
                        school_name = e[0]
                parent_id = ManagerParent.objects.filter(token=au).values_list('parent_id')

                if parent_id:
                    for e in parent_id:
                        parent_id = e[0]
                ManagerParent.objects.filter(parent_id=parent_id[0][0], db_name=school_name).update(
                    mobile_token='')

                with connections[school_name].cursor() as cursor:
                    student_id = request.data.get('student_id')
                    list_al = request.data.get('list_al')
                    # allergies.food
                    cursor.execute(
                        "select year_id, user_id,canteen_spending from student_student WHERE id=%s",
                        [student_id])
                    student_info = cursor.fetchall()

                    cursor.execute(
                        "select branch_id,company_id from res_users WHERE id=%s",
                        [student_info[0][1]])
                    student_info_users = cursor.fetchall()

                    # cursor.execute(
                    #     "select attribute_value_id from allergies_food WHERE student_id = %s and year_id=%s and branch_id=%s and company_id=%s",
                    #     [student_id, student_info[0][0], student_info_users[0][0], student_info_users[0][0]])
                    # allergies_food = cursor.fetchall()
                    #
                    # allergies_food = list(set(allergies_food))
                    cursor.execute(
                        "delete from allergies_food where student_id=%s",
                        [student_id])

                    # for allergies in allergies_food:
                    #
                    #     if allergies not  in list_al:
                    #         cursor.execute(
                    #             "INSERT INTO allergies_food(year_id, student_id, branch_id,company_id,attribute_value_id)VALUES (%s,%s,%s,%s,%s);",
                    #             [student_info[0][0], student_id, student_info_users[0][0], student_info_users[0][0],
                    #              allergies])
                    for allergies in list_al:
                        cursor.execute(
                            "INSERT INTO allergies_food(year_id, student_id, branch_id,company_id,attribute_value_id)VALUES (%s,%s,%s,%s,%s);",
                            [student_info[0][0], student_id, student_info_users[0][0], student_info_users[0][0],
                             allergies])

                result = {'result': 'ok'}
                return Response(result)
            result = {'result': 'Not Authorization'}
            return Response(result)
        result = {'result': 'Not headers'}
        return Response(result)


@api_view(['POST'])
def post_spending(request):
    if request.method == 'POST':
        if request.headers:
            if request.headers.get('Authorization'):
                au = request.headers.get('Authorization').replace('Bearer', '').strip()
                db_name = ManagerParent.objects.filter(token=au).values_list('db_name')

                if db_name:
                    for e in db_name:
                        school_name = e[0]
                parent_id = ManagerParent.objects.filter(token=au).values_list('parent_id')

                if parent_id:
                    for e in parent_id:
                        parent_id = e[0]
                ManagerParent.objects.filter(parent_id=parent_id[0][0], db_name=school_name).update(
                    mobile_token='')
                student_id = request.data.get('student_id')
                canteen_spending = request.data.get('canteen_spending')
                result = {'result': 'erorr'}
                with connections[school_name].cursor() as cursor:
                    try:
                        cursor.execute(
                            "UPDATE public.student_student SET canteen_spending=%s WHERE id=%s;",
                            [canteen_spending, student_id])
                        # print(student_id)
                        result = {'result': 'ok'}
                    except:
                        result = {'result': ' does not exist canteen_spending'}

                print(result)

                return Response(result)
            result = {'result': 'Not Authorization'}
            return Response(result)
        result = {'result': 'Not headers'}
        return Response(result)


@api_view(['POST'])
def get_info_canteen_student(request):
    if request.method == 'POST':
        if request.headers:
            if request.headers.get('Authorization'):
                au = request.headers.get('Authorization').replace('Bearer', '').strip()
                db_name = ManagerParent.objects.filter(token=au).values_list('db_name')

                if db_name:
                    for e in db_name:
                        school_name = e[0]
                parent_id = ManagerParent.objects.filter(token=au).values_list('parent_id')

                if parent_id:
                    for e in parent_id:
                        parent_id = e[0]
                ManagerParent.objects.filter(parent_id=parent_id[0][0], db_name=school_name).update(
                    mobile_token='')
                date_allergies = []
                date_schdule = []
                date_spending = []
                with connections[school_name].cursor() as cursor:
                    student_id = request.data.get('student_id')

                    cursor.execute(
                        "select year_id, user_id,canteen_spending from student_student WHERE id=%s",
                        [student_id])
                    student_info = cursor.fetchall()

                    cursor.execute(
                        "select branch_id,company_id from res_users WHERE id=%s",
                        [student_info[0][1]])
                    student_info_users = cursor.fetchall()

                    cursor.execute(
                        "select attribute_value_id from allergies_food WHERE student_id = %s and year_id=%s and branch_id=%s and company_id=%s",
                        [student_id, student_info[0][0], student_info_users[0][0], student_info_users[0][0]])
                    allergies_food = cursor.fetchall()

                    allergies_food = list(set(allergies_food))

                    cursor.execute(
                        "select id from banned_food WHERE student_id = %s and year_id=%s and branch_id=%s and company_id=%s",
                        [student_id, student_info[0][0], student_info_users[0][0], student_info_users[0][0]])
                    banned_food = cursor.fetchall()
                    cursor.execute(
                        "SELECT id, name FROM school_day WHERE id in (SELECT school_day_id FROM public.res_company_school_day_rel where res_company_id=%s)",
                        [student_info_users[0][0]])
                    school_day = cursor.fetchall()
                    student_spending = 1
                    date_spending.append({
                        "canteen_spending": str(student_info[0][2]) if student_info[0][2] else "0",
                        "student_spending": str(student_spending),
                        "per_spending": float(student_spending / student_info[0][2]) if student_info[0][2] and
                                                                                        student_info[0][
                                                                                            2] != 0 else 0.0,
                    })
                    for day in school_day:
                        cursor.execute(
                            "SELECT id  FROM allergies_food_day WHERE student_id = %s and year_id=%s and branch_id=%s and company_id=%s and day_id=%s",
                            [student_id, student_info[0][0], student_info_users[0][0], student_info_users[0][0],
                             day[0]])
                        student_food_day = cursor.fetchall()
                        date_schdule.append({'name': day[1], "len_item": str(len(student_food_day)), "day_id": day[0]})
                    # allergies.food.day
                    for allergies in allergies_food:
                        cursor.execute(
                            "select name from product_attribute_value WHERE id = %s ",
                            [allergies[0]])
                        allergies_food1 = cursor.fetchall()
                        date_allergies.append({"name": allergies_food1[0][0],
                                               })

                result = {'food_allegies': date_allergies, "banned_food": str(len(banned_food)),
                          "schdule_meals": date_schdule, "spending": date_spending}

                return Response(result)
            result = {'result': 'Not Authorization'}
            return Response(result)
        result = {'result': 'Not headers'}
        return Response(result)


@api_view(['GET'])
def get_category(request):
    if request.method == 'GET':
        if request.headers:
            if request.headers.get('Authorization'):
                au = request.headers.get('Authorization').replace('Bearer', '').strip()
                db_name = ManagerParent.objects.filter(token=au).values_list('db_name')

                if db_name:
                    for e in db_name:
                        school_name = e[0]
                parent_id = ManagerParent.objects.filter(token=au).values_list('parent_id')

                if parent_id:
                    for e in parent_id:
                        parent_id = e[0]
                ManagerParent.objects.filter(parent_id=parent_id[0][0], db_name=school_name).update(
                    mobile_token='')
                date = []
                with connections[school_name].cursor() as cursor:
                    # canteen_spending
                    # student_id = request.data.get('student_id')
                    # cursor.execute(
                    #     "select year_id, user_id,canteen_spending from student_student WHERE id=%s",
                    #     [student_id])
                    # student_info = cursor.fetchall()
                    #
                    # cursor.execute(
                    #     "select branch_id,company_id from res_users WHERE id=%s",
                    #     [student_info[0][1]])
                    # student_info_users = cursor.fetchall()

                    cursor.execute("select id,name,parent_id from pos_category",
                                   [])
                    pos_category = cursor.fetchall()

                    for category in pos_category:
                        cursor.execute("select id,name from pos_category WHERE parent_id=%s",
                                       [category[0]])
                        pos_category_sub = cursor.fetchall()
                        subMenu = []
                        for category_sub in pos_category_sub:
                            subMenu.append({"name": category_sub[1],
                                            "icon": "https://trackware-schools.s3.eu-central-1.amazonaws.com/flutter_app/Exams.svg",
                                            "id": category_sub[0], "stutes": False, "sub": True

                                            })
                        if not category[2]:
                            date.append({"name": category[1], "id": category[0], "stutes": False,
                                         "icon": "https://trackware-schools.s3.eu-central-1.amazonaws.com/flutter_app/Exams.svg",
                                         "subMenu": subMenu, "sub": False
                                         })

                result = {'result': date}
                return Response(result)
            result = {'result': 'Not Authorization'}
            return Response(result)
        result = {'result': 'Not headers'}
        return Response(result)


@api_view(['POST'])
def post_banned(request):
    if request.method == 'POST':
        if request.headers:
            if request.headers.get('Authorization'):
                au = request.headers.get('Authorization').replace('Bearer', '').strip()
                db_name = ManagerParent.objects.filter(token=au).values_list('db_name')

                if db_name:
                    for e in db_name:
                        school_name = e[0]
                parent_id = ManagerParent.objects.filter(token=au).values_list('parent_id')

                if parent_id:
                    for e in parent_id:
                        parent_id = e[0]
                ManagerParent.objects.filter(parent_id=parent_id[0][0], db_name=school_name).update(
                    mobile_token='')
                student_id = request.data.get('student_id')
                canteen_banned = request.data.get('canteen_banned')
                result = {'result': 'erorr'}
                with connections[school_name].cursor() as cursor:
                    cursor.execute(
                        "select year_id, user_id,canteen_spending from student_student WHERE id=%s",
                        [student_id])
                    student_info = cursor.fetchall()

                    cursor.execute(
                        "select branch_id,company_id from res_users WHERE id=%s",
                        [student_info[0][1]])
                    student_info_users = cursor.fetchall()

                    cursor.execute(
                        "select id from banned_food WHERE student_id = %s and year_id=%s and branch_id=%s and company_id=%s",
                        [student_id, student_info[0][0], student_info_users[0][0], student_info_users[0][0]])
                    allergies_food = cursor.fetchall()

                    allergies_food = list(set(allergies_food))
                    if allergies_food:
                        cursor.execute(
                            "select id,product_id,pos_category from banned_food WHERE id in %s",
                            [tuple(allergies_food)])
                        allergies_food1 = cursor.fetchall()
                        cursor.execute(
                            "delete from banned_food where student_id=%s",
                            [student_id])
                        for allergies in range(len(allergies_food)):
                            if allergies_food[allergies] not in canteen_banned:

                                if allergies_food1[allergies][2]:

                                    cursor.execute(
                                        "INSERT INTO banned_food(year_id, student_id, branch_id,company_id,pos_category)VALUES (%s,%s,%s,%s,%s);",
                                        [student_info[0][0], student_id, student_info_users[0][0],
                                         student_info_users[0][0],
                                         allergies_food1[allergies][2]])
                                else:
                                    cursor.execute(
                                        "INSERT INTO banned_food(year_id, student_id, branch_id,company_id,product_id)VALUES (%s,%s,%s,%s,%s);",
                                        [student_info[0][0], student_id, student_info_users[0][0],
                                         student_info_users[0][0],
                                         allergies_food1[allergies][1]])

                    for allergies in canteen_banned:
                        cursor.execute(
                            "INSERT INTO banned_food(year_id, student_id, branch_id,company_id,pos_category)VALUES (%s,%s,%s,%s,%s);",
                            [student_info[0][0], student_id, student_info_users[0][0], student_info_users[0][0],
                             allergies])
            result = {'result': 'ok'}
            return Response(result)
            result = {'result': 'Not Authorization'}
            return Response(result)
        result = {'result': 'Not headers'}
        return Response(result)


@api_view(['GET'])
def get_category_Item(request):
    if request.method == 'GET':
        if request.headers:
            if request.headers.get('Authorization'):
                au = request.headers.get('Authorization').replace('Bearer', '').strip()
                db_name = ManagerParent.objects.filter(token=au).values_list('db_name')

                if db_name:
                    for e in db_name:
                        school_name = e[0]
                parent_id = ManagerParent.objects.filter(token=au).values_list('parent_id')

                if parent_id:
                    for e in parent_id:
                        parent_id = e[0]
                ManagerParent.objects.filter(parent_id=parent_id[0][0], db_name=school_name).update(
                    mobile_token='')
                date = []
                category = []
                with connections[school_name].cursor() as cursor:
                    # canteen_spending
                    # student_id = request.data.get('student_id')
                    # cursor.execute(
                    #     "select year_id, user_id,canteen_spending from student_student WHERE id=%s",
                    #     [student_id])
                    # student_info = cursor.fetchall()
                    #
                    # cursor.execute(
                    #     "select branch_id,company_id from res_users WHERE id=%s",
                    #     [student_info[0][1]])
                    # student_info_users = cursor.fetchall()
                    # res.config.settings
                    # cursor.execute("select currency_id from  res_config_settings ",
                    #                [])
                    # currency_id = cursor.fetchall()
                    # cursor.execute("select name from res_currency WHERE id=%s",
                    #                [currency_id[0][0]])
                    # currency = cursor.fetchall()
                    category.append({"name": 'all',
                                     "id": 0,
                                     "icon": "https://trackware-schools.s3.eu-central-1.amazonaws.com/allergic.svg",
                                     "sta": True

                                     })

                    cursor.execute("select id,name,parent_id from pos_category WHERE parent_id isNull",
                                   [])
                    pos_category1 = cursor.fetchall()
                    # print(pos_category1)

                    cursor.execute(
                        "select id,name,pos_categ_id,list_price,image_url from product_template WHERE is_canteen=%s",
                        [True])
                    product_template = cursor.fetchall()
                    for category1 in product_template:
                        type = 'all'
                        if category1[2]:
                            cursor.execute("select id,name,parent_id from pos_category WHERE id=%s",
                                           [category1[2]])
                            pos_category = cursor.fetchall()
                            if pos_category[0][2]:
                                cursor.execute("select id,name,parent_id from pos_category WHERE id=%s",
                                               [pos_category[0][2]])
                                pos_category = cursor.fetchall()

                            type = pos_category[0][1]
                        date.append({
                            "name": str(category1[1]),
                            "id": category1[0],
                            "type": str(type),
                            "price": str(category1[3]) + " " + str('JOD'),
                            "image": "https://trackware-schools.s3.eu-central-1.amazonaws.com/" + category1[4] if
                            category1[4] else 'https://trackware-schools.s3.eu-central-1.amazonaws.com/product.png',

                        })

                    for category1 in pos_category1:
                        category.append({"name": category1[1],
                                         "id": category1[0],
                                         "icon": "https://trackware-schools.s3.eu-central-1.amazonaws.com/allergic.svg",
                                         "sta": False

                                         })
                result = {'category': category, "product": date}
                return Response(result)
            result = {'result': 'Not Authorization'}
            return Response(result)
        result = {'result': 'Not headers'}
        return Response(result)


@api_view(['POST'])
def post_banned_item(request):
    if request.method == 'POST':
        if request.headers:
            if request.headers.get('Authorization'):
                au = request.headers.get('Authorization').replace('Bearer', '').strip()
                db_name = ManagerParent.objects.filter(token=au).values_list('db_name')

                if db_name:
                    for e in db_name:
                        school_name = e[0]
                parent_id = ManagerParent.objects.filter(token=au).values_list('parent_id')

                if parent_id:
                    for e in parent_id:
                        parent_id = e[0]
                ManagerParent.objects.filter(parent_id=parent_id[0][0], db_name=school_name).update(
                    mobile_token='')
                student_id = request.data.get('student_id')
                canteen_banned = request.data.get('canteen_banned')
                result = {'result': 'erorr'}
                with connections[school_name].cursor() as cursor:
                    cursor.execute(
                        "select year_id, user_id,canteen_spending from student_student WHERE id=%s",
                        [student_id])
                    student_info = cursor.fetchall()

                    cursor.execute(
                        "select branch_id,company_id from res_users WHERE id=%s",
                        [student_info[0][1]])
                    student_info_users = cursor.fetchall()

                    cursor.execute(
                        "select id from banned_food WHERE student_id = %s and year_id=%s and branch_id=%s and company_id=%s",
                        [student_id, student_info[0][0], student_info_users[0][0], student_info_users[0][0]])
                    allergies_food = cursor.fetchall()

                    allergies_food = list(set(allergies_food))
                    canteen_banned = list(set(canteen_banned))
                    if allergies_food:
                        cursor.execute(
                            "select id,product_id,pos_category from banned_food WHERE id in %s",
                            [tuple(allergies_food)])
                        allergies_food1 = cursor.fetchall()
                        cursor.execute(
                            "delete from banned_food where student_id=%s",
                            [student_id])

                        for allergies in range(len(allergies_food)):
                            if allergies_food[allergies] not in canteen_banned:

                                if allergies_food1[allergies][2]:

                                    cursor.execute(
                                        "INSERT INTO banned_food(year_id, student_id, branch_id,company_id,pos_category)VALUES (%s,%s,%s,%s,%s);",
                                        [student_info[0][0], student_id, student_info_users[0][0],
                                         student_info_users[0][0],
                                         allergies_food1[allergies][2]])
                                else:
                                    cursor.execute(
                                        "INSERT INTO banned_food(year_id, student_id, branch_id,company_id,product_id)VALUES (%s,%s,%s,%s,%s);",
                                        [student_info[0][0], student_id, student_info_users[0][0],
                                         student_info_users[0][0],
                                         allergies_food1[allergies][1]])
                    for allergies in canteen_banned:
                        cursor.execute(
                            "INSERT INTO banned_food(year_id, student_id, branch_id,company_id,product_id)VALUES (%s,%s,%s,%s,%s);",
                            [student_info[0][0], student_id, student_info_users[0][0], student_info_users[0][0],
                             allergies])
            result = {'result': 'ok'}
            return Response(result)
            result = {'result': 'Not Authorization'}
            return Response(result)
        result = {'result': 'Not headers'}
        return Response(result)


@api_view(['POST'])
def post_sec_item(request):
    if request.method == 'POST':
        if request.headers:
            if request.headers.get('Authorization'):
                au = request.headers.get('Authorization').replace('Bearer', '').strip()
                db_name = ManagerParent.objects.filter(token=au).values_list('db_name')

                if db_name:
                    for e in db_name:
                        school_name = e[0]
                parent_id = ManagerParent.objects.filter(token=au).values_list('parent_id')

                if parent_id:
                    for e in parent_id:
                        parent_id = e[0]
                ManagerParent.objects.filter(parent_id=parent_id[0][0], db_name=school_name).update(
                    mobile_token='')
                student_id = request.data.get('student_id')
                canteen_banned = request.data.get('canteen_banned')
                day_id = request.data.get('day_id')
                with connections[school_name].cursor() as cursor:
                    cursor.execute(
                        "select year_id, user_id,canteen_spending from student_student WHERE id=%s",
                        [student_id])
                    student_info = cursor.fetchall()

                    cursor.execute(
                        "select branch_id,company_id from res_users WHERE id=%s",
                        [student_info[0][1]])
                    student_info_users = cursor.fetchall()
                    cursor.execute(
                        "SELECT id  FROM allergies_food_day WHERE student_id = %s and year_id=%s and branch_id=%s and company_id=%s and day_id=%s",
                        [student_id, student_info[0][0], student_info_users[0][0], student_info_users[0][0], day_id])
                    student_food_day = cursor.fetchall()
                    student_food_day = list(set(student_food_day))
                    canteen_banned = list(set(canteen_banned))
                    cursor.execute(
                        "delete from allergies_food_day where student_id=%s and  year_id=%s and branch_id=%s and company_id=%s and day_id=%s",
                        [student_id, student_info[0][0], student_info_users[0][0], student_info_users[0][0], day_id])

                    for allergies in student_food_day:
                        if allergies[0] not in canteen_banned:
                            cursor.execute(
                                "INSERT INTO allergies_food_day(year_id, student_id, branch_id,company_id,product_id,day_id)VALUES (%s,%s,%s,%s,%s,%s);",
                                [student_info[0][0], student_id, student_info_users[0][0], student_info_users[0][0],
                                 allergies, day_id])
                    for allergies in canteen_banned:
                        cursor.execute(
                            "INSERT INTO allergies_food_day(year_id, student_id, branch_id,company_id,product_id,day_id)VALUES (%s,%s,%s,%s,%s,%s);",
                            [student_info[0][0], student_id, student_info_users[0][0], student_info_users[0][0],
                             allergies, day_id])

                result = {'result': 'ok'}
                return Response(result)
            result = {'result': 'Not Authorization'}
            return Response(result)
        result = {'result': 'Not headers'}
        return Response(result)


@api_view(['POST'])
def get_banned_food_s(request):
    if request.method == 'POST':
        if request.headers:
            if request.headers.get('Authorization'):
                au = request.headers.get('Authorization').replace('Bearer', '').strip()
                db_name = ManagerParent.objects.filter(token=au).values_list('db_name')

                if db_name:
                    for e in db_name:
                        school_name = e[0]
                parent_id = ManagerParent.objects.filter(token=au).values_list('parent_id')

                if parent_id:
                    for e in parent_id:
                        parent_id = e[0]
                ManagerParent.objects.filter(parent_id=parent_id[0][0], db_name=school_name).update(
                    mobile_token='')
                student_id = request.data.get('student_id')
                data_cat = []
                date_ite = []
                with connections[school_name].cursor() as cursor:
                    cursor.execute(
                        "select year_id, user_id,canteen_spending from student_student WHERE id=%s",
                        [student_id])
                    student_info = cursor.fetchall()

                    cursor.execute(
                        "select branch_id,company_id from res_users WHERE id=%s",
                        [student_info[0][1]])
                    student_info_users = cursor.fetchall()

                    cursor.execute(
                        "select id,pos_category,product_id from banned_food WHERE student_id = %s and year_id=%s and branch_id=%s and company_id=%s ",
                        [student_id, student_info[0][0], student_info_users[0][0], student_info_users[0][0]])
                    banned_food = cursor.fetchall()
                    for allergies in banned_food:

                        if allergies[1]:
                            category_sup = ''
                            cursor.execute("select id,name from pos_category WHERE id=%s",
                                           [allergies[1]])
                            pos_category = cursor.fetchall()
                            if pos_category[0]:
                                cursor.execute("select id,name from pos_category WHERE parent_id=%s ",
                                               [pos_category[0][0]])
                                pos_category_sup = cursor.fetchall()
                                if pos_category_sup:
                                    for category in pos_category_sup:
                                        category_sup += category[1] + ''

                            data_cat.append({
                                "name": pos_category[0][1],
                                "id": allergies[0],
                                "category_sup": category_sup

                            })
                        else:
                            cursor.execute(
                                "select id,name,pos_categ_id,list_price,is_canteen,image_url from product_template WHERE id=%s ",
                                [allergies[2]])
                            product_template = cursor.fetchall()
                            type = ''
                            if product_template[0][2]:
                                cursor.execute("select id,name from pos_category WHERE id=%s",
                                               [product_template[0][2]])
                                pos_category = cursor.fetchall()
                                type = pos_category[0][1] if pos_category[0][1] else ''
                            date_ite.append({
                                "name": str(product_template[0][1]),
                                "id": allergies[0],
                                "price": str(product_template[0][3]) + " " + str('JOD'),
                                "image": "https://trackware-schools.s3.eu-central-1.amazonaws.com/" +
                                         product_template[0][5] if product_template[0][
                                    5] else 'https://trackware-schools.s3.eu-central-1.amazonaws.com/product.png',

                                "type": type

                            })

                result = {'date_ite': date_ite, "data_cat": data_cat}
                return Response(result)
            result = {'result': 'Not Authorization'}
            return Response(result)
        result = {'result': 'Not headers'}
        return Response(result)


@api_view(['POST'])
def delete_banned(request):
    if request.method == 'POST':
        if request.headers:
            if request.headers.get('Authorization'):
                au = request.headers.get('Authorization').replace('Bearer', '').strip()
                db_name = ManagerParent.objects.filter(token=au).values_list('db_name')

                if db_name:
                    for e in db_name:
                        school_name = e[0]
                parent_id = ManagerParent.objects.filter(token=au).values_list('parent_id')

                if parent_id:
                    for e in parent_id:
                        parent_id = e[0]
                ManagerParent.objects.filter(parent_id=parent_id[0][0], db_name=school_name).update(
                    mobile_token='')

                banned_id = request.data.get('banned_id')

                with connections[school_name].cursor() as cursor:
                    cursor.execute(
                        "delete from banned_food where id=%s",
                        [banned_id])
                result = {'result': 'ok'}
                return Response(result)
            result = {'result': 'Not Authorization'}
            return Response(result)
        result = {'result': 'Not headers'}
        return Response(result)


@api_view(['POST'])
def delete_food(request):
    if request.method == 'POST':
        if request.headers:
            if request.headers.get('Authorization'):
                au = request.headers.get('Authorization').replace('Bearer', '').strip()
                db_name = ManagerParent.objects.filter(token=au).values_list('db_name')

                if db_name:
                    for e in db_name:
                        school_name = e[0]
                parent_id = ManagerParent.objects.filter(token=au).values_list('parent_id')

                if parent_id:
                    for e in parent_id:
                        parent_id = e[0]
                ManagerParent.objects.filter(parent_id=parent_id[0][0], db_name=school_name).update(
                    mobile_token='')

                id = request.data.get('id')

                with connections[school_name].cursor() as cursor:
                    cursor.execute(
                        "delete from allergies_food_day where id=%s",
                        [id])
                result = {'result': 'ok'}
                return Response(result)
            result = {'result': 'Not Authorization'}
            return Response(result)
        result = {'result': 'Not headers'}
        return Response(result)


@api_view(['POST'])
def get_food_s(request):
    if request.method == 'POST':
        if request.headers:
            if request.headers.get('Authorization'):
                au = request.headers.get('Authorization').replace('Bearer', '').strip()
                db_name = ManagerParent.objects.filter(token=au).values_list('db_name')

                if db_name:
                    for e in db_name:
                        school_name = e[0]
                parent_id = ManagerParent.objects.filter(token=au).values_list('parent_id')

                if parent_id:
                    for e in parent_id:
                        parent_id = e[0]
                ManagerParent.objects.filter(parent_id=parent_id[0][0], db_name=school_name).update(
                    mobile_token='')
                student_id = request.data.get('student_id')
                day_id = request.data.get('day_id')

                date_ite = []
                with connections[school_name].cursor() as cursor:
                    cursor.execute(
                        "select year_id, user_id,canteen_spending from student_student WHERE id=%s",
                        [student_id])
                    student_info = cursor.fetchall()

                    cursor.execute(
                        "select branch_id,company_id from res_users WHERE id=%s",
                        [student_info[0][1]])
                    student_info_users = cursor.fetchall()
                    cursor.execute(
                        "SELECT id,product_id  FROM allergies_food_day WHERE student_id = %s and year_id=%s and branch_id=%s and company_id=%s and day_id=%s",
                        [student_id, student_info[0][0], student_info_users[0][0], student_info_users[0][0], day_id])
                    student_food_day = cursor.fetchall()

                    for allergies in student_food_day:

                        cursor.execute(
                            "select id,name,pos_categ_id,list_price,is_canteen,image_url from product_template WHERE id=%s ",
                            [allergies[1]])
                        product_template = cursor.fetchall()
                        type = ''
                        if product_template[0][2]:
                            cursor.execute("select id,name from pos_category WHERE id=%s",
                                           [product_template[0][2]])
                            pos_category = cursor.fetchall()
                            type = pos_category[0][1] if pos_category[0][1] else ''
                        date_ite.append({
                            "name": str(product_template[0][1]),
                            "id": allergies[0],
                            "price": str(product_template[0][3]) + " " + str('JOD'),
                            "image": "https://trackware-schools.s3.eu-central-1.amazonaws.com/" + product_template[0][
                                5] if product_template[0][
                                5] else 'https://trackware-schools.s3.eu-central-1.amazonaws.com/product.png',
                            "type": type

                        })

                result = {'date_item': date_ite}
                return Response(result)
            result = {'result': 'Not Authorization'}
            return Response(result)
        result = {'result': 'Not headers'}
        return Response(result)

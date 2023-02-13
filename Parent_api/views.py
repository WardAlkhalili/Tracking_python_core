
from selectors import SelectSelector

from django.shortcuts import render

# Create your views here.
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import *
from django.db import connections
from django.core.files.base import ContentFile
from django.http.response import Http404, JsonResponse
from django.http import HttpResponse
from django.core.serializers import serialize
from collections import ChainMap
from rest_framework import status
from itertools import chain
# from ..Driver_api.models import Manager
# from yousef.api.Tracking_python_core.Driver_api.models import Manager

import pandas as pd
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
import json
import calendar
from datetime import date, timedelta, datetime
import requests
import pytz
import datetime
from rest_framework import status


@api_view(['POST'])
def parent_login(request):
    if request.method == 'POST':
        password = request.data.get('password')
        user_name = request.data.get('user_name')
        school_name = request.data.get('school_name')
        mobile_token = request.data.get('mobile_token')

        # url = "http://localhost:9098/web/session/authenticate"
        # url = 'https://' + school_name + '.staging.trackware.com/web/session/authenticate'

        url = 'https://tst.tracking.trackware.com/web/session/authenticate'
        # url = 'http://127.0.0.1:9098/web/session/authenticate'
        try:
            body = json.dumps({"jsonrpc": "2.0", "params": {"db": school_name, "login": user_name, "password": password}})
            headers = {
                'Content-Type': 'application/json',
            }

            response1 = requests.request("POST", url, headers=headers, data=body)

            response = response1.json()
            if "error" in response:
                result = {
                    "status": "erorrq"}
                return Response(result)
            session = response1.cookies
            uid = response['result']['uid']
            company_id = response['result']['company_id']

        except:
            result = {
                "status": "erorr2"
                          ""}
            return Response(result)
        with connections[school_name].cursor() as cursor:
            cursor.execute("select id from school_parent WHERE user_id = %s", [response['result']['uid']])
            columns2 = (x.name for x in cursor.description)
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
            manager_parent = ManagerParent(token=unique_id, db_name=school_name, user_id=uid,
                                           parent_id=parent_id[0][0],
                                           school_id=company_id, mobile_token=mobile_token)
            # manager_parent = ManagerParent(token=token_auth, db_name=school_name, user_id=uid,
            #                                parent_id=parent_id[0][0],
            #                                school_id=company_id, mobile_token=mobile_token)

            manager_parent.save()

            # result = {
            #     'db_name': school_name,
            #     'user_id': uid,
            #     'parent_id': parent_id[0][0],
            #     'token': token_auth.key,
            #     'school_id': company_id
            #
            # }

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


import datetime


# from ..Driver_api.models import *


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
                        with connections[school_name].cursor() as cursor:
                            cursor.execute(
                                "INSERT INTO feed_back(model_id, model_type, feed_back, impression, student_id)VALUES (%s, %s,%s,%s,%s);",
                                [25, 'App\Model\Parents', feed_back, 3, student_id])
                            # cursor.execute("INSERT INTO feed_back(feed_back, impression, student_id)VALUES (%s, %s, %s);", [feed_back,impression,student_id])
                            # columns = (x.name for x in cursor.description)
                            # data_id_bus = cursor.fetchall()
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
                            columns = (x.name for x in cursor.description)
                            data_id_bus = cursor.fetchall()

                            if data_id_bus[0][0]:

                                data = json.loads(data_id_bus[0][0])

                                if type(data['notifications']) is str:
                                    li = list(data['notifications'].split(","))
                                    result={
                                              "notifications": {
                                                "locale": "ar" if "ar" in li[3] else 'en' ,
                                                "nearby": True if "true"in li[0] else False ,
                                                "check_in": True if "true" in li[1] else False ,
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
                            columns = (x.name for x in cursor.description)
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
                            columns = (x.name for x in cursor.description)
                            student_name = cursor.fetchall()
                            cursor.execute(
                                "select  id,date,state from pickup_request WHERE name = %s AND parent_id = %s ORDER BY ID DESC LIMIT 1",
                                [student_name[0][0], parent_id])
                            columns = (x.name for x in cursor.description)
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
                                    columns = (x.name for x in cursor.description)
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
                                columns = (x.name for x in cursor.description)
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
                        # school_name = ManagerParent.pincode('iks')
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


                    for e in parent_id:
                        parent_id = e[0]
                    for e in school_id:
                        school_id = e[0]
                    if db_name:
                        for e in db_name:
                            school_name = e[0]

                        school_name = ManagerParent.pincode(school_name)
                        with connections[school_name].cursor() as cursor:
                            cursor.execute(
                                "select activate_app_map from school_parent WHERE id = %s",
                                [parent_id])
                            columns = (x.name for x in cursor.description)
                            parent_show_map = cursor.fetchall()
                            cursor.execute(
                                "select  id,display_name_search,user_id,pick_up_type,drop_off_type,image_url,father_id,mother_id,state,academic_grade_name1,pick_up_type from student_student WHERE (father_id = %s OR mother_id = %s OR responsible_id_value = %s)  And state = 'done'",
                                [parent_id, parent_id, parent_id])
                            columns = (x.name for x in cursor.description)
                            student = cursor.fetchall()
                            student1 = []
                            columnNames = [column[0] for column in cursor.description]
                            for record in student:
                                student1.append(dict(zip(columnNames, record)))
                            studen_list = []
                            cursor.execute(
                                "select  lat,lng,pickup_request_distance,change_location,show_map,enable_parents_to_confirm_student_pickup,pickup_request_distance from transport_setting  ORDER BY ID DESC LIMIT 1")
                            columns = (x.name for x in cursor.description)
                            setting = cursor.fetchall()

                            show_map=True
                            if (parent_show_map[0][0] == True):
                            # if (setting[0][4]==True and parent_show_map[0][0]==None) or (setting[0][4]==False and parent_show_map[0][0]==True) or (setting[0][4]and parent_show_map[0][0]) :
                                show_map =True
                            else:
                                show_map=False
                            cursor.execute(
                                "select  name,phone from res_company WHERE id = %s ",
                                [school_id])
                            columns = (x.name for x in cursor.description)
                            school = cursor.fetchall()
                            for rec in range(len(student)):
                                # round = self.env["round.schedule"].search([('student_id', '=', self.id)])
                                is_active_round = False
                                student_round_id = 0
                                curr_date = date.today()

                                cursor.execute(
                                    "select  id  from school_day where name = %s",
                                    [calendar.day_name[curr_date.weekday()]])
                                day_name = cursor.fetchall()
                                cursor.execute(
                                    "select id from round_schedule WHERE  day_id = %s",
                                    [day_name[0][0]])
                                columns3 = (x.name for x in cursor.description)
                                rounds_details = cursor.fetchall()
                                for rou in range(len(rounds_details)):
                                    cursor.execute(
                                        "select round_schedule_id,transport_state from transport_participant WHERE round_schedule_id = %s and student_id = %s",
                                        [rounds_details[rou][0], student1[rec]['id']])
                                    columns4 = (x.name for x in cursor.description)
                                    rounds_count_student = cursor.fetchall()

                                    if rounds_count_student:
                                        cursor.execute(
                                            "select round_id from round_schedule WHERE  id = %s",
                                            [rounds_count_student[0][0]])
                                        columns3 = (x.name for x in cursor.description)
                                        rounds = cursor.fetchall()
                                        cursor.execute(
                                            "select is_active from transport_round WHERE  id = %s",
                                            [rounds[0][0]])
                                        columns3 = (x.name for x in cursor.description)
                                        is_active = cursor.fetchall()
                                        if is_active[0][0]:
                                            student_round_id = rounds[0][0]
                                            is_active_round = is_active[0][0]
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
                                        "icon": "https://trackware-schools.s3.eu-central-1.amazonaws.com/Assignments.png"
                                    },
                                    "Badges": {
                                        # "url": "https://" + school_name + ".staging.trackware.com/my/Badges/",tst.tracking.trackware.com
                                        # "arabic_url": "https://" + school_name + ".staging.trackware.com/ar_SY/my/Badges/",
                                        "url": "https://tst.tracking.trackware.com/my/Badges/",
                                        "arabic_url": "tst.tracking.trackware.com/ar_SY/my/Badges/",
                                        "name": "Badges",
                                        "name_ar": "الشارات",
                                        "icon": "https://trackware-schools.s3.eu-central-1.amazonaws.com/Badge.png"
                                    },
                                    "Weeklyplans":
                                        {
                                            # "url": "https://" + school_name + ".staging.trackware.com/my/Weekly-plans/",
                                            # "arabic_url": "https://" + school_name + ".staging.trackware.com/ar_SY/my/Weekly-plans/",
                                            "url": "https://tst.tracking.trackware.com/my/Weekly-plans/",
                                            "arabic_url": "https://tst.tracking.trackware.com/ar_SY/my/Weekly-plans/",
                                            "name": "Weeklyplans",
                                            "name_ar": "الخطط الأسبوعية",
                                            "icon": "https://trackware-schools.s3.eu-central-1.amazonaws.com/Weekly+Plans.png"
                                        },
                                    "Assignments": {
                                        "url": "https://tst.tracking.trackware.com/my/Assignments/",
                                        "arabic_url": "https://tst.tracking.trackware.com/ar_SY/my/Assignments/",
                                        # "url": "https://" + school_name + ".staging.trackware.com/my/Assignments/",
                                        # "arabic_url": "https://" + school_name + ".staging.trackware.com/ar_SY/my/Assignments/",
                                        "name": "Assignments",
                                        "name_ar": "الواجبات الالكترونية",
                                        "icon": "https://trackware-schools.s3.eu-central-1.amazonaws.com/Assignments.png"
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
                                         "icon": "https://trackware-schools.s3.eu-central-1.amazonaws.com/Events.png"
                                         },
                                    "Homeworks":
                                        {"name": "Homeworks",
                                         # "url": "https://" + school_name + ".staging.trackware.com/my/Homeworks/",
                                         # "arabic_url": "https://" + school_name + ".staging.trackware.com/ar_SY/my/Homeworks/",
                                         "url": "https://tst.tracking.trackware.com/my/Homeworks/",
                                         "arabic_url": "https://tst.tracking.trackware.com/ar_SY/my/Homeworks/",
                                         "name_ar": "الواجبات المنزلية",
                                         "icon": "https://trackware-schools.s3.eu-central-1.amazonaws.com/worksheets.png"
                                         },
                                    "Calendar":
                                        {"name": "Calendar",
                                         "url": "https://tst.tracking.trackware.com/my/Calendar/",
                                         "arabic_url": "https://tst.tracking.trackware.com/ar_SY/my/Calendar/",
                                         # "url": "https://" + school_name + ".staging.trackware.com/my/Calendar/",
                                         # "arabic_url": "https://" + school_name + ".staging.trackware.com/ar_SY/my/Calendar/",
                                         "name_ar": "التقويم",
                                         "icon": "https://trackware-schools.s3.eu-central-1.amazonaws.com/School+Calendar.png"
                                         },

                                    "Clinic":
                                        {"name": "Clinic",
                                         "name_ar": "العيادة",
                                         # "url": "https://" + school_name + ".staging.trackware.com/my/Clinic/",
                                         # "arabic_url": "https://" + school_name + ".staging.trackware.com/ar_SY/my/Clinic/",
                                         "url": "https://tst.tracking.trackware.com/my/Clinic/",
                                         "arabic_url": "https://tst.tracking.trackware.com/ar_SY/my/Clinic/",
                                         "arabic_name": "العيادة",
                                         "icon": "https://trackware-schools.s3.eu-central-1.amazonaws.com/Clinic.png"
                                         }
                                }
                                url_m = {}
                                model_list = (
                                    "Badges", "Clinic", "Calendar", "Homework", "Events", "Online Assignments",
                                    "Weekly Plans",'Online Exams')
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
                                        x['Homeworks']['url'] = x['Homeworks']['url'] + str(student1[rec]['user_id'])
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

                                cursor.execute(
                                    "select name from ir_ui_menu where name ='Tracking'")
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
                                        "icon": "https://trackware-schools.s3.eu-central-1.amazonaws.com/Absence.png"
                                    }
                                    )
                                    show_absence = True
                                try:
                                    cursor.execute(
                                        "select is_portal_exist from school_parent")
                                    is_portal_exist = cursor.fetchall()
                                    # sql = """select is_portal_exist from school_parent '"""
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
                                                "icon": "https://trackware-schools.s3.eu-central-1.amazonaws.com/Absence.png"
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

                                student_st=''
                                assistant_id=0
                                assistant_name=''
                                assistant_mobile_number=''
                                driver_mobile_token=''
                                driver_mobile_number=''
                                driver_name=''
                                bus_id=0
                                round_type=''
                                round_name=''
                                if bool(is_active_round):

                                    student_st=rounds_count_student[0][1] if rounds_count_student else ""

                                    cursor.execute(
                                        "select name,type,attendant_id,vehicle_id,driver_id from transport_round WHERE id = %s",
                                        [ int(student_round_id)])
                                    round_info = cursor.fetchall()
                                    round_type=round_info[0][1]
                                    round_name=round_info[0][0]
                                    assistant_id=int(round_info[0][2])
                                    cursor.execute(
                                        "select name,mobile_phone from hr_employee WHERE id = %s",
                                        [assistant_id])
                                    assistant = cursor.fetchall()
                                    assistant_mobile_number=assistant[0][1]
                                    assistant_name = assistant[0][0]

                                    cursor.execute(
                                        "select name,mobile from res_partner WHERE id = %s",
                                        [round_info[0][4]])
                                    driver_info = cursor.fetchall()
                                    driver_name=driver_info[0][0]
                                    driver_mobile_number = driver_info[0][1]
                                    cursor.execute(
                                        "select bus_no from fleet_vehicle WHERE id = %s",
                                        [round_info[0][3]])
                                    fleet_info = cursor.fetchall()
                                    bus_id=int(fleet_info[0][0])
                                    # fleet.vehicle

                                student_grade = None
                                # ----------------------

                                cursor.execute(
                                    "SELECT student_distribution_line_id FROM student_distribution_line_student_student_rel WHERE student_student_id=%s",
                                    [student1[rec]['id']])
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
                                        student_grade=academic_grade[0][0]
                                if student_grade==None:
                                    cursor.execute(
                                        "select user_id from student_student where id=%s",
                                        [student1[rec]['id']])
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
                                            if class_id_q:
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
                                studen_list.append({

                                    "name": student1[rec]['display_name_search'],
                                    "id": student1[rec]['id'],
                                    "user_id": student1[rec]['user_id'],
                                    "avatar":'https://trackware-schools.s3.eu-central-1.amazonaws.com/' + str(student1[rec]['image_url']) if student1[rec]['image_url'] else 'https://s3.eu-central-1.amazonaws.com/trackware.schools/public_images/default_student.png',
                                    "school_id": int(school_id),
                                    "student_grade": student_grade,
                                    "drop_off_by_parent": drop,
                                    "pickup_by_parent": drop,
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

                                    "show_absence":show_absence,
                                    "student_status": {
                                        "activity_type": str(student_st),
                                        "round_id":int(student_round_id) ,
                                        "datetime": ""
                                    },
                                    # "mobile_numbers": [
                                    #     {
                                    #         "mobile": school[0][1],
                                    #         "name": school[0][0],
                                    #         "type": "school"
                                    #     },
                                    #     {
                                    #         "mobile": "",
                                    #         "name": "My Company (San Francisco)",
                                    #         "type": "school"
                                    #     },
                                    #     {
                                    #         "mobile": "",
                                    #         "name": "My Company (San Francisco)",
                                    #         "type": "school"
                                    #     }
                                    # ],
                                    "features": model,
                                })
                            result = {'message':'','students': studen_list, "parent_id": int(parent_id)}

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
    return year + "-" + month + "-" + day + " " + hour + ":" + minute + ":" + second


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
                    for e in parent_id:
                        parent_id = e[0]
                    if db_name:
                        for e in db_name:
                            school_name = e[0]
                        school_name = ManagerParent.pincode(school_name)
                        start_date = request.data.get('start_date')
                        end_date = request.data.get('end_date')
                        student_round=[]
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
                                "select  id,display_name_search,image_url from student_student WHERE (father_id = %s OR mother_id = %s OR responsible_id_value = %s)  And state = 'done'",
                                [parent_id, parent_id, parent_id])
                            student = cursor.fetchall()
                            student_round_id = []

                            for rec1 in student:


                                message_ids = []
                                for rec in school_message:
                                    message_ids.append(rec[0])
                                if message_ids:
                                    cursor.execute(
                                        "select  student_student_id  from school_message_student_student where school_message_id in %s",
                                        [tuple(message_ids)])
                                    school_message_student_student = cursor.fetchall()
                                    cursor.execute(
                                        "select  school_message_id from school_message_student_student WHERE school_message_id in %s AND student_student_id = %s",
                                        [tuple(message_ids), rec1[0]])
                                    message_student = cursor.fetchall()
                                    message_id = []
                                    for rec in message_student:
                                        message_id.append(rec[0])
                                    if message_id:
                                        # get school message
                                        cursor.execute(
                                            "select  id,search_type,title,message,create_date,date from school_message WHERE id in %s",
                                            [tuple(list(dict.fromkeys(message_id)))])
                                        school_message1 = cursor.fetchall()

                                        for rec in range(len(school_message1)):
                                            deadline = school_message1[rec][4]

                                            notifications.append({
                                                "avatar": "https://s3.eu-central-1.amazonaws.com/notifications-images/mobile-notifications-icons/notification_icon_msg_admin.png",
                                                "date_time": date_time(deadline),
                                                "notifications_text": school_message1[rec][3] if school_message1[rec][
                                                    3] else '',
                                                "create_date": school_message1[rec][5],
                                                "notifications_title": school_message1[rec][2] if school_message1[rec][
                                                    2] else '',
                                            })

                                        #
                            #     student_id.append(rec1[0])
                                cursor.execute(
                                    "select  round_schedule_id from transport_participant WHERE student_id = %s",
                                    [rec1[0]])
                                round_schedule_id = cursor.fetchall()


                            #     round_schedule_ids = []
                            #     get bus message
                                for rec in round_schedule_id:


                                    cursor.execute(
                                        "select  round_id from round_schedule WHERE id = %s",
                                        [rec[0]])
                                    round_schedule = cursor.fetchall()


                                    round_schedules = []
                                    student_round_h=[]
                                    for rec in round_schedule:


                                        if rec[0] in  student_round:

                                            continue
                                        else:
                                            cursor.execute(
                                                "select  type from transport_round WHERE id = %s",
                                                [rec[0]])

                                            type = cursor.fetchall()

                                            if type[0][0] =='pick_up':
                                                student_round_h.append(rec[0])
                                            student_round.append(rec[0])
                                            # student_round_id.append(rec[0])

                                            round_schedules.append(rec[0])
                                    round_schedules = list(dict.fromkeys(student_round))

                                    for rec_s in round_schedules:
                                        cursor.execute(
                                            "select  vehicle_id from transport_round WHERE id = %s",
                                            [rec_s])

                                        vehicle_id1 = cursor.fetchall()
                                        cursor.execute(
                                            "select bus_no from fleet_vehicle WHERE id = %s  ",
                                            [vehicle_id1[0][0]])
                                        bus_num1 = cursor.fetchall()

                                        cursor.execute(
                                            "select  name,vehicle_id,driver_id from transport_round WHERE id = %s  ",
                                            [rec_s])
                                        round_info = cursor.fetchall()
                                        if rec_s in student_round_id:
                                            pass
                                        else:
                                            student_round_id.append(rec_s)
                                            cursor.execute(
                                                "select  message_ar,create_date,type,round_id from sh_message_wizard WHERE round_id = %s and (type= %s or from_type =%s or from_type =%s ) ORDER BY ID DESC LIMIT 50",
                                                [rec_s,'emergency','App\Model\Driver','App\Model\sta' + str(parent_id)])
                                            sh_message_wizard = cursor.fetchall()

                                            # save bus message

                                            for message_wizard in range(len(sh_message_wizard)):
                                                test_round_id=[]
                                                date_mas=[]
                                                for std in student:
                                                    cursor.execute(
                                                        "select  id,round_id from round_student_history WHERE student_id = %s AND round_id=%s AND bus_check_in is not null AND  datetime >= %s AND  datetime < %s ",
                                                        [std[0],rec,datetime.datetime(
                                                            sh_message_wizard[message_wizard][1].year, sh_message_wizard[message_wizard][1].month,
                                                            sh_message_wizard[message_wizard][1].day),datetime.datetime(
                                                            sh_message_wizard[message_wizard][1].year, sh_message_wizard[message_wizard][1].month,
                                                            sh_message_wizard[message_wizard][1].day+1)])
                                                    attendance_round = cursor.fetchall()

                                                    if not attendance_round:

                                                        cursor.execute(
                                                            "select  is_active from transport_round WHERE id = %s  ",
                                                            [rec_s])
                                                        is_active = cursor.fetchall()
                                                        date_time_message=datetime.datetime(
                                                            sh_message_wizard[message_wizard][1].year, sh_message_wizard[message_wizard][1].month,
                                                            sh_message_wizard[message_wizard][1].day)
                                                        car_time=datetime.datetime(datetime.datetime.now().year,datetime.datetime.now().month,datetime.datetime.now().day)
                                                        if is_active[0][0] and car_time==date_time_message:
                                                            cursor.execute(
                                                                "select  round_schedule_id from transport_participant WHERE student_id = %s",
                                                                [std[0]])
                                                            round_schedule_id_tst = cursor.fetchall()
                                                            schedule_id=[]
                                                            for cha_round_s in round_schedule_id_tst:
                                                                schedule_id.append(cha_round_s[0])
                                                            if schedule_id:
                                                                cursor.execute(
                                                                    "select  round_id from round_schedule WHERE id in %s",
                                                                    [tuple(schedule_id)])
                                                                round_id_tst = cursor.fetchall()
                                                                round_id_student=[]
                                                                for r_id in round_id_tst:
                                                                    round_id_student.append(r_id[0])
                                                                if  rec_s in round_id_student:
                                                                    deadline = sh_message_wizard[message_wizard][1]
                                                                    notifications_text = str(
                                                                        sh_message_wizard[message_wizard][0]) if \
                                                                    sh_message_wizard[message_wizard][0] else ''
                                                                    if " just been " in notifications_text:
                                                                        if str(std[1]) in notifications_text:
                                                                            notifications.append({
                                                                                "notifications_text": notifications_text,
                                                                                "date_time": date_time(deadline),
                                                                                "create_date": deadline,
                                                                                "notifications_title": 'Bus notification',
                                                                                "avatar": "https://s3.eu-central-1.amazonaws.com/notifications-images/mobile-notifications-icons/notification_icon_check_in_drop.png"
                                                                            })
                                                                    elif "has not checked into the bus" in notifications_text:

                                                                        if str(std[1]) in notifications_text:
                                                                            notifications.append({
                                                                                "notifications_text": notifications_text,
                                                                                "date_time": date_time(deadline),
                                                                                "create_date": deadline,
                                                                                "notifications_title": "Absence notification",
                                                                                "avatar": "https://s3.eu-central-1.amazonaws.com/notifications-images/mobile-notifications-icons/notification_icon_check_in_drop.png"
                                                                            })
                                                                    elif "did not check into the bus today" in notifications_text:

                                                                        if str(std[1]) in notifications_text:
                                                                            notifications.append({
                                                                                "notifications_text": notifications_text,
                                                                                "date_time": date_time(deadline),
                                                                                "create_date": deadline,
                                                                                "notifications_title": "No Show Notification",
                                                                                "avatar": "https://s3.eu-central-1.amazonaws.com/notifications-images/mobile-notifications-icons/notification_icon_check_in_drop.png"
                                                                            })
                                                                    elif "just reached" in notifications_text:

                                                                        if str(std[1]) in notifications_text:
                                                                            notifications.append({
                                                                                "notifications_text": notifications_text,
                                                                                "date_time": date_time(deadline),
                                                                                "create_date": deadline,
                                                                                "notifications_title": "Bus notification",
                                                                                "avatar": "https://s3.eu-central-1.amazonaws.com/notifications-images/mobile-notifications-icons/notification_icon_check_in_drop.png"
                                                                            })
                                                                    else:

                                                                        notifications.append({
                                                                            "notifications_text": notifications_text,
                                                                            "date_time": date_time(deadline),
                                                                            "create_date": deadline,
                                                                            "notifications_title": "Message from bus no. " + str(
                                                                                bus_num1[0][0]) + "  " + str(std[1]),
                                                                            "avatar": "https://s3.eu-central-1.amazonaws.com/notifications-images/mobile-notifications-icons/notification_icon_check_in_drop.png"
                                                                        })

                                                        continue

                                                    deadline = sh_message_wizard[message_wizard][1]
                                                    notifications_text=str(sh_message_wizard[message_wizard][0]) if sh_message_wizard[message_wizard][0] else ''

                                                    if "just been" in notifications_text:

                                                        if str(std[1]) in notifications_text:
                                                            notifications.append({
                                                                "notifications_text":notifications_text ,
                                                                "date_time": date_time(deadline),
                                                                "create_date": deadline,
                                                                "notifications_title": 'Bus notification',
                                                                "avatar": "https://s3.eu-central-1.amazonaws.com/notifications-images/mobile-notifications-icons/notification_icon_check_in_drop.png"
                                                            })
                                                    elif "did not check into the bus today" in notifications_text:

                                                        if str(std[1]) in notifications_text:
                                                            notifications.append({
                                                                "notifications_text": notifications_text,
                                                                "date_time": date_time(deadline),
                                                                "create_date": deadline,
                                                                "notifications_title": "No Show Notification",
                                                                "avatar": "https://s3.eu-central-1.amazonaws.com/notifications-images/mobile-notifications-icons/notification_icon_check_in_drop.png"
                                                            })
                                                    elif "has not checked into the bus" in notifications_text:

                                                        if str(std[1]) in notifications_text:
                                                            notifications.append({
                                                                "notifications_text":notifications_text ,
                                                                "date_time": date_time(deadline),
                                                                "create_date": deadline,
                                                                "notifications_title": "Absence notification",
                                                                "avatar": "https://s3.eu-central-1.amazonaws.com/notifications-images/mobile-notifications-icons/notification_icon_check_in_drop.png"
                                                            })
                                                    elif "just reached" in notifications_text:

                                                        if str(std[1]) in notifications_text:
                                                            notifications.append({
                                                                "notifications_text": notifications_text,
                                                                "date_time": date_time(deadline),
                                                                "create_date": deadline,
                                                                "notifications_title": "Bus notification",
                                                                "avatar": "https://s3.eu-central-1.amazonaws.com/notifications-images/mobile-notifications-icons/notification_icon_check_in_drop.png"
                                                            })
                                                    else:
                                                        notifications.append({
                                                            "notifications_text": notifications_text,
                                                            "date_time": date_time(deadline),
                                                            "create_date": deadline,
                                                            "notifications_title": "Message from bus no. " + str(
                                                                bus_num1[0][0]) + "  " + str(std[1]),
                                                            "avatar": "https://s3.eu-central-1.amazonaws.com/notifications-images/mobile-notifications-icons/notification_icon_check_in_drop.png"
                                                        })

                                        if student_round_h:

                                            cursor.execute(
                                                "select  id,round_start from round_history WHERE round_id in %s and round_name in %s ORDER BY ID DESC LIMIT 1 ",
                                                [tuple(student_round_h), tuple(student_round_h)])
                                            round_history = cursor.fetchall()

                                            if round_history:
                                                history_round = []

                                                for round_h in round_history:
                                                    history_round.append(round_h[0])
                                                for std in student:
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
                                                                            "select  display_name_search from student_student WHERE  id = %s",
                                                                            [time_out[0][1]])
                                                                        name = cursor.fetchall()
                                                                        deadline = time_out[0][0] if time_out[0][0] else time_out[0][2]

                                                                        notifications.append({
                                                                            "notifications_text":name[0][ 0] + " has just reached the school.  ",
                                                                            "date_time":date_time(deadline),
                                                                            "create_date": deadline,
                                                                            "notifications_title":  "Bus Notification",
                                                                            "avatar": "https://s3.eu-central-1.amazonaws.com/notifications-images/mobile-notifications-icons/notification_icon_check_in_drop.png"
                                                                        })
                                        list_hist_student = []
                                        cursor.execute(
                                            " SELECT  notification_id FROM student_history WHERE (activity_type='absent-all' or activity_type='absent') and student_id=%s",
                                            [rec1[0]])
                                        student_history = cursor.fetchall()


                                        for mas in student_history:
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
                                                notifications.append({
                                                    "notifications_text": sh_message_wizard1[sh_message_bus][0],
                                                    "date_time": date_time(deadline),
                                                    "create_date": deadline,
                                                    "notifications_title": "Message from bus no. " + str(bus_num1[0][0]) +"   "+ str(
                                                        rec1[1]),
                                                    "avatar": "https://s3.eu-central-1.amazonaws.com/notifications-images/mobile-notifications-icons/notification_icon_check_in_drop.png"
                                                })

                            notifications.sort(key=get_year, reverse=True)

                            result = {"notifications": notifications}
                            return Response(result)
                        # notifications = []
                        # result = {"notifications": notifications}
                        # return Response(result)
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
                            cursor.execute("select  display_name_search,year_id,user_id from student_student WHERE id = %s",
                                           [student_id])
                            columns = (x.name for x in cursor.description)
                            student_name = cursor.fetchall()
                            cursor.execute(
                                " select branch_id from res_users where id=%s",
                                [student_name[0][2]])
                            branch_id = cursor.fetchall()

                            cursor.execute(
                                "select  id,date,state from pickup_request WHERE name = %s AND parent_id = %s ORDER BY ID DESC LIMIT 1",
                                [student_name[0][0], parent_id])
                            columns = (x.name for x in cursor.description)
                            date_t = cursor.fetchall()
                            if date_t:
                                if not (date_t[0][1].strftime('%Y-%m-%d') == datetime.datetime.now().strftime(
                                        '%Y-%m-%d')):
                                    date_string = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                    r = datetime.datetime.strptime(date_string, '%Y-%m-%d %H:%M:%S')
                                    cursor.execute(
                                        "INSERT INTO  pickup_request (date,name,pick_up_by,source,state,parent_id,write_date,year_id,branch_id,create_date) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s); ",
                                        [r, student_name[0][0], 'family_member', 'app', 'draft', parent_id, r, student_name[0][1] ,branch_id[0][0],r])
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
                                    [r, student_name[0][0], 'family_member', 'app', 'draft', parent_id, r,student_name[0][1],branch_id[0][0],r])
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
                            date_absent=when
                            when = datetime.datetime.strptime(when+' 00:00:00', '%d/%m/%Y %H:%M:%S')
                            target_rounds=request.data.get('target_rounds')
                            # round_id=request.data.get('status')
                            with connections[school_name].cursor() as cursor:
                                type="absent-all" if target_rounds=='both' else "absent"
                                cursor.execute("select  display_name_search from student_student WHERE id = %s",
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
                                r_id=[]
                                for rec in round_schedule_id:
                                    r_id.append(rec[0])
                                if r_id:

                                    cursor.execute(
                                        "select id,round_id from round_schedule WHERE id in %s and day_id =%s",
                                        [tuple(r_id), day_id[0][0]])
                                    rounds_details = cursor.fetchall()

                                    if target_rounds =='both':
                                        for res in rounds_details:

                                            cursor.execute(
                                                "INSERT INTO student_history(lat,long, student_id, round_id,datetime,activity_type,notification_id)VALUES (%s,%s,%s,%s,%s,%s,%s);",
                                                [lat, long, student_id, res[1], when,"absent-all",notification_id[0][0]])
                                            cursor.execute(
                                                "INSERT INTO round_student_history(student_id,round_id,datetime)VALUES (%s,%s,%s);",
                                                [student_id, res[1], when])

                                            cursor.execute(
                                                "UPDATE   transport_participant SET transport_state=%s  WHERE student_id = %s and round_schedule_id = %s",
                                                ['absent-all',student_id,res[0]])
                                    else:
                                        round_id=[]
                                        for rec in rounds_details:
                                            round_id.append(rec[1])

                                        cursor.execute(
                                            "select id from transport_round WHERE id in %s and  type=%s",
                                            [tuple(round_id), 'pick_up'])
                                        rounds_details = cursor.fetchall()

                                        for res in rounds_details:


                                            cursor.execute(
                                                "INSERT INTO student_history(lat,long, student_id, round_id,datetime,activity_type,notification_id)VALUES (%s,%s,%s,%s,%s,%s,%s);",
                                                [lat, long, student_id, res[0], when,
                                                 'absent', notification_id[0][0]])
                                            cursor.execute(
                                                "INSERT INTO round_student_history( student_id, round_id,datetime)VALUES (%s,%s,%s);",
                                                [student_id, res[0],when])
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
                                if type =='drop-off':

                                    cursor.execute("UPDATE   student_student SET drop_off_lat=%s ,drop_off_lng=%s WHERE id = %s",
                                                   [lat,long,student_id])
                                    result = {'result': "ok"}

                                    return Response(result)
                                elif type == 'pick-up':

                                    cursor.execute(
                                        "UPDATE   student_student SET pick_up_lat=%s ,pick_up_lng=%s WHERE id = %s",
                                        [lat, long, student_id])
                                    result = {'result': "ok"}
                                    return Response(result)
                                elif type =='both':
                                    cursor.execute(
                                        "UPDATE  student_student SET pick_up_lat=%s ,pick_up_lng=%s,drop_off_lat=%s,drop_off_lng=%s WHERE id = %s",
                                        [lat, long,lat, long, student_id])
                                    result = {'result': "ok"}
                                    return Response(result)
                        elif name == 'confirmed_pick':

                            with connections[school_name].cursor() as cursor:
                                parent_id = ManagerParent.objects.filter(token=au).values_list('parent_id')
                                for e in parent_id:
                                    parent_id = e[0]
                                cursor.execute("select  display_name_search from student_student WHERE id = %s",
                                               [student_id])
                                columns = (x.name for x in cursor.description)
                                student_name = cursor.fetchall()
                                cursor.execute(
                                    "select  id,date,state from pickup_request WHERE name = %s AND parent_id = %s ORDER BY ID DESC LIMIT 1",
                                    [student_name[0][0], parent_id])
                                columns = (x.name for x in cursor.description)
                                date_t = cursor.fetchall()
                                if date_t:
                                            cursor.execute(
                                                "UPDATE public.pickup_request SET picked_up_par=%s WHERE id=%s",
                                                ['confirmed', date_t[0][0]])
                                            result = {'result': True}
                                            return Response(result)

                        #         driver_id = Manager.objects.filter(token=au).values_list('driver_id')
                        #         for e in driver_id:
                        #             driver_id = e[0]
                        #         date_string = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        #         r = datetime.datetime.strptime(date_string, '%Y-%m-%d %H:%M:%S')
                        #         cursor.execute(
                        #             "select  bus_num  from fleet_vehicle WHERE driver_id = %s  ",
                        #             [driver_id])
                        #         bus_num = cursor.fetchall()
                        #         cursor.execute(
                        #             "select  name  from res_partner WHERE id = %s  ",
                        #             [driver_id])
                        #         driver_id = cursor.fetchall()
                        #
                        #
                        #         message_en="The battery of the tracking device in the bus "+bus_num+" is running out of charge"
                        #         cursor.execute(
                        #                 "INSERT INTO sh_message_wizard(create_date,from_type, type, message_en,sender_name)VALUES (%s,%s,%s,%s,%s);",
                        #                 [r, 'App\Model\Driver', 'battery_low', message_en, driver_id[0][0]])
                        # elif name == 'network':
                        #     with connections[school_name].cursor() as cursor:
                        #         driver_id = Manager.objects.filter(token=au).values_list('driver_id')
                        #         for e in driver_id:
                        #             driver_id = e[0]
                        #         date_string = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        #         r = datetime.datetime.strptime(date_string, '%Y-%m-%d %H:%M:%S')
                        #         cursor.execute(
                        #             "select  bus_num  from fleet_vehicle WHERE driver_id = %s  ",
                        #             [driver_id])
                        #         bus_num = cursor.fetchall()
                        #         cursor.execute(
                        #             "select  name  from res_partner WHERE id = %s  ",
                        #             [driver_id])
                        #         driver_id = cursor.fetchall()
                        #
                        #         message_en = "The battery of the tracking device in the bus " + bus_num + " is running out of charge"
                        #         cursor.execute(
                        #             "INSERT INTO sh_message_wizard(create_date,from_type, type, message_en,sender_name)VALUES (%s,%s,%s,%s,%s);",
                        #             [r, 'App\Model\Driver', 'network', message_en, driver_id[0][0]])
                        # elif name == 'user_no_move_time_exceeded':
                        #         with connections[school_name].cursor() as cursor:
                        #             driver_id = Manager.objects.filter(token=au).values_list('driver_id')
                        #             for e in driver_id:
                        #                 driver_id = e[0]
                        #             date_string = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        #             r = datetime.datetime.strptime(date_string, '%Y-%m-%d %H:%M:%S')
                        #             cursor.execute(
                        #                 "select  name  from res_partner WHERE id = %s  ",
                        #                 [driver_id])
                        #             driver_id = cursor.fetchall()
                        #
                        #             message_en = "	The driver "+driver_id[0][0]+" has stopped in . The allowed time is 1 minute(s)"
                        #             cursor.execute(
                        #                 "INSERT INTO sh_message_wizard(create_date,from_type, type, message_en,sender_name)VALUES (%s,%s,%s,%s,%s);",
                        #                 [r, 'App\Model\Driver', 'network', message_en, driver_id[0][0]])
                        #         # user_no_move_time_exceeded
                        #
                        #



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
                        academic_year_ids=[]
                        data=[]
                        for rec in academic_year:
                            academic_year_ids.append(rec[0])
                        cursor.execute(
                            "select  school_badge_id,teacher_id,subject_id,date,new_badge,id  from badge_badge WHERE student_id = %s AND year_id in %s  ORDER BY ID DESC",
                            [student_id, tuple(academic_year_ids)])
                        badges = cursor.fetchall()

                        for b in badges:
                            cursor.execute(
                                "select  name,description,image_url  from school_badge WHERE id = %s ",
                                [b[0]])
                            school_badge = cursor.fetchall()

                            cursor.execute(
                                "select  name  from hr_employee WHERE id = %s ",
                                [b[1]])
                            teacher_name = cursor.fetchall()
                            subject_name=''
                            delta=''
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
                                d1 = date(datetime.datetime.now().year, datetime.datetime.now().month, datetime.datetime.now().day)
                                delta = d1 - d0

                            data.append({'name': school_badge[0][0],
                                         'date':b[3].strftime("%d %b %Y"),
                                         'image':'https://trackware-schools.s3.eu-central-1.amazonaws.com/' + str( school_badge[0][2]) if  school_badge[0][2] else"",
                                         'id': b[5],
                                         'teacher':teacher_name[0][0],
                                         'subject': subject_name[0][0] if subject_name else '',
                                         'description': school_badge[0][1],
                                         'new_badge': b[4],
                                         'disable': delta.days<badge_duration[0][0] if delta else True
                                         })

                    result = {'result': data}



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

                        data=[]
                        for f_data in calendar_event_id:

                            cursor.execute(
                                " select id,name,start_datetime from calendar_event where id = %s ",
                                [f_data[0]])
                            event = cursor.fetchall()

                            if event[0][2]==None:

                                data.append({'id': event[0][0],
                                             'name': event[0][1],
                                             'start_date': event[0][2].strftime(
                                                 "%Y") if event[0][2] else '',
                                             'year': event[0][2].strftime("%Y") if event[0][2] else ''
                                             })
                            else:

                                data.append({'id': event[0][0],
                                             'name':event[0][1],
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
                        academic_year_ids=[]
                        data=[]
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
                                    " select id,name,date,note,temperature,blood_pressure,prescription from school_clinic where patient_id=%s and year_id = %s ORDER BY ID DESC",
                                    [partner_id_q[0][0],user_id_q[0][1]])
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
                                                 'prescription': v[6]if v[6] else "" })
                                except:
                                    date_s = v[2]
                                    data.append({'visit_id': v[0],
                                                 'name': v[1],
                                                 'date': date_s,
                                                 'time': date_s,
                                                 'note': v[3],
                                                 'temperature': v[4],
                                                 'blood_pressure': v[5],
                                                 'prescription':  v[6]if v[6] else ""})
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
                        absence_request=[]
                        daily_attendance=[]
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
                                [student_id,user_id_q[0][1],branch_id[0][0]])
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
                                                 'reason': 'Death of A Relative' if s[3] == 'death' else s[3],
                                                 'type': s[4],
                                                 'arrival_time': s[5] if s[5] else "0"
                                                 })
                                else:
                                    daily_attendance.append({'leave_id':  s[1],
                                                 'name':user_id_q[0][0],
                                                 'start_date': None,
                                                 'end_date': '30 Sep 2021',
                                                 'reason': 'Death of A Relative' if s[3] == 'death' else s[3],
                                                 'type': s[4],
                                                 'arrival_time': s[5] if s[5] else "0"
                                                 })
                            for st in studentleaves:

                                arrival_time = calculate_time(st[7])

                                absence_request.append({'leave_id': st[0],
                                             'name': st[1],
                                             'start_date': st[2].strftime("%d %b %Y"),
                                             'end_date': st[3],
                                             'reason': 'Death of A Relative' if st[4] == 'death' else (
                                                 st[4].capitalize() if st[4] else ""),
                                             'type': st[5].capitalize() if st[5] else "",
                                             'status': st[6].capitalize() if st[6] else "",
                                             'arrival_time': arrival_time })

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

                        # checksum = request.data.get('checksum')
                        # file_size = request.data.get('file_size')
                        Session = request.data.get('session')
                        student_id = request.data.get('student_id')
                        start_date = request.data.get('start_date')
                        end_date = request.data.get('end_date')
                        type = request.data.get('type')
                        notes = request.data.get('notes')
                        departure_time = request.data.get('departure_time')
                        reason= request.data.get('reason')
                        arrival_time = request.data.get('arrival_time')
                        base_url = request.data.get('base_url')
                        with connections[school_name].cursor() as cursor:

                            attached_files = request.data.get("file")
                            body = json.dumps({"jsonrpc": "2.0",
                                               "params": {"student_id": int(student_id), "attachments": attached_files,
                                                          "arrival_time": arrival_time, "departure_time": departure_time, "type": type,
                                                          "start_date":start_date,"end_date":end_date,"reason":reason,"notes":notes

                                                          }})
                            headers = {
                                'X-Openerp-Session-Id': Session,
                                'Content-Type': 'application/json',
                            }
                            url = base_url + "check_user_type1"
                            response1 = requests.request("POST", url,
                                                         headers=headers, data=body)


                            result = {'result':'ok'}
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
                                               "params": {"student_id": int(user_id_q[0][0]), "attachments": attached_files,
                                                          "wk_id": wk_id,

                                                          }})
                            headers = {
                                'X-Openerp-Session-Id': Session,
                                'Content-Type': 'application/json',
                            }

                            url = str(base_url) + "upload_worksheet"

                            response1 = requests.request("POST", url,
                                                         headers=headers, data=body)


                            result = {'result':'ok'}
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
                        base_url=request.data.get('base_url')
                        with connections[school_name].cursor() as cursor:
                            cursor.execute(
                                "select user_id from student_student where id=%s",
                                [student_id])
                            user_id_q = cursor.fetchall()

                            attached_files = request.data.get("file")
                            body = json.dumps({"jsonrpc": "2.0",
                                               "params": {"stu_id": int(student_id), "attachments": attached_files,"user_id":int(student_id),
                                                          "wk_id": wk_id,

                                                          }})

                            headers = {
                                'X-Openerp-Session-Id': Session,
                                'Content-Type': 'application/json',
                            }
                            # url ="http://192.168.1.150:9098/upload_events_flutter"
                            url = str(base_url) + "upload_events_flutter"
                            response1 = requests.request("POST", url,
                                                         headers=headers, data=body)



                            result = {'result':'ok'}
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
                            result = {'result':'ok'}
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

                                data = []
                                state = 'new'
                                start = False
                                cursor.execute(
                                    " select id,survey_id,token,last_displayed_page_id,state from survey_user_input where partner_id=%s and year_id = %s and branch_id =%s   ORDER BY create_date DESC, state DESC",
                                    [partner_id_q[0][0], user_id_q[0][1], partner_id_q[0][1]])
                                assignments = cursor.fetchall()


                            for assingment in assignments:
                                cursor.execute(
                                    " select id,state,deadline,title,access_token,subject_id,allowed_time_to_start,time_limit,mark,exam_names from survey_survey where id=%s and certificate=%s",
                                    [assingment[1], True])
                                survey = cursor.fetchall()


                                if  survey:

                                    cursor.execute(
                                        "select  name  from school_subject WHERE id = %s ",
                                        [survey[0][5]])
                                    subject_name = cursor.fetchall()

                                    cursor.execute(
                                        "SELECT * FROM allowed_enter_exam_student_survey_rel WHERE survey_survey_id = %s and student_student_id = %s  ",
                                        [survey[0][0],student_id])
                                    allowed_enter_exam_student_survey_rel = cursor.fetchall()
                                    allowed_to_enter_exam_after_time_limit=True if allowed_enter_exam_student_survey_rel else False

                                    cursor.execute(
                                        " select id  from survey_question where survey_id=%s",
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
                                                if  assingment[4] == 'done':
                                                    state = 'done'
                                                    start = False
                                                else:
                                                    state =  assingment[4]
                                                    start = True
                                        else:
                                            start_time = ""
                                            state =  assingment[4]
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
                                            allowed_time_to_start_exam = pd.to_datetime(allowed_time_to_start, format='%M')
                                            exam_start_sss = start_time2 + timedelta( minutes=allowed_time_to_start_exam.minute)

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
                                            "name": survey[0][3],
                                            "subject": subject_name[0][0],
                                            "token": survey[0][4],
                                            'answer_token': assingment[2],
                                            'questions_count': len(survey_question),
                                            "state": state,
                                            'last_displayed_page': "None",
                                            'answered_questions': len(survey_user_input_line),
                                            "ass_state": survey[0][1],
                                            "start": start,
                                            'start_time': start_time if start_time else 'None',
                                            'allowed_time_to_start_exams': allowed_time_to_start_exams if allowed_time_to_start_exams else  'None',
                                            'allowed_enter_exam_student_ids': allowed_to_enter_exam_after_time_limit[0][0] if allowed_to_enter_exam_after_time_limit else "None" ,
                                            "exam_name_english": exam_name[0][0] if exam_name else 'None',
                                            "exam_name_arabic": exam_name[0][1]if exam_name else 'None',
                                            'mark': int(survey[0][8]),
                                            'time_limit': survey[0][7]if survey[0][7] else 0 ,
                                            'allowed_time_to_start': survey[0][6] if survey[0][6] else 0,
                                            'late_to_exams': late_to_exams if late_to_exams else "None",
                                            'late_time': late_time if late_time else "None",
                                            'exam_start_in': exam_start_in if exam_start_in else "None",
                                            'allowed_to_enter_exam_after_time_limit': True if allowed_to_enter_exam_after_time_limit else True
                                        })

                        result = {'result': data}

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
                                    [partner_id_q[0][0], user_id_q[0][1],partner_id_q[0][1]])
                                assignments = cursor.fetchall()


                            for assingment in assignments:
                                cursor.execute(
                                    " select id,state,deadline,title,access_token,subject_id from survey_survey where id=%s and is_assignment=%s",
                                    [assingment[1],True])
                                survey = cursor.fetchall()

                                if  survey:

                                    cursor.execute(
                                        "select  name  from school_subject WHERE id = %s ",
                                        [survey[0][5]])
                                    subject_name = cursor.fetchall()
                                    cursor.execute(
                                        " select id  from survey_question where survey_id=%s",
                                        [assingment[1]])
                                    survey_question = cursor.fetchall()
                                    cursor.execute(
                                        " select id  from survey_user_input_line where survey_id=%s",
                                        [assingment[1]])
                                    survey_user_input_line = cursor.fetchall()
                                    if survey[0][1]== 'open':
                                        if survey[0][2]:
                                            deadline = survey[0][2]
                                            # cursor.execute(
                                            #     """select timezone from transport_setting ORDER BY ID DESC LIMIT 1""")
                                            # transport_setting = cursor.fetchall()
                                            # date_tz = transport_setting[0][0]
                                            date_tz = 'Asia/Kuwait'
                                            deadline.replace(date_tz)
                                            deadline =  deadline.replace(date_tz)
                                            deadline = datetime.strptime(deadline, "%d/%m/%Y %H:%M:%S")
                                            x=datetime.datetime.now().replace(date_tz)
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
                                        data.append({
                                            "id": assingment[0],
                                            "assignment_id": assingment[1],
                                            "name": survey[0][3],
                                            "subject": subject_name[0][0],
                                            "token": survey[0][4],
                                            'answer_token': assingment[2],
                                            'questions_count': len(survey_question),
                                            "state": state,
                                            'last_displayed_page': assingment[3],
                                            'answered_questions': len(survey_user_input_line),
                                            "ass_state": survey[0][1],
                                            "deadline": deadline,
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
                                    [ user_id_q[0][1],partner_id_q[0][1]])
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
def get_weekly_plan_lines(request, plan_id, student_id,week_name):
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
                             

                                # cursor.execute(
                                #     "select enable_saturday,enable_sunday,enable_monday,enable_tuesday,enable_wednesday,enable_thursday,enable_friday,subject_id,notes,description_saturday,"
                                #     "description_sunday,description_monday,description_tuesday,description_wednesday,description_thursday,description_friday,id from week_plan_lines where week_id=%s and state ='approved' and class_id =%s",
                                #     [plan_id,class_id[0][0]])
                                # lines = cursor.fetchall()
                                cursor.execute(
                                    "select enable_saturday,enable_sunday,enable_monday,enable_tuesday,enable_wednesday,enable_thursday,enable_friday,subject_id,notes,description_saturday,"
                                    "description_sunday,description_monday,description_tuesday,description_wednesday,description_thursday,description_friday,id from week_plan_lines where week_id=%s and class_id=%s and state ='approved'",
                                    [plan_id,class_id[0][0]])
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
                                dayss=[]

                                for col in columns:
                                    dayss.append({
                                        "id":col[0],
                                        "day": col[1]
                                    })
                                data['columns'] = dayss

                                subject_lines = []
                                for l in lines:
                                    cursor.execute(
                                        "select  name  from school_subject WHERE id = %s ",
                                        [l[7]])
                                    subject_name = cursor.fetchall()
                                    line = {'subject_id': l[7], 'subject_name': subject_name[0][0], 'notes': l[8] if l[8] else '',
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

                                                line['attachments'].append({'id': att[0], 'name': att[1], 'datas': att[2]})
                                            # else:
                                                # line['attachments'].append({'id': 1, 'name': '', 'datas': ''})
                                    # else:
                                        # line['attachments'].append({'id': 1, 'name': '', 'datas': ''})
                                data['lines'] = subject_lines

                                notes = ''
                                # for note in week.week_note_ids:
                                #     if cls.id in note.class_ids.ids:
                                #         notes += note.note + ','
                                # if notes:
                                #     notes = notes[:-1] + '.'
                                data['notes'] = notes
                        result = {'result': data}
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
                                    worksheet_id=[]
                                    for rec in class_worksheet_id:
                                        if rec[0]:
                                            worksheet_id.append(rec[0])
                                    if worksheet_id:
                                        cursor.execute(
                                            " select id,name,priority,create_date,subject_id,deadline from class_worksheet where state='published' and year_id = %s and branch_id =%s and id in %s  ORDER BY create_date DESC",
                                            [user_id_q[0][1], partner_id_q[0][1],tuple(worksheet_id)])
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
                                                             'date': str(date.strftime("%d %b %Y")),
                                                             'priority': w[2],
                                                             'deadline': str(deadline.strftime("%d %b %Y") +' '+ str(deadline.hour)+':'+str(deadline.minute)+':'+str(deadline.second)) if deadline else '',
                                                             'subject': subject_name[0][0],
                                                             'finish':str(deadline <datetime.datetime.now().astimezone(new_timezone)) if deadline else ''
                                                             })
                                    result = {'result': data}

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
                                            [ student_id])
                                        events = cursor.fetchall()

                                        for ev in events:
                                            cursor.execute(
                                                " select name,state,start_date from school_event where id=%s and  year_id = %s",
                                                [ev[1],user_id_q[0][1]])
                                            school_event = cursor.fetchall()
                                            # school.event
                                            if school_event:
                                                data.append({'event_id': ev[0],
                                                             'name': school_event[0][0],
                                                             'start_date': school_event[0][2].strftime("%d %b %Y"),
                                                             'state': school_event[0][1],
                                                             'participant_state': ev[2],
                                                             'new_added':str(ev[3]) if ev[3] else ''
                                                             })
                                result = {'result': data}

                                return Response(result)
    result = {'result': ''}
    return Response(result)


    # search_filters = self.search(std_dom).portal_filterable_serchable()

    # return {'data': data, 'search_filters': search_filters}

@api_view(['GET'])
def get_worksheet_form_view_data(request, wsheet,std):
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
                                            date_time_obj = datetime.datetime.strptime(str(date_time_str), '%Y-%m-%d %H:%M:%S').astimezone(new_timezone)
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
                                            import urllib.request
                                            import math
                                            # importing the module
                                            file = urllib.request.urlopen(worksheet[0][6])
                                            size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
                                            i = int(math.floor(math.log(file.length, 1024)))
                                            p = math.pow(1024, i)
                                            s = round(file.length / p, 2)
                                        cursor.execute(
                                            "select id from student_student where id=%s",
                                            [std])
                                        user_id_q = cursor.fetchall()
                                        student_solution=[]
                                        if user_id_q:
                                            cursor.execute(
                                                "select id from student_details where worksheet_id=%s and student_id=%s",
                                                [worksheet[0][0],std])
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
                                                            'name':str(res[0]),
                                                            'file_size':str(res[1])
                                                        })

                                        data.append({'worksheet_id':worksheet[0][0],
                                                     'name': worksheet[0][1],
                                                     'date': str(worksheet[0][3]),
                                                     'teacher_name':hr_employee[0][1],
                                                     'link': worksheet[0][6] if worksheet[0][6] else '',
                                                     'teacher_id':hr_employee[0][0],
                                                     'teacher_image':  hr_employee[0][2]if hr_employee[0][2] else "https://s3.eu-central-1.amazonaws.com/trackware.schools/public_images/default_student.png" ,
                                                     'teacher_position': job_name[0][0] if job_name else 'Teacher',
                                                     'subject': subject_name[0][0],
                                                     'homework':  "%s %s" % (s, size_name[i]) if worksheet[0][7] else '',
                                                     'homework_name':  worksheet[0][8],
                                                     'description':  worksheet[0][9],
                                                     'deadline':  str(date_time_obj) if worksheet[0][5] else "",
                                                     'end':str(datetime.datetime.now()>=worksheet[0][5]) if worksheet[0][5] else "",
                                                     'student_solution':student_solution
                                                     })
                                    result = {'result': data}
                                    return Response(result)
                        result = {'result': data}
                        return Response(result)
def remove_html(string):
    import re
    regex = re.compile(r'<[^>]+>')
    return regex.sub('', string)
@api_view(['GET'])
def get_event_form_view_data(request, event,std):
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
                                        " select id,event_id,state from school_event_registration where  id =%s   ORDER BY create_date DESC",
                                        [event])
                                    events = cursor.fetchall()

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
                                    contact_id=''

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
                                    available_seats= school_event[0][3] - len(participants)
                                    cursor.execute(
                                        "select user_id from student_student where id=%s",
                                        [std])
                                    user_id_q = cursor.fetchall()
                                    student_solution = []
                                    if user_id_q:
                                                import math
                                                cursor.execute(
                                                    "SELECT name,file_size  FROM public.ir_attachment where res_model='school.event' and res_id =%s and student_idq =%s",
                                                    [events[0][1],std])
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
                                    contact_name=''
                                    supervisor_name=''
                                    supervisor_image='https://s3.eu-central-1.amazonaws.com/trackware.schools/public_images/default_student.png'
                                    contact_image='https://s3.eu-central-1.amazonaws.com/trackware.schools/public_images/default_student.png'
                                    contact_id_id=0
                                    supervisor_id_id=0

                                    if contact_id :
                                        contact_name = contact_id[0][1] if contact_id[0][1] else ""
                                        contact_image =contact_id[0][2]if contact_id[0][2] else "https://s3.eu-central-1.amazonaws.com/trackware.schools/public_images/default_student.png"
                                        contact_id_id  =contact_id[0][0]if contact_id[0][0] else 0

                                    if supervisor_id:
                                        supervisor_name = supervisor_id[0][1] if supervisor_id[0][1] else ""
                                        supervisor_image   = supervisor_id[0][2] if supervisor_id[0][2] else "https://s3.eu-central-1.amazonaws.com/trackware.schools/public_images/default_student.png"
                                        supervisor_id_id = supervisor_id[0][0] if supervisor_id[0][0] else 0

                                    data.append({'event_id': events[0][0],
                                                 'name': school_event[0][0],
                                                 'start_date': str(school_event[0][11].strftime("%d %b %Y")),
                                                 'end_date': str(school_event[0][12].strftime("%d %b %Y")),
                                                 'registration_start_date': str(school_event[0][13]) if school_event[0][13] else '' ,
                                                 'registration_last_date': str(school_event[0][14])if school_event[0][14] else '',
                                                 'maximum_participants':school_event[0][3],
                                                 'available_seats':available_seats ,
                                                 'cost': str(school_event[0][5]) + ' ' + str(res_currency[0][0]),
                                                 'contact_name':contact_name,
                                                 'contact_id':contact_id_id,
                                                 'contact_image':contact_image,
                                                 'supervisor_name':supervisor_name,
                                                 'event': str(school_event[0][6])if school_event[0][6] else '',
                                                 'event_name': str(school_event[0][7]) if school_event[0][7] else '',
                                                 'link': str(school_event[0][8]) if school_event[0][8] else '',
                                                 'supervisor_id': supervisor_id_id,
                                                 'supervisor_image': supervisor_image,
                                                 'state':events[0][2] ,
                                                 'flag': str(True) if events[0][2] == 'draft' else str(False),
                                                 'period': str(school_event[0][12] - school_event[0][11]),
                                                 'student_solution':student_solution})


                                    result = {'result': data}

                                    return Response(result)






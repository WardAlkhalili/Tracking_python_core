from django.shortcuts import render

# Create your views here.
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
import json
import calendar
from datetime import date
import requests
import datetime
from rest_framework import status


@api_view(['POST'])
def parent_login(request):
    if request.method == 'POST':
        password = request.data.get('password')
        user_name = request.data.get('user_name')
        school_name = request.data.get('school_name')
        mobile_token = request.data.get('mobile_token')
        # print("jjjjjjjjjjjjjjjjjjjjjjjjjjjj ",mobile_token)

        # url = "http://localhost:9098/web/session/authenticate"
        url = 'https://' + school_name + '.staging.trackware.com/web/session/authenticate'
        # url = 'http://127.0.0.1:9098/web/session/authenticate'
        body = json.dumps({"jsonrpc": "2.0", "params": {"db": school_name, "login": user_name, "password": password}})
        headers = {
            'Content-Type': 'application/json',
        }
        response1 = requests.request("POST", url, headers=headers, data=body)
        response = response1.json()
        session = response1.cookies
        uid = response['result']['uid']
        company_id = response['result']['company_id']
        with connections[school_name].cursor() as cursor:
            cursor.execute("select id from school_parent WHERE user_id = %s", [response['result']['uid']])
            columns2 = (x.name for x in cursor.description)
            parent_id = cursor.fetchall()
            user = User.objects.all().first()
            user = User.objects.all().first()
            # print(user)
            token_auth, created = Token.objects.get_or_create(user=user)
            from django.utils.crypto import get_random_string
            unique_id = get_random_string(length=32)
            # print(unique_id)
            ManagerParent.objects.filter(parent_id=parent_id[0][0], db_name=school_name, user_id=uid).update(
                is_active=False)
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
                        notifications = request.data.get('notifications')
                        # school_name = ManagerParent.pincode('iks')
                        with connections[school_name].cursor() as cursor:
                            y = json.dumps(notifications)
                            settings = "{\"notifications\":" + y + "}"
                            cursor.execute(
                                "UPDATE public.school_parent SET settings=%s WHERE id=%s;",
                                [settings, parent_id])
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
                                return Response(data)
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
                    # print(au)
                    l.append(au.split(","))

                    db_name = ManagerParent.objects.filter(token=au.split(",")[0]).values_list('db_name')
                    parent_id = ManagerParent.objects.filter(token=au.split(",")[0]).values_list('parent_id')
                    school_id = ManagerParent.objects.filter(token=au.split(",")[0]).values_list('school_id')
                    # print(parent_id)
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
                                        "select round_schedule_id from transport_participant WHERE round_schedule_id = %s and student_id = %s",
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
                                    "Badges": {
                                        "url": "https://" + school_name + ".staging.trackware.com/my/Badges/",
                                        "arabic_url": "https://" + school_name + ".staging.trackware.com/ar_SY/my/Badges/",
                                        "name": "Badges",
                                        "name_ar": "الشارات",
                                        "icon": "https://trackware-schools.s3.eu-central-1.amazonaws.com/Badge.png"
                                    },
                                    "Weeklyplans":
                                        {
                                            "url": "https://" + school_name + ".staging.trackware.com/my/Weekly-plans/",
                                            "arabic_url": "https://" + school_name + ".staging.trackware.com/ar_SY/my/Weekly-plans/",
                                            "name": "Weeklyplans",
                                            "name_ar": "الخطط الأسبوعية",
                                            "icon": "https://trackware-schools.s3.eu-central-1.amazonaws.com/Weekly+Plans.png"
                                        },
                                    "Assignments": {
                                        "url": "https://" + school_name + ".staging.trackware.com/my/Assignments/",
                                        "arabic_url": "https://" + school_name + ".staging.trackware.com/ar_SY/my/Assignments/",
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
                                         "name_ar": "Events",
                                         "url": "https://" + school_name + ".staging.trackware.com/my/Events/",
                                         "arabic_url": "https://" + school_name + ".staging.trackware.com/ar_SY/my/Events/",
                                         "arabic_name": "الفعاليات و الانشطة",
                                         "icon": "https://trackware-schools.s3.eu-central-1.amazonaws.com/Events.png"
                                         },
                                    "Homeworks":
                                        {"name": "Homeworks",
                                         "url": "https://" + school_name + ".staging.trackware.com/my/Homeworks/",
                                         "arabic_url": "https://" + school_name + ".staging.trackware.com/ar_SY/my/Homeworks/",
                                         "name_ar": "الواجبات المنزلية",
                                         "icon": "https://trackware-schools.s3.eu-central-1.amazonaws.com/worksheets.png"
                                         },
                                    "Calendar":
                                        {"name": "Calendar",
                                         "url": "https://" + school_name + ".staging.trackware.com/my/Calendar/",
                                         "arabic_url": "https://" + school_name + ".staging.trackware.com/ar_SY/my/Calendar/",
                                         "name_ar": "التقويم",
                                         "icon": "https://trackware-schools.s3.eu-central-1.amazonaws.com/School+Calendar.png"
                                         },

                                    "Clinic":
                                        {"name": "Clinic",
                                         "name_ar": "Clinic",
                                         "url": "https://" + school_name + ".staging.trackware.com/my/Clinic/",
                                         "arabic_url": "https://" + school_name + ".staging.trackware.com/ar_SY/my/Clinic/",
                                         "arabic_name": "العيادة",
                                         "icon": "https://trackware-schools.s3.eu-central-1.amazonaws.com/Clinic.png"
                                         }
                                }
                                url_m = {}
                                model_list = (
                                    "Badges", "Clinic", "Calendar", "Homework", "Events", "Online Assignments",
                                    "Weekly Plans")
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
                                        "url": "https://" + school_name + ".staging.trackware.com/my/Absence/" + str(
                                            student1[rec]['user_id']),
                                        "arabic_url": "https://" + school_name + ".staging.trackware.com/ar_SY/my/Absence/" + str(
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
                                                "url": "https://" + school_name + ".staging.trackware.com/my/Absence/" + str(
                                                    student1[rec]['user_id']),
                                                "arabic_url": "https://" + school_name + ".staging.trackware.com/ar_SY/my/Absence/" + str(
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

                                studen_list.append({
                                    'id': student1[rec]['id'],
                                    'user_id': student1[rec]['user_id'],
                                    'father_id': student1[rec]['father_id'],
                                    'mother_id': student1[rec]['mother_id'],
                                    'student_grade': student1[rec]['academic_grade_name1'],
                                    "change_location": setting[0][3],
                                    'name': student1[rec]['display_name_search'],
                                    'grade_name': '',
                                    'drop_off_by_parent': drop,
                                    'pickup_by_parent': pick,
                                    "is_active": is_active_round,
                                    "round_id": student_round_id,
                                    'avatar': 'https://trackware-schools.s3.eu-central-1.amazonaws.com/' + str(
                                        student1[rec]['image_url']) if student1[rec][
                                        'image_url'] else str(
                                        'https://s3.eu-central-1.amazonaws.com/trackware.schools/public_images/default_student.png'),
                                    "school_name": school[0][0],
                                    "school_mobile_number": school[0][1],
                                    "school_lat": setting[0][0],
                                    "school_lng": setting[0][1],
                                    'pickup_request_distance': setting[0][2],
                                    "show_map": setting[0][4],
                                    "show_absence": show_absence,
                                    'pickup_request_distance':setting[0][5],
                                    "show_pickup_request": True if student1[rec]['pick_up_type']=='by_school' else False,
                                    "student_status": {
                                        "activity_type": "",
                                        "round_id": 0,
                                        "datetime": ""
                                    },
                                    "mobile_numbers": [
                                        {
                                            "mobile": school[0][1],
                                            "name": school[0][0],
                                            "type": "school"
                                        },
                                        {
                                            "mobile": "",
                                            "name": "My Company (San Francisco)",
                                            "type": "school"
                                        },
                                        {
                                            "mobile": "",
                                            "name": "My Company (San Francisco)",
                                            "type": "school"
                                        }
                                    ],
                                    "features": model,
                                })
                            result = {'students': studen_list}
                            # print(result)
                            return Response(result)
                    result = {'status': 'error'}
                    return Response(result)
        result = {'status': 'error'}
        return Response(result)
    elif request.method == 'GET':
        result = {'status': 'error'}
        return Response(result)


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
                        # print(start_date,end_date)
                        with connections[school_name].cursor() as cursor:
                            if start_date and end_date:
                                cursor.execute(
                                    "select  id  from school_message WHERE create_date >= %s AND create_date <= %s",
                                    [start_date, end_date])
                                school_message = cursor.fetchall()
                                # print(school_message)
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
                            # print(student)
                            student_id = []
                            for rec in student:
                                student_id.append(rec[0])
                            cursor.execute(
                                "select  round_schedule_id from transport_participant WHERE student_id in %s",
                                [tuple(student_id)])
                            round_schedule_id = cursor.fetchall()
                            round_schedule_ids = []
                            for rec in round_schedule_id:
                                round_schedule_ids.append(rec[0])
                            if round_schedule_ids:
                                cursor.execute(
                                    "select  round_id from round_schedule WHERE id in %s",
                                    [tuple(round_schedule_ids)])
                                round_schedule = cursor.fetchall()
                                round_schedules = []
                                for rec in round_schedule:
                                    round_schedules.append(rec[0])
                                if round_schedules:
                                    cursor.execute(
                                        "select  message_ar,create_date,type from sh_message_wizard WHERE round_id in %s",
                                        [tuple(list(dict.fromkeys(round_schedules)))])
                                    sh_message_wizard = cursor.fetchall()
                                    # for rec in range(len(sh_message_wizard)):
                                    # notifications.append({
                                    #     "notifications_text": sh_message_wizard[rec][0],
                                    #     "date_time": sh_message_wizard[rec][1],
                                    #     "create_date": sh_message_wizard[rec][1],
                                    #     "notifications_title": sh_message_wizard[rec][2],
                                    #     "avatar": "https://s3.eu-central-1.amazonaws.com/notifications-images/mobile-notifications-icons/notification_icon_check_in_drop.png"
                                    # })

                            message_ids = []
                            for rec in school_message:
                                message_ids.append(rec[0])
                            # print(student_id)
                            if message_ids:
                                cursor.execute(
                                    "select  student_student_id  from school_message_student_student where school_message_id in %s",
                                    [tuple(message_ids)])
                                school_message_student_student = cursor.fetchall()
                                # print(school_message_student_student)
                                cursor.execute(
                                    "select  school_message_id from school_message_student_student WHERE school_message_id in %s AND student_student_id in %s",
                                    [tuple(message_ids), tuple(student_id)])
                                message_student = cursor.fetchall()
                                # print(message_student)
                                message_id = []
                                for rec in message_student:
                                    message_id.append(rec[0])
                                if message_id:
                                    cursor.execute(
                                        "select  id,search_type,title,message,create_date,date from school_message WHERE id in %s",
                                        [tuple(list(dict.fromkeys(message_id)))])
                                    school_message1 = cursor.fetchall()
                                    for rec in range(len(school_message1)):
                                        notifications.append({
                                            "avatar": "https://s3.eu-central-1.amazonaws.com/notifications-images/mobile-notifications-icons/notification_icon_msg_admin.png",
                                            "date_time": str(school_message1[rec][4].year) + "-" + str(
                                                school_message1[rec][4].month) + "-" + str(
                                                school_message1[rec][4].day) + " " + str(
                                                school_message1[rec][4].hour) + ":" + str(
                                                school_message1[rec][4].hour) + ":" + str(
                                                school_message1[rec][4].minute) + ":" + str(
                                                school_message1[rec][4].second),
                                            "notifications_text": school_message1[rec][3],
                                            "create_date": school_message1[rec][5],
                                            "notifications_title": school_message1[rec][2],

                                        })

                                    result = {"notifications": notifications}

                                    return Response(result)
                            notifications = []
                            # notifications.append({
                            #
                            #     "notifications_text": 'school_message1[rec][3]',
                            #     "date_time": 'school_message1[rec][5]',
                            #     "create_date": 'school_message1[rec][4]',
                            #     "notifications_title": 'school_message1[rec][2]',
                            #     "avatar": "https://s3.eu-central-1.amazonaws.com/notifications-images/mobile-notifications-icons/notification_icon_check_in_drop.png"
                            # })
                            result = {"notifications": notifications}
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
                                        "INSERT INTO  pickup_request (date,name,pick_up_by,source,state,parent_id,write_date) VALUES (%s,%s,%s,%s,%s,%s,%s); ",
                                        [r, student_name[0][0], 'family_member', 'app', 'draft', parent_id, r])
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
                                    "INSERT INTO  pickup_request (date,name,pick_up_by,source,state,parent_id,write_date) VALUES (%s,%s,%s,%s,%s,%s,%s); ",
                                    [r, student_name[0][0], 'family_member', 'app', 'draft', parent_id, r])
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
                    parent_id = ManagerParent.objects.filter(token=au).values_list('parent_id')
                    for e in parent_id:
                        parent_id = e[0]
                    if db_name:
                        for e in db_name:
                            school_name = e[0]

                        school_name = ManagerParent.pincode(school_name)
                        type = request.data.get('location_type')
                        sender_id = parent_id
                        date = request.data.get('date')
                        student_id = request.data.get('student_id')
                        name = request.data.get('name')
                        lat = request.data.get('lat')
                        long = request.data.get('long')
                        if name == 'childs_attendance':
                            when = request.data.get('when')
                            target_rounds=request.data.get('target_rounds')
                            round_id=request.data.get('status')
                            with connections[school_name].cursor() as cursor:
                                cursor.execute("select  display_name_search from student_student WHERE id = %s",
                                               [student_id])

                                student_name = cursor.fetchall()
                                cursor.execute("select  display_name_search from school_parent WHERE id = %s",
                                               [sender_id])

                                sender_name = cursor.fetchall()
                                message_en = "	My child  " + student_name[0][0] + " will be absent on " + str(
                                    date) + " .So please do not pass by my home for pickup"
                                date_string = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                r = datetime.datetime.strptime(date_string, '%Y-%m-%d %H:%M:%S')
                                cursor.execute(
                                    "INSERT INTO sh_message_wizard(create_date,from_type, type, message_en,sender_name)VALUES (%s,%s,%s,%s,%s);",
                                    [r, 'App\Model\Parents', type, message_en, sender_name[0][0]])
                                notification_id= cursor.lastrowid
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
                                cursor.execute(
                                    "select id,round_id from round_schedule WHERE id in %s and day_id =%s",
                                    [tuple(r_id), day_id[0][0]])
                                rounds_details = cursor.fetchall()
                                if target_rounds =='both':
                                    for res in rounds_details:
                                        cursor.execute(
                                            "INSERT INTO student_history(lat,long, student_id, round_id,datetime,activity_type,notification_id)VALUES (%s,%s,%s,%s,%s,%s,%s);",
                                            [lat, long, student_id, res[1], datetime.datetime.now(),'absent-all',notification_id])
                                        cursor.execute(
                                            "INSERT INTO round_student_history(student_id,round_id,datetime)VALUES (%s,%s,%s);",
                                            [student_id, res[1], datetime.datetime.now()])
                                        cursor.execute(
                                            "UPDATE   transport_participant SET transport_state=%s  WHERE student_id = %s and round_schedule_id = %s",
                                            ['absent-all',student_id,res[0]])
                                else:
                                    round_id=[]
                                    for rec in rounds_details:
                                        round_id.append(rec[1])
                                    cursor.execute(
                                        "select id from transport_round WHERE id in %s and  type=%s",
                                        [round_id, 'pick_up'])
                                    rounds_details = cursor.fetchall()

                                    for res in rounds_details:
                                        cursor.execute(
                                            "INSERT INTO student_history(lat,long, student_id, round_id,datetime,activity_type,notification_id)VALUES (%s,%s,%s,%s,%s,%s,%s);",
                                            [lat, long, student_id, res[1], datetime.datetime.now(),
                                             'absent', notification_id])
                                        cursor.execute(
                                            "INSERT INTO round_student_history( student_id, round_id,datetime)VALUES (%s,%s,%s);",
                                            [student_id, res[1], datetime.datetime.now()])
                                        cursor.execute(
                                            "UPDATE   transport_participant SET transport_state=%s  WHERE student_id = %s and round_schedule_id = %s",
                                            ['absent', student_id, res[0]])
                                result = {'result': "ok"}

                                return Response(result)
                        elif name == 'changed_location':
                            with connections[school_name].cursor() as cursor:
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
                                        "UPDATE   student_student SET pick_up_lat=%s ,pick_up_lng=%s,drop_off_lat,drop_off_lng WHERE id = %s",
                                        [lat, long,lat, long, student_id])
                                    result = {'result': "ok"}
                                    return Response(result)



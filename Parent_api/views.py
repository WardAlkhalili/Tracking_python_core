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
        # url = "http://localhost:9098/web/session/authenticate"
        url = 'http://192.168.1.127:9098/web/session/authenticate'
        # url = 'http://127.0.0.1:9098/web/session/authenticate'
        body = json.dumps( {"jsonrpc": "2.0", "params": {"db": 'iks', "login": user_name, "password": password}})
        headers = {
            'Content-Type': 'application/json',
        }
        response = requests.request("POST", url, headers=headers, data=body).json()
        response = requests.request("POST", url, headers=headers, data=body).json()
        uid = response['result']['uid']
        company_id = response['result']['company_id']
        with connections[school_name].cursor() as cursor:
            cursor.execute("select id from school_parent WHERE user_id = %s", [response['result']['uid']])
            columns2 = (x.name for x in cursor.description)
            parent_id = cursor.fetchall()
            user = User.objects.all().first()
            user = User.objects.all().first()
            token_auth, created = Token.objects.get_or_create(user=user)
            manager_parent = ManagerParent(token=token_auth, db_name=school_name, user_id=uid,
                                           parent_id=parent_id[0][0],
                                           school_id=company_id,mobile_token=mobile_token)

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
                "session_id": "f29679e7256bbda0ea318b92c0089b339c2c03a4",
                "web_base_url": response['result']['web_base_url'],
                "Authorization": "Bearer " + token_auth.key}
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
                                        "INSERT INTO  pickup_request (date,name,pick_up_by,source,state,parent_id,write_date) VALUES (%s,%s,%s,%s,%s,%s,%s); ",
                                        [r, student_name[0][0], 'family_member', 'app', 'draft', parent_id,r])
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
                                    "INSERT INTO  pickup_request (date,name,pick_up_by,source,state,parent_id,,write_date) VALUES (%s,%s,%s,%s,%s,%s,%s); ",
                                    [r, student_name[0][0], 'family_member', 'app', 'draft', parent_id,r])
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

                    au = request.headers.get('Authorization').replace('Bearer', '').strip()
                    db_name = ManagerParent.objects.filter(token=au).values_list('db_name')
                    parent_id = ManagerParent.objects.filter(token=au).values_list('parent_id')
                    school_id = ManagerParent.objects.filter(token=au).values_list('school_id')
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
                                "select  id,display_name_search,user_id,pick_up_type,drop_off_type,image_url,academic_grade_name1,father_id,mother_id from student_student WHERE father_id = %s OR mother_id = %s OR responsible_id_value = %s  And state = 'done'",
                                [parent_id, parent_id, parent_id])
                            columns = (x.name for x in cursor.description)
                            student = cursor.fetchall()
                            studen_list = []
                            cursor.execute(
                                "select  lat,lng,pickup_request_distance from transport_setting  ORDER BY ID DESC LIMIT 1")
                            columns = (x.name for x in cursor.description)
                            setting = cursor.fetchall()
                            cursor.execute(
                                "select  name,phone from res_company WHERE id = %s ",
                                [school_id])
                            columns = (x.name for x in cursor.description)
                            school = cursor.fetchall()
                            for rec in range(len(student)):
                                x = {
                                        "Badges": {
                                            "url": "http://127.0.0.1:9098/my/Badges/",
                                            "arabic_url": "http://127.0.0.1:9098/ar_SY/my/Badges/",
                                            "name": "Badges",
                                            "name_ar": "الشارات",
                                            "icon": "https://trackware-schools.s3.eu-central-1.amazonaws.com/Badge.png"
                                        },
                                        "Weeklyplans":
                                            {
                                                "url": "http://192.168.1.127:9098/my/Weekly-plans/",
                                                "arabic_url": "https://192.168.1.127:9098/ar_SY/my/Weekly-plans/",
                                                "name": "Weeklyplans",
                                                "name_ar": "الخطط الأسبوعية",
                                                "icon": "https://trackware-schools.s3.eu-central-1.amazonaws.com/Weekly+Plans.png"
                                            },
                                        "Assignments": {
                                            "url": "http://192.168.1.127:9098/my/Assignments/",
                                            "arabic_url": "http://192.168.1.127:9098/ar_SY/my/Assignments/",
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
                                             "url": "http://192.168.1.127:9098/my/Events/",
                                             "arabic_url": "http://192.168.1.127:9098/ar_SY/my/Events/",
                                             "arabic_name": "الفعاليات و الانشطة",
                                             "icon": "https://trackware-schools.s3.eu-central-1.amazonaws.com/Events.png"
                                             },
                                        "Homeworks":
                                            {"name": "Homeworks",
                                             "url": "http://192.168.1.127:9098/my/Homeworks/",
                                             "arabic_url": "http://192.168.1.127:9098/ar_SY/my/Homeworks/",
                                             "name_ar": "الواجبات المنزلية",
                                             "icon": "https://trackware-schools.s3.eu-central-1.amazonaws.com/worksheets.png"
                                             },
                                        "Calendar":
                                            {"name": "Calendar",
                                             "url": "https://iks.staging.trackware.com/my/Calendar/",
                                             "arabic_url": "https://iks.staging.trackware.com/ar_SY/my/Calendar/",
                                             "name_ar": "التقويم",
                                             "icon": "https://trackware-schools.s3.eu-central-1.amazonaws.com/School+Calendar.png"
                                             },

                                        "Clinic":
                                            {"name": "Clinic",
                                             "name_ar": "Clinic",
                                             "url": "http://192.168.1.127:9098/my/Clinic/",
                                             "arabic_url": "http://192.168.1.127:9098/ar_SY/my/Clinic/",
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

                                for rec1 in res:
                                    if 'Weekly Plans' == rec1:
                                        x['Weeklyplans']['arabic_url']=x['Weeklyplans']['arabic_url']+str(student[rec][2])
                                        x['Weeklyplans']['url'] = x['Weeklyplans']['url'] + str(
                                            student[rec][2])
                                        model.append(x['Weeklyplans'])

                                    if 'Events' == rec1:
                                        x['Events']['arabic_url'] = x['Events']['arabic_url'] + str(student[rec][2])
                                        x['Events']['url'] = x['Events']['url'] + str(student[rec][2])
                                        model.append(x['Events'])

                                    if 'Online Assignments' == rec1:
                                        x['Assignments']['arabic_url'] = x['Assignments']['arabic_url'] + str(student[rec][2])
                                        x['Assignments']['url'] = x['Assignments']['url'] + str(
                                            student[rec][2])
                                        model.append(x['Assignments'])

                                    if 'Homework' == rec1:
                                        x['Homeworks']['arabic_url'] = x['Homeworks']['arabic_url'] + str(student[rec][2])
                                        x['Homeworks']['url'] = x['Homeworks']['url'] + str(
                                            student[rec][2])
                                        model.append(x['Homeworks'])

                                    if 'Badges' == rec1:
                                        x['Badges']['arabic_url'] = x['Badges']['arabic_url'] + str(student[rec][2])
                                        x['Badges']['url'] = x['Badges']['url'] + str(student[rec][2])
                                        model.append(x['Badges'])

                                    if 'Calendar' == rec1:
                                        x['Calendar']['url'] = x['Calendar']['url'] + str(student[rec][2])
                                        x['Calendar']['arabic_url'] = x['Calendar']['arabic_url'] + str(student[rec][2])
                                        model.append(x['Calendar'])

                                    if 'Clinic' == rec1:
                                        x['Clinic']['arabic_url'] = x['Clinic']['arabic_url'] + str(student[rec][2])
                                        x['Clinic']['url'] = x['Clinic']['url'] + str(student[rec][2])
                                        model.append(x['Clinic'])


                                cursor.execute(
                                    "select name from ir_ui_menu where name ='Tracking'")
                                tracking = cursor.fetchall()

                                if len(tracking) > 0:
                                    model.append({
                                        "url": "http://192.168.1.127:9098/my/Absence/"+str(student[rec][2]),
                                        "arabic_url": "http://192.168.1.127:9098/ar_SY/my/Absence/"+str(student[rec][2]),
                                        "name": "Absence",
                                        "name_ar": "الغياب",
                                        "icon": "https://trackware-schools.s3.eu-central-1.amazonaws.com/Absence.png"
                                    }
                                    )

                                try:
                                    cursor.execute(
                                        "select is_portal_exist from school_parent")
                                    is_portal_exist = cursor.fetchall()
                                    # sql = """select is_portal_exist from school_parent '"""
                                except:
                                    model = {
                                        "Absence":
                                            {
                                                "url": "http://192.168.1.127:9098/my/Absence/"+str(student[rec][2]),
                                                "arabic_url": "http://192.168.1.127:9098/ar_SY/my/Absence/"+str(student[rec][2]),
                                                "name": "Absence",
                                                "name_ar": "الغياب",
                                                "icon": "https://trackware-schools.s3.eu-central-1.amazonaws.com/Absence.png"
                                            }

                                    }


                                if 'by_parents' in student[rec][3]:
                                    pick = True
                                else:
                                    pick = False
                                if 'by_parents' in student[rec][4]:
                                    drop = True
                                else:
                                    drop = False
                                studen_list.append({
                                    'id': student[rec][0],
                                    'user_id': student[rec][2],
                                    'father_id': student[rec][7],
                                    'mother_id': student[rec][8],
                                    'name': student[rec][1],
                                    'grade_name': student[rec][6],
                                    'drop_off_by_parent': drop,
                                    'pickup_by_parent': pick,
                                    "is_active": False,
                                    'avatar': student[rec][5] if student[rec][
                                        5] else 'https://s3.eu-central-1.amazonaws.com/trackware.schools/public_images/default_student.png',
                                    "school_name": school[0][0],
                                    "school_mobile_number": school[0][1],
                                    "school_lat": setting[0][0],
                                    "school_lng": setting[0][1],
                                    'pickup_request_distance': setting[0][2],
                                    "student_status": {
                                        "activity_type": "",
                                        "round_id": 0,
                                        "datetime": ""
                                    },
                                    "features": model,
                                })
                            result = {'students': studen_list}
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
                                "select  id,display_name_search,image_url from student_student WHERE father_id = %s OR mother_id = %s OR responsible_id_value = %s  And state = 'done'",
                                [parent_id, parent_id, parent_id])
                            student = cursor.fetchall()
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
                            if message_ids:
                                cursor.execute(
                                    "select  school_message_id from school_message_student_student WHERE school_message_id in %s AND student_student_id in %s",
                                    [tuple(message_ids), tuple(student_id)])
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
                                        notifications.append({
                                            "avatar": "https://s3.eu-central-1.amazonaws.com/notifications-images/mobile-notifications-icons/notification_icon_msg_admin.png",
                                            "date_time": "2022-03-14 18:22:28",
                                            "notifications_text": school_message1[rec][3],
                                            "date_time": school_message1[rec][5],
                                            "notifications_title": school_message1[rec][2],

                                        })

                                    result = {"notifications": notifications}
                                    return Response(result)
                            notifications = []
                            notifications.append({

                                "notifications_text": 'school_message1[rec][3]',
                                "date_time": 'school_message1[rec][5]',
                                "create_date": 'school_message1[rec][4]',
                                "notifications_title": 'school_message1[rec][2]',
                                "avatar": "https://s3.eu-central-1.amazonaws.com/notifications-images/mobile-notifications-icons/notification_icon_check_in_drop.png"
                            })
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
                                    "INSERT INTO  pickup_request (date,name,pick_up_by,source,state,parent_id,create_date,write_date) VALUES (%s,%s,%s,%s,%s,%s,%s,%s); ",
                                    [r, student_name[0][0], 'family_member', 'app', 'draft', parent_id,r,r])
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
                                    [r, student_name[0][0], 'family_member', 'app', 'draft', parent_id,r,r])
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


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
        user_name = request.data.get('login')
        school_name = request.data.get('school_name')
        url = "http://localhost:9098/web/session/authenticate"

        body = json.dumps({
            "jsonrpc": "2.0",
            "params": {
                "db": school_name,
                "login": user_name,
                "password": password
            }
        })

        headers = {
            'Content-Type': 'application/json',
        }
        response = requests.request("POST", url, headers=headers, data=body).json()
        uid = response['result']['uid']
        company_id = response['result']['company_id']

        with connections[response['result']['db']].cursor() as cursor:
            cursor.execute("select id from school_parent WHERE user_id = %s", [response['result']['uid']])
            columns2 = (x.name for x in cursor.description)
            parent_id = cursor.fetchall()

            user = User.objects.all().first()
            token_auth, created = Token.objects.get_or_create(user=user)

            manager_parent = ManagerParent(token=token_auth, db_name=school_name, user_id=uid, parent_id=parent_id[0][0],
                                           school_id=company_id)
            manager_parent.save()

            result = {
                'db_name': school_name,
                'user_id': uid,
                'parent_id': parent_id[0][0],
                'token': token_auth.key,
                'school_id': company_id

            }

        return Response(result)
import datetime

# from ..Driver_api.models import *


@api_view(['POST', 'GET'])
def feed_back(request):
    if request.method == 'POST':
        student_id = request.data.get('student_id')
        feed_back = request.data.get('feed_back')
        impression = request.data.get('impression')
        school_name = ManagerParent.pincode('iks')
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


@api_view(['POST', 'GET'])
def settings(request):
    if request.method == 'POST':
        notifications = request.data.get('notifications')

        school_name = ManagerParent.pincode('iks')
        with connections[school_name].cursor() as cursor:
            y = json.dumps(notifications)
            settings = "{\"notifications\":" + y + "}"
            cursor.execute(
                "UPDATE public.school_parent SET settings=%s WHERE id=%s;",
                [settings, 1])
            result = {
                'status': 'ok', }
            return Response(result)
    elif request.method == 'GET':
        school_name = ManagerParent.pincode('iks')
        with connections[school_name].cursor() as cursor:
            cursor.execute("select  settings from school_parent WHERE id = %s", [2])
            columns = (x.name for x in cursor.description)
            data_id_bus = cursor.fetchall()
            if data_id_bus[0][0]:
                data = json.loads(data_id_bus[0][0])
                return Response(data)
            result = {'status': 'Empty'}
            return Response(result)


@api_view(['POST', 'GET'])
def student_served(request):
    if request.method == 'POST':
        round_id = request.data.get('round_id')
        student_id = request.data.get('student_id')
        datetime_c = datetime.datetime.now()
        school_name = ManagerParent.pincode('iks')
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
    elif request.method == 'GET':
        result = {'status': 'error'}
        return Response(result)


@api_view(['POST', 'GET'])
def student_pick_up(request):
    if request.method == 'POST':
        status = request.data.get('status')
        student_id = request.data.get('student_id')
        school_name = ManagerParent.pincode('iks')
        with connections[school_name].cursor() as cursor:
            cursor.execute("select  display_name_search from student_student WHERE id = %s", [student_id])
            columns = (x.name for x in cursor.description)
            student_name = cursor.fetchall()
            cursor.execute(
                "select  id,date,state from pickup_request WHERE name = %s AND parent_id = %s ORDER BY ID DESC LIMIT 1",
                [student_name[0][0], 94])
            columns = (x.name for x in cursor.description)
            date_t = cursor.fetchall()
            if date_t:
                if not (date_t[0][1].strftime('%Y-%m-%d') == datetime.datetime.now().strftime('%Y-%m-%d')):
                    date_string = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    r = datetime.datetime.strptime(date_string, '%Y-%m-%d %H:%M:%S')

                    cursor.execute(
                        "INSERT INTO  pickup_request (date,name,pick_up_by,source,state,parent_id) VALUES (%s,%s,%s,%s,%s,%s); ",
                        [r, student_name[0][0], 'family_member', 'app', 'draft', 1])
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
                    "INSERT INTO  pickup_request (date,name,pick_up_by,source,state,parent_id) VALUES (%s,%s,%s,%s,%s,%s); ",
                    [r, student_name[0][0], 'family_member', 'app', 'draft', 1])

                result = {'result': True}
                return Response(result)


    elif request.method == 'GET':
        # if request.headers:
        #     if request.headers.get('Authorization'):
        #         if 'Bearer' in request.headers.get('Authorization'):
        #             au = request.headers.get('Authorization').replace('Bearer', '').strip()
        #             db_name = Manager.objects.filter(token=au).values_list('db_name')
        #             if db_name:
        #                 for e in db_name:
        #                     school_name = e[0]
        d = datetime.datetime.now().strftime('%Y-%m-%d 00:00:00')
        school_name = ManagerParent.pincode('iks')
        result = {}
        with connections[school_name].cursor() as cursor:
            cursor.execute(
                "select  name,state from pickup_request WHERE parent_id = %s AND date <= %s AND date >= %s",
                [1, datetime.datetime.now(), datetime.datetime.strptime(d, '%Y-%m-%d %H:%M:%S')])
            columns = (x.name for x in cursor.description)
            date_t = cursor.fetchall()
            studen_state = [dict(zip(columns, row)) for row in date_t]
            for rec in range(len(date_t)):
                result[studen_state[rec]['name']] = {'status': studen_state[rec]['state']}
            return Response(result)
        result = {'status': 'error'}
        return Response(result)


@api_view(['POST', 'GET'])
def kids_list(request):
    if request.method == 'POST':
        x = {
            "Badges": {
                "url": "my/Badges/", "arabic_url": "ar_SY/my/Badges",
                "arabic_name": "الشارات",
                "icon": "https://trackware-schools.s3.eu-central-1.amazonaws.com/Badge.png"
            },
            "Weeklyplans":
                {
                    "url": "my/Weekly-plans/",
                    "arabic_url": "ar_SY/my/Weekly-plans",
                    "arabic_name": "الخطط الأسبوعية",
                    "icon": "https://trackware-schools.s3.eu-central-1.amazonaws.com/Weekly+Plans.png"
                },
            "Assignments": {
                "url": "my/Assignments/",
                "arabic_url": "ar_SY/my/Assignments",
                "arabic_name": "الواجبات الالكترونية",
                "icon": "https://trackware-schools.s3.eu-central-1.amazonaws.com/Assignments.png"
            },
            # "Exam": {
            #     "url": "my/exam/",
            #     "arabic_url": "ar_SY/my/exam",
            #     "arabic_name": "امتحانات",
            #     "icon": "https://trackware-schools.s3.eu-central-1.amazonaws.com/Assignments.png"
            # },
            "Events":
                {
                    "url": "my/Events/", "arabic_url": "ar_SY/my/Events", "arabic_name": "الفعاليات و الانشطة",
                    "icon": "https://trackware-schools.s3.eu-central-1.amazonaws.com/Events.png"
                },
            "Homeworks":
                {
                    "url": "my/Homeworks/",
                    "arabic_url": "ar_SY/my/Homeworks",
                    "arabic_name": "الواجبات المنزلية",
                    "icon": "https://trackware-schools.s3.eu-central-1.amazonaws.com/worksheets.png"
                },
            "Calendar":
                {
                    "url": "my/Calendar/",
                    "arabic_url": "ar_SY/my/Calendar",
                    "arabic_name": "التقويم",
                    "icon": "https://trackware-schools.s3.eu-central-1.amazonaws.com/School+Calendar.png"
                },

            "Clinic":
                {
                    "url": "my/Clinic/", "arabic_url": "ar_SY/my/Clinic/", "arabic_name": "العيادة",
                    "icon": "https://trackware-schools.s3.eu-central-1.amazonaws.com/Clinic.png"
                }
        }
        model_list=("Badges","Clinic","Calendar","Homework","Events","Online Assignments","Weekly Plans")
        if request.headers:
            if request.headers.get('Authorization'):
                if 'Bearer' in request.headers.get('Authorization'):

                    au = request.headers.get('Authorization').replace('Bearer', '').strip()
                    db_name = ManagerParent.objects.filter(token=au).values_list('db_name')
                    parent_id=ManagerParent.objects.filter(token=au).values_list('parent_id')
                    school_id=ManagerParent.objects.filter(token=au).values_list('school_id')
                    for e in parent_id:
                        parent_id = e[0]
                    for e in school_id:
                        school_id = e[0]
                    if db_name:
                        for e in db_name:
                            school_name = e[0]



                        school_name = ManagerParent.pincode(school_name)
                        with connections[school_name].cursor() as cursor:
                            cursor.execute("select name from ir_ui_menu where name in %s",[model_list])
                            list = cursor.fetchall()
                            res = []
                            [res.append(x[0]) for x in list if x[0] not in res]
                            model=[]
                            for rec in res:
                                if 'Weekly Plans' == rec:
                                    model.append(x['Weeklyplans'])
                                if 'Events' == rec:
                                    model.append(x['Events'])
                                if 'Online Assignments' == rec:
                                    model.append(x['Assignments'])
                                if 'Homework' == rec:
                                    model.append(x['Homeworks'])
                                if 'Badges' == rec:
                                    model.append(x['Badges'])
                                if 'Calendar' == rec:
                                    model.append(x['Calendar'])
                                if 'Clinic' == rec:
                                    model.append(x['Clinic'])

                            cursor.execute(
                                "select name from ir_ui_menu where name ='Tracking'")
                            tracking = cursor.fetchall()

                            if len(tracking) > 0:
                                model.append( {
                                    "url": "my/Absence/",
                                    "arabic_url": "ar_SY/my/Absence",
                                    "arabic_name": "الغياب",
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
                                            "url": "my/Absence/",
                                            "arabic_url": "ar_SY/my/Absence",
                                            "arabic_name": "الغياب",
                                            "icon": "https://trackware-schools.s3.eu-central-1.amazonaws.com/Absence.png"
                                        }
                                }

                            cursor.execute(
                                "select  id,display_name_search,user_id,pick_up_type,drop_off_type,image_url,grade_name,father_id,mother_id from student_student WHERE father_id = %s OR mother_id = %s OR responsible_id_value = %s  And state = 'done'",
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
                                    'father_id':student[rec][7],
                                    'mother_id': student[rec][8],
                                    'display_name_search': student[rec][1],
                                    'grade_name': student[rec][6],
                                    'drop_off_by_parent': drop,
                                    'pickup_by_parent': pick,
                                    'avatar': student[rec][5] if student[rec][5] else 'https://s3.eu-central-1.amazonaws.com/trackware.schools/public_images/default_student.png' ,
                                    "school_name": school[0][0],
                                    "school_mobile_number": school[0][1],
                                    "school_lat": setting[0][0],
                                    "school_lng": setting[0][1],
                                    'pickup_request_distance':setting[0][2],
                                    "features":model,
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


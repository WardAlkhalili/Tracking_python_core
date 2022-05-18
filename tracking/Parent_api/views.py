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

@api_view(['POST'])
def parent_login(request):
    
    if request.method == 'POST':
        
        password = request.data.get('password')
        user_name = request.data.get('login')
        school_name = request.data.get('school_name')
        url="http://localhost:8888/web/session/authenticate"
         
        body=json.dumps({
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
        uid=response['result']['uid']
        company_id = response['result']['company_id']
        
        with connections[response['result']['db']].cursor() as cursor:
            
            cursor.execute("select id from school_parent WHERE user_id = %s",[response['result']['uid']])    
            columns2 = (x.name for x in cursor.description)        
            parent_id = cursor.fetchall()

            user = User.objects.all().first()
            token_auth, created = Token.objects.get_or_create(user=user)
            manager_parent = ManagerParent(token=token_auth,db_name=school_name,user_id=uid,parent_id=parent_id,school_id=company_id)
            manager_parent.save()
        
            result = {
                'db_name' : school_name,
                'user_id': uid,
                'parent_id':parent_id,
                'token': token_auth.key,
                'school_id' :company_id

            }
    
        return Response(response)
import datetime
# from ..Driver_api.models import *


@api_view(['POST', 'GET'])
def feed_back(request):
    if request.method == 'POST':
        student_id = request.data.get('student_id')
        feed_back = request.data.get('feed_back')
        impression = request.data.get('impression')
        school_name = Manager.pincode('iks')
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

        school_name = Manager.pincode('iks')
        with connections[school_name].cursor() as cursor:
            y = json.dumps(notifications)
            settings = "{\"notifications\":"+y+"}"
            cursor.execute(
                "UPDATE public.school_parent SET settings=%s WHERE id=%s;",
                [settings, 1])
            result = {
                'status': 'ok', }
            return Response(result)
    elif  request.method == 'GET':
        school_name = Manager.pincode('iks')
        with connections[school_name].cursor() as cursor:
            cursor.execute("select  settings from school_parent WHERE id = %s", [2])
            columns = (x.name for x in cursor.description)
            data_id_bus = cursor.fetchall()
            if data_id_bus[0][0]:
                data=json.loads(data_id_bus[0][0])
                return Response(data)
            result = {'status':'Empty'}
            return Response(result)


@api_view(['POST', 'GET'])
def student_served(request):
    if request.method == 'POST':
        round_id = request.data.get('round_id')
        student_id = request.data.get('student_id')
        datetime_c = datetime.datetime.now()
        school_name = Manager.pincode('iks')
        with connections[school_name].cursor() as cursor:
            cursor.execute("select  activity_type from student_history WHERE round_id = %s AND student_id = %s AND datetime = %s ", [round_id,student_id,datetime_c])
            columns = (x.name for x in cursor.description)
            student_served = cursor.fetchall()
            if student_served:
                if student_served[0][0]=="out-school" or student_served[0][0]=="out":
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
            school_name = Manager.pincode('iks')
            with connections[school_name].cursor() as cursor:
                cursor.execute("select  display_name_search from student_student WHERE id = %s", [student_id])
                columns = (x.name for x in cursor.description)
                student_name = cursor.fetchall()
                cursor.execute("select  id,date,state from pickup_request WHERE name = %s AND parent_id = %s ORDER BY ID DESC LIMIT 1", [student_name[0][0],94])
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
                        if date_t[0][2]== 'waiting':
                            cursor.execute(
                                "UPDATE public.pickup_request SET state=%s WHERE id=%s;",
                                ['done', date_t[0][0]])
                            result = {'result': True}
                            return Response(result)
                        elif date_t[0][2]== 'draft':
                            result = {'status': 'error'}
                            return Response(result)
                        elif date_t[0][2]== 'done':
                            result = {'status': 'error'}
                            return Response(result)
                else:
                    q="INSERT INTO  pickup_request (name,pick_up_by, parent_id,date,source,state) VALUES (%s, %s,%s, %s,%s); ",[student_name[0][0],'family_member', '1', datetime.datetime.now(), 'app', 'draft']

                    date_string=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    r=datetime.datetime.strptime(date_string, '%Y-%m-%d %H:%M:%S')

                    cursor.execute( "INSERT INTO  pickup_request (date,name,pick_up_by,source,state,parent_id) VALUES (%s,%s,%s,%s,%s,%s); ",
                        [r,student_name[0][0],'family_member','app','draft',1])

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
            d=datetime.datetime.now().strftime('%Y-%m-%d 00:00:00')
            school_name = Manager.pincode('iks')
            result={}
            with connections[school_name].cursor() as cursor:
                cursor.execute(
                    "select  name,state from pickup_request WHERE parent_id = %s AND date <= %s AND date >= %s",
                    [1,datetime.datetime.now() ,datetime.datetime.strptime(d, '%Y-%m-%d %H:%M:%S')])
                columns = (x.name for x in cursor.description)
                date_t = cursor.fetchall()
                studen_state = [dict(zip(columns, row)) for row in date_t]
                for rec in range(len(date_t)):
                    result[studen_state[rec]['name']] = {'status': studen_state[rec]['state']}
                return Response(result)
            result = {'status': 'error'}
            return Response(result)